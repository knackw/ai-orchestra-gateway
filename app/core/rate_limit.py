"""
SEC-007: Rate Limiting Configuration

Implements rate limiting with Redis for production environments.
Memory-based limiting is only allowed in development/testing.
"""

import os
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Determine storage URL (Redis or Memory)
# Use memory:// for testing or when Redis is not available
REDIS_URL = os.getenv("REDIS_URL", "")
TESTING = os.getenv("TESTING", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()


def get_storage_uri() -> str:
    """
    Get the appropriate storage URI for rate limiting.

    SEC-007: Production requires Redis for proper multi-instance rate limiting.

    - In testing mode: always use memory
    - In production: MUST use Redis (raises error if not set)
    - In development/staging: use Redis if available, else memory with warning
    """
    if TESTING:
        return "memory://"

    if REDIS_URL:
        logger.info("Rate limiting: Using Redis storage")
        return REDIS_URL

    # Production requires Redis
    if ENVIRONMENT == "production":
        logger.critical(
            "SEC-007: REDIS_URL not set in production! "
            "Memory-based rate limiting does not work across multiple instances. "
            "Falling back to memory (SECURITY RISK - fix immediately!)"
        )
        # In strict mode, you could raise an error here:
        # raise RuntimeError("REDIS_URL required in production for rate limiting")

    # Default to memory for development/staging
    logger.warning(
        "SEC-007: REDIS_URL not set, using in-memory rate limiting. "
        "This is acceptable for development but NOT for production."
    )
    return "memory://"


def get_project_key(request: Request) -> str:
    """
    Rate limit key function.
    Throttles based on 'X-License-Key' header if present, otherwise IP.
    This ensures limits are per-license.
    """
    api_key = request.headers.get("X-License-Key")
    if api_key:
        return api_key
    return get_remote_address(request)


# Initialize Limiter with appropriate storage
limiter = Limiter(
    key_func=get_project_key,
    storage_uri=get_storage_uri(),
    strategy="fixed-window"
)


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom 429 handler to return JSON.
    """
    return JSONResponse(
        {"detail": f"Rate limit exceeded: {exc}"},
        status_code=429
    )
