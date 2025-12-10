"""
SEC-021: Request ID and Distributed Tracing Middleware

Provides:
1. Unique Request ID generation for every request
2. Support for incoming trace IDs from upstream services
3. Correlation ID propagation for distributed tracing
4. Context variable storage for logging access
5. Trace information in response headers
"""

import logging
import time
import uuid
from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Context variables for request tracking
request_id_context: ContextVar[str] = ContextVar("request_id", default="")
trace_id_context: ContextVar[str] = ContextVar("trace_id", default="")
span_id_context: ContextVar[str] = ContextVar("span_id", default="")
parent_span_id_context: ContextVar[Optional[str]] = ContextVar(
    "parent_span_id", default=None
)

logger = logging.getLogger(__name__)


def generate_trace_id() -> str:
    """Generate a new trace ID (32 hex characters)."""
    return uuid.uuid4().hex


def generate_span_id() -> str:
    """Generate a new span ID (16 hex characters)."""
    return uuid.uuid4().hex[:16]


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware for Request ID and Distributed Tracing.

    Features:
    1. Generates a unique Request ID for every request
    2. Supports incoming trace IDs from upstream services (X-Trace-ID, traceparent)
    3. Generates span IDs for this service's handling
    4. Sets IDs in ContextVars for logging access
    5. Adds trace headers to responses

    Supported incoming headers:
    - X-Request-ID: Simple request ID
    - X-Trace-ID: Trace ID from upstream
    - X-Span-ID: Parent span ID from upstream
    - traceparent: W3C Trace Context format (00-<trace-id>-<span-id>-<flags>)

    Response headers added:
    - X-Request-ID: Request ID (same as trace ID for simplicity)
    - X-Trace-ID: Trace ID for correlation
    - X-Span-ID: This service's span ID
    - X-Response-Time: Request processing time in ms
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        # Extract or generate trace ID
        trace_id = self._extract_trace_id(request)
        if not trace_id:
            trace_id = generate_trace_id()

        # Extract parent span ID if provided
        parent_span_id = self._extract_parent_span_id(request)

        # Generate span ID for this service's handling
        span_id = generate_span_id()

        # Use trace ID as request ID for simplicity
        request_id = trace_id

        # Set context variables
        request_id_token = request_id_context.set(request_id)
        trace_id_token = trace_id_context.set(trace_id)
        span_id_token = span_id_context.set(span_id)
        parent_span_token = parent_span_id_context.set(parent_span_id)

        # Set in request state for access in handlers
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        request.state.span_id = span_id
        request.state.parent_span_id = parent_span_id

        try:
            response = await call_next(request)

            # Calculate response time
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Add tracing headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Span-ID"] = span_id
            response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"

            # Log request completion with trace context
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} "
                f"({elapsed_ms:.2f}ms) [trace_id={trace_id}, span_id={span_id}]"
            )

            return response
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} - ERROR ({elapsed_ms:.2f}ms) "
                f"[trace_id={trace_id}, span_id={span_id}]: {e}"
            )
            raise
        finally:
            # Clean up context variables
            request_id_context.reset(request_id_token)
            trace_id_context.reset(trace_id_token)
            span_id_context.reset(span_id_token)
            parent_span_id_context.reset(parent_span_token)

    def _extract_trace_id(self, request: Request) -> Optional[str]:
        """Extract trace ID from request headers."""
        # Check X-Trace-ID header
        trace_id = request.headers.get("X-Trace-ID")
        if trace_id and self._is_valid_trace_id(trace_id):
            return trace_id

        # Check X-Request-ID header (use as trace ID)
        request_id = request.headers.get("X-Request-ID")
        if request_id and self._is_valid_trace_id(request_id):
            return request_id

        # Check W3C traceparent header
        traceparent = request.headers.get("traceparent")
        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 2 and self._is_valid_trace_id(parts[1]):
                return parts[1]

        return None

    def _extract_parent_span_id(self, request: Request) -> Optional[str]:
        """Extract parent span ID from request headers."""
        # Check X-Span-ID header
        span_id = request.headers.get("X-Span-ID")
        if span_id and self._is_valid_span_id(span_id):
            return span_id

        # Check W3C traceparent header
        traceparent = request.headers.get("traceparent")
        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 3 and self._is_valid_span_id(parts[2]):
                return parts[2]

        return None

    def _is_valid_trace_id(self, trace_id: str) -> bool:
        """Validate trace ID format (32 hex characters or UUID)."""
        if not trace_id:
            return False
        # Allow both 32 hex chars and UUID format
        clean_id = trace_id.replace("-", "")
        if len(clean_id) != 32:
            return False
        try:
            int(clean_id, 16)
            return True
        except ValueError:
            return False

    def _is_valid_span_id(self, span_id: str) -> bool:
        """Validate span ID format (16 hex characters)."""
        if not span_id:
            return False
        if len(span_id) != 16:
            return False
        try:
            int(span_id, 16)
            return True
        except ValueError:
            return False


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_context.get()


def get_trace_id() -> str:
    """Get current trace ID from context."""
    return trace_id_context.get()


def get_span_id() -> str:
    """Get current span ID from context."""
    return span_id_context.get()


def get_parent_span_id() -> Optional[str]:
    """Get parent span ID from context (if any)."""
    return parent_span_id_context.get()


def get_trace_headers() -> dict:
    """
    Get headers for propagating trace context to downstream services.

    Returns dict with:
    - X-Trace-ID
    - X-Span-ID (current span becomes parent for downstream)
    - traceparent (W3C format)
    """
    trace_id = get_trace_id()
    span_id = get_span_id()

    headers = {}
    if trace_id:
        headers["X-Trace-ID"] = trace_id
    if span_id:
        headers["X-Span-ID"] = span_id
    if trace_id and span_id:
        # W3C Trace Context format: version-trace_id-span_id-flags
        headers["traceparent"] = f"00-{trace_id}-{span_id}-01"

    return headers


# Export all trace functions
__all__ = [
    "RequestIDMiddleware",
    "get_request_id",
    "get_trace_id",
    "get_span_id",
    "get_parent_span_id",
    "get_trace_headers",
]
