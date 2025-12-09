"""
SEC-015: Whitelist-based CORS Configuration

Implements strict CORS policy with:
- Whitelist of allowed origins
- Environment-based configuration
- No wildcards in production
- Proper credentials handling
"""

from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def get_allowed_origins() -> List[str]:
    """
    Get list of allowed CORS origins based on environment.

    Development: Defaults to localhost origins
    Production: Requires explicit CORS_ORIGINS environment variable

    Returns:
        List of allowed origin URLs
    """
    # Production: ONLY use explicitly configured origins
    if settings.is_production:
        if not settings.CORS_ORIGINS:
            # No origins allowed in production by default (secure by default)
            return []
        return settings.CORS_ORIGINS

    # Development: Allow localhost by default, plus any configured origins
    default_dev_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    if settings.CORS_ORIGINS:
        # Merge defaults with configured origins, remove duplicates
        return list(set(default_dev_origins + settings.CORS_ORIGINS))

    return default_dev_origins


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.

    Security features:
    - Strict origin whitelist (no wildcards in production)
    - Configurable credentials support
    - Configurable preflight cache time
    - Only allows specific HTTP methods
    - Only allows safe headers by default

    Args:
        app: FastAPI application instance
    """
    allowed_origins = get_allowed_origins()

    # Log CORS configuration (without sensitive data)
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"CORS configured with {len(allowed_origins)} allowed origins")
    if settings.is_development:
        logger.info(f"Development mode: allowed origins = {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Strict whitelist
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "OPTIONS",
        ],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Type",
            "Content-Language",
            "Authorization",
            "X-Request-ID",
            "X-CSRF-Token",
            "X-License-Key",
        ],
        max_age=settings.CORS_MAX_AGE,
    )


def validate_cors_configuration() -> None:
    """
    Validate CORS configuration at startup.

    Raises:
        ValueError: If CORS configuration is invalid
    """
    # Production must have explicit origins or be empty (no CORS)
    if settings.is_production and not settings.CORS_ORIGINS:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "Production mode: No CORS origins configured. "
            "CORS will block all cross-origin requests. "
            "Set CORS_ORIGINS environment variable to allow specific origins."
        )

    # Check for wildcard in production (security risk)
    if settings.is_production and settings.CORS_ORIGINS:
        if "*" in settings.CORS_ORIGINS:
            raise ValueError(
                "Security Error: Wildcard (*) in CORS origins is not allowed in production. "
                "Please specify explicit origins."
            )

    # Validate origin format
    for origin in settings.CORS_ORIGINS:
        if not origin.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid CORS origin: {origin}. "
                f"Origins must start with http:// or https://"
            )
