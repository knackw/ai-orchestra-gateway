"""
SEC-010: API Error Message Sanitization with RFC 7807 Problem Details

Implements RFC 7807 (Problem Details for HTTP APIs) for standardized
error responses. Ensures that stack traces and internal error details
are not exposed to end users in production environment.

RFC 7807 Format:
{
    "type": "https://api.example.com/errors/insufficient-credits",
    "title": "Insufficient Credits",
    "status": 402,
    "detail": "Your account has 0 credits remaining. Please add credits to continue.",
    "instance": "/api/v1/generate",
    "trace_id": "abc123"
}
"""

import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

# Base URL for error type URIs
ERROR_TYPE_BASE = "https://api.ai-orchestra.de/errors"


class ProblemDetail(BaseModel):
    """
    RFC 7807 Problem Details response model.

    This standardized error format provides:
    - type: URI reference to error documentation
    - title: Short human-readable summary
    - status: HTTP status code
    - detail: Human-readable explanation specific to this occurrence
    - instance: URI reference to the specific occurrence
    - trace_id: Correlation ID for distributed tracing (extension)
    - timestamp: ISO 8601 timestamp (extension)
    """

    type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "type": "https://api.ai-orchestra.de/errors/insufficient-credits",
                "title": "Insufficient Credits",
                "status": 402,
                "detail": "Your account has 0 credits remaining.",
                "instance": "/api/v1/generate",
                "trace_id": "req-abc123",
                "timestamp": "2025-12-09T12:00:00Z",
            }
        }


# Error type mappings for common errors
ERROR_TYPES = {
    400: ("bad-request", "Bad Request"),
    401: ("unauthorized", "Unauthorized"),
    402: ("payment-required", "Payment Required"),
    403: ("forbidden", "Forbidden"),
    404: ("not-found", "Not Found"),
    405: ("method-not-allowed", "Method Not Allowed"),
    409: ("conflict", "Conflict"),
    422: ("validation-error", "Validation Error"),
    429: ("rate-limit-exceeded", "Rate Limit Exceeded"),
    500: ("internal-error", "Internal Server Error"),
    502: ("bad-gateway", "Bad Gateway"),
    503: ("service-unavailable", "Service Unavailable"),
    504: ("gateway-timeout", "Gateway Timeout"),
}

# Specific error types for domain-specific errors
DOMAIN_ERROR_TYPES = {
    "insufficient_credits": ("insufficient-credits", "Insufficient Credits"),
    "license_inactive": ("license-inactive", "License Inactive"),
    "license_expired": ("license-expired", "License Expired"),
    "pii_detected": ("pii-detected", "PII Detected"),
    "provider_unavailable": ("provider-unavailable", "AI Provider Unavailable"),
    "csrf_invalid": ("csrf-invalid", "CSRF Token Invalid"),
    "session_expired": ("session-expired", "Session Expired"),
}

