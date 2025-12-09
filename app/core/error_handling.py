"""
SEC-010: API Error Message Sanitization

Ensures that stack traces and internal error details are not exposed
to end users in production environment.
"""

import logging
import traceback
from typing import Any

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

# Error messages that are safe to expose
SAFE_ERROR_MESSAGES = {
    400: "Bad Request",
    401: "Unauthorized",
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
EXPOSE_DETAIL_STATUS_CODES = {400, 401, 403, 404, 409, 422, 429}


def sanitize_error_message(
    status_code: int,
    detail: Any,
    is_development: bool = False
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
        return str(detail) if detail else SAFE_ERROR_MESSAGES.get(status_code, "Unknown Error")

    # In production, only expose safe client error messages
    if status_code in EXPOSE_DETAIL_STATUS_CODES:
        # Ensure detail doesn't contain stack traces or internal info
        detail_str = str(detail) if detail else ""

        # Block patterns that might leak internal info
        blocked_patterns = [
            "Traceback",
            "File \"",
            "line ",
            "at 0x",
            "postgres",
            "supabase",
            "password",
            "secret",
            "key=",
            "token=",
        ]

        if any(pattern.lower() in detail_str.lower() for pattern in blocked_patterns):
            return SAFE_ERROR_MESSAGES.get(status_code, "Error")

        # Limit message length
        if len(detail_str) > 200:
            detail_str = detail_str[:200] + "..."

        return detail_str if detail_str else SAFE_ERROR_MESSAGES.get(status_code, "Error")

    # For 5xx errors, always return generic message
    return SAFE_ERROR_MESSAGES.get(status_code, "Internal Server Error")


async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """
    Custom HTTP exception handler that sanitizes error messages.
    """
    sanitized_detail = sanitize_error_message(
        exc.status_code,
        exc.detail,
        settings.is_development
    )

    # Log full error details internally
    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": sanitized_detail},
        headers=getattr(exc, "headers", None),
    )


async def starlette_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle Starlette HTTP exceptions with sanitization.
    """
    sanitized_detail = sanitize_error_message(
        exc.status_code,
        exc.detail,
        settings.is_development
    )

    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": sanitized_detail},
        headers=getattr(exc, "headers", None),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unhandled exceptions with sanitization.

    CRITICAL: Never expose stack traces in production.
    """
    # Log full error with stack trace internally
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        exc_info=True
    )

    if settings.is_development:
        # In development, show full error details
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
                "traceback": traceback.format_exc() if settings.is_development else None,
            },
        )

    # In production, show generic message
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
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
