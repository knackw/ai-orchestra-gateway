"""
SEC-017: Request Timeout Middleware

Implements request timeout to prevent slow requests from consuming resources.
Protects against slowloris attacks and resource exhaustion.
"""

import asyncio
import logging
from typing import Callable

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)

# Default timeout in seconds
DEFAULT_TIMEOUT = 30

# Longer timeout for AI generation endpoints
AI_ENDPOINT_TIMEOUT = 120

# Paths with custom timeout settings
TIMEOUT_CONFIG = {
    "/api/v1/generate": AI_ENDPOINT_TIMEOUT,
    "/api/v1/webhooks/stripe": 60,  # Stripe webhooks need processing time
    "/health": 5,
    "/metrics": 5,
}


def get_timeout_for_path(path: str) -> int:
    """
    Get the appropriate timeout for a given path.

    Args:
        path: The request path

    Returns:
        Timeout in seconds
    """
    # Check exact matches first
    if path in TIMEOUT_CONFIG:
        return TIMEOUT_CONFIG[path]

    # Check prefix matches
    for prefix, timeout in TIMEOUT_CONFIG.items():
        if path.startswith(prefix):
            return timeout

    return DEFAULT_TIMEOUT


class TimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces request timeouts.

    Returns 504 Gateway Timeout if request processing exceeds the limit.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        timeout = get_timeout_for_path(request.url.path)

        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )
            return response

        except asyncio.TimeoutError:
            logger.warning(
                f"Request timeout ({timeout}s) for {request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=504,
                content={
                    "detail": "Request timeout. Please try again with a simpler request.",
                    "timeout_seconds": timeout,
                }
            )


# For httpx client timeouts
def get_httpx_timeout(service: str = "default") -> float:
    """
    Get timeout configuration for httpx clients.

    Args:
        service: The service name (anthropic, scaleway, supabase, etc.)

    Returns:
        Timeout in seconds for httpx
    """
    timeouts = {
        "anthropic": 120.0,
        "scaleway": 120.0,
        "openai": 120.0,
        "supabase": 30.0,
        "stripe": 30.0,
        "default": 30.0,
    }
    return timeouts.get(service, timeouts["default"])


# For frontend API calls (used in documentation)
FRONTEND_TIMEOUT_CONFIG = {
    "default": 10000,  # 10 seconds in milliseconds
    "ai_generation": 120000,  # 2 minutes for AI generation
    "file_upload": 60000,  # 1 minute for file uploads
}