# Error messages that are safe to expose
SAFE_ERROR_MESSAGES = {
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

# Status codes where original message can be shown (client errors with context)
EXPOSE_DETAIL_STATUS_CODES = {400, 401, 402, 403, 404, 409, 422, 429}


def get_error_type(status_code: int, error_code: Optional[str] = None) -> tuple:
    """
    Get error type slug and title for RFC 7807 response.

    Args:
        status_code: HTTP status code
        error_code: Optional domain-specific error code

    Returns:
        Tuple of (type_slug, title)
    """
    if error_code and error_code in DOMAIN_ERROR_TYPES:
        return DOMAIN_ERROR_TYPES[error_code]
    return ERROR_TYPES.get(status_code, ("unknown-error", "Unknown Error"))


def create_problem_detail(
    status_code: int,
    detail: Optional[str] = None,
    error_code: Optional[str] = None,
    request: Optional[Request] = None,
    trace_id: Optional[str] = None,
) -> ProblemDetail:
    """
    Create RFC 7807 Problem Detail response.

    Args:
        status_code: HTTP status code
        detail: Human-readable explanation
        error_code: Optional domain-specific error code
        request: FastAPI request object for instance URI
        trace_id: Correlation ID for tracing

    Returns:
        ProblemDetail model
    """
    type_slug, title = get_error_type(status_code, error_code)

    return ProblemDetail(
        type=f"{ERROR_TYPE_BASE}/{type_slug}",
        title=title,
        status=status_code,
        detail=detail,
        instance=str(request.url.path) if request else None,
        trace_id=trace_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def sanitize_error_message(
    status_code: int, detail: Any, is_development: bool = False
) -> str:
    """
    Sanitize error messages for production.

    In production:
    - Client errors (4xx) may show controlled details
    - Server errors (5xx) show generic messages

    In development:
    - All error details are shown
    """
    if is_development:
        return (
            str(detail)
            if detail
            else SAFE_ERROR_MESSAGES.get(status_code, "Unknown Error")
        )

    # In production, only expose safe client error messages
    if status_code in EXPOSE_DETAIL_STATUS_CODES:
        # Ensure detail doesn't contain stack traces or internal info
        detail_str = str(detail) if detail else ""

        # Block patterns that might leak internal info
        blocked_patterns = [
            "Traceback",
            'File "',
            "line ",
            "at 0x",
            "postgres",
            "supabase",
            "password",
            "secret",
            "key=",
            "token=",
            "api_key",
            "authorization",
        ]

        if any(pattern.lower() in detail_str.lower() for pattern in blocked_patterns):
            return SAFE_ERROR_MESSAGES.get(status_code, "Error")

        # Limit message length
        if len(detail_str) > 200:
            detail_str = detail_str[:200] + "..."

        return detail_str if detail_str else SAFE_ERROR_MESSAGES.get(status_code, "Error")

    # For 5xx errors, always return generic message
    return SAFE_ERROR_MESSAGES.get(status_code, "Internal Server Error")


def get_trace_id(request: Request) -> str:
    """
    Get or create trace ID for request.

    Checks for existing trace ID in headers (from distributed tracing),
    or generates a new one.
    """
    # Check for existing trace ID from middleware or upstream
    trace_id = request.headers.get("X-Request-ID")
    if not trace_id:
        trace_id = request.headers.get("X-Trace-ID")
    if not trace_id:
        # Check if set by our RequestIDMiddleware
        trace_id = getattr(request.state, "request_id", None)
    if not trace_id:
        trace_id = f"req-{uuid4().hex[:12]}"
    return trace_id


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom HTTP exception handler with RFC 7807 Problem Details.
    """
    trace_id = get_trace_id(request)

    # Extract error code if provided in detail dict
    error_code = None
    original_detail = exc.detail
    if isinstance(exc.detail, dict):
        error_code = exc.detail.get("error_code")
        original_detail = exc.detail.get("message", str(exc.detail))

    sanitized_detail = sanitize_error_message(
        exc.status_code, original_detail, settings.is_development
    )

    # Log full error details internally
    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}: "
        f"{original_detail} [trace_id={trace_id}]"
    )

    # Create RFC 7807 Problem Detail response
    problem = create_problem_detail(
        status_code=exc.status_code,
        detail=sanitized_detail,
        error_code=error_code,
        request=request,
        trace_id=trace_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
        headers={
            **(getattr(exc, "headers", None) or {}),
            "Content-Type": "application/problem+json",
            "X-Request-ID": trace_id,
        },
    )


async def starlette_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle Starlette HTTP exceptions with RFC 7807 Problem Details.
    """
    trace_id = get_trace_id(request)

    sanitized_detail = sanitize_error_message(
        exc.status_code, exc.detail, settings.is_development
    )

    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}: "
        f"{exc.detail} [trace_id={trace_id}]"
    )

    problem = create_problem_detail(
        status_code=exc.status_code,
        detail=sanitized_detail,
        request=request,
        trace_id=trace_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
        headers={
            **(getattr(exc, "headers", None) or {}),
            "Content-Type": "application/problem+json",
            "X-Request-ID": trace_id,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unhandled exceptions with RFC 7807 Problem Details.

    CRITICAL: Never expose stack traces in production.
    """
    trace_id = get_trace_id(request)

    # Log full error with stack trace internally
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc} "
        f"[trace_id={trace_id}]",
        exc_info=True,
    )

    if settings.is_development:
        # In development, show full error details
        problem = ProblemDetail(
            type=f"{ERROR_TYPE_BASE}/internal-error",
            title="Internal Server Error",
            status=500,
            detail=str(exc),
            instance=str(request.url.path),
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        content = problem.model_dump(exclude_none=True)
        content["exception_type"] = type(exc).__name__
        content["traceback"] = traceback.format_exc()

        return JSONResponse(
            status_code=500,
            content=content,
            headers={
                "Content-Type": "application/problem+json",
                "X-Request-ID": trace_id,
            },
        )

    # In production, show generic message
    problem = create_problem_detail(
        status_code=500,
        detail="An unexpected error occurred. Please try again later.",
        request=request,
        trace_id=trace_id,
    )

    return JSONResponse(
        status_code=500,
        content=problem.model_dump(exclude_none=True),
        headers={
            "Content-Type": "application/problem+json",
            "X-Request-ID": trace_id,
        },
    )


def register_error_handlers(app):
    """
    Register custom error handlers on the FastAPI app.

    Usage:
        from app.core.error_handling import register_error_handlers
        register_error_handlers(app)
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


# Export ProblemDetail for use in endpoints
__all__ = [
    "ProblemDetail",
    "create_problem_detail",
    "sanitize_error_message",
    "register_error_handlers",
    "DOMAIN_ERROR_TYPES",
]
