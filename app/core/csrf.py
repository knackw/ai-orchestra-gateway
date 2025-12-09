"""
SEC-002: CSRF Protection Middleware

Implements CSRF token validation for state-changing requests.
Uses double-submit cookie pattern for stateless CSRF protection.
"""

import secrets
import logging
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# CSRF Configuration
CSRF_TOKEN_LENGTH = 32
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_MAX_AGE = 3600 * 24  # 24 hours
CSRF_COOKIE_SECURE = True  # Set to False for local development without HTTPS
CSRF_COOKIE_HTTPONLY = False  # Must be readable by JavaScript
CSRF_COOKIE_SAMESITE = "strict"

# Methods that require CSRF protection
CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Paths exempt from CSRF (webhooks, API endpoints with Bearer auth)
CSRF_EXEMPT_PATHS = {
    "/api/v1/webhooks/stripe",
    "/api/v1/generate",
    "/api/v1/auth/logout",  # SEC-019: Auth endpoints use Bearer tokens
    "/api/v1/auth/logout-all",  # SEC-019: Auth endpoints use Bearer tokens
    "/health",
    "/metrics",
}


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


def get_csrf_token_from_cookie(request: Request) -> Optional[str]:
    """Extract CSRF token from cookie."""
    return request.cookies.get(CSRF_COOKIE_NAME)


def get_csrf_token_from_header(request: Request) -> Optional[str]:
    """Extract CSRF token from header."""
    return request.headers.get(CSRF_HEADER_NAME)


def is_csrf_exempt(request: Request) -> bool:
    """Check if request path is exempt from CSRF protection."""
    path = request.url.path

    # Exempt specific paths
    if path in CSRF_EXEMPT_PATHS:
        return True

    # Exempt paths that start with exempt prefixes
    for exempt_path in CSRF_EXEMPT_PATHS:
        if path.startswith(exempt_path):
            return True

    # Exempt requests with Bearer token (API authentication)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return True

    # Exempt requests with X-License-Key (API authentication)
    if request.headers.get("X-License-Key"):
        return True

    return False


def validate_csrf_token(cookie_token: Optional[str], header_token: Optional[str]) -> bool:
    """
    Validate CSRF token using double-submit cookie pattern.

    Both tokens must be present and match using constant-time comparison.
    """
    if not cookie_token or not header_token:
        return False

    return secrets.compare_digest(cookie_token, header_token)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware using double-submit cookie pattern.

    For GET requests: Sets a CSRF token in a cookie
    For POST/PUT/PATCH/DELETE: Validates the CSRF token from header matches cookie
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method.upper()

        # For safe methods, just set/refresh the CSRF cookie
        if method not in CSRF_PROTECTED_METHODS:
            response = await call_next(request)

            # Set CSRF cookie if not present
            if not get_csrf_token_from_cookie(request):
                csrf_token = generate_csrf_token()
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=csrf_token,
                    max_age=CSRF_COOKIE_MAX_AGE,
                    secure=CSRF_COOKIE_SECURE,
                    httponly=CSRF_COOKIE_HTTPONLY,
                    samesite=CSRF_COOKIE_SAMESITE,
                )

            return response

        # For state-changing methods, validate CSRF token
        if not is_csrf_exempt(request):
            cookie_token = get_csrf_token_from_cookie(request)
            header_token = get_csrf_token_from_header(request)

            if not validate_csrf_token(cookie_token, header_token):
                logger.warning(
                    f"CSRF validation failed for {method} {request.url.path} "
                    f"from {request.client.host if request.client else 'unknown'}"
                )
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token validation failed"
                )

        response = await call_next(request)
        return response


def get_csrf_token_endpoint(request: Request) -> dict:
    """
    Endpoint to get a fresh CSRF token.

    Usage: GET /api/v1/csrf-token
    Response: {"csrf_token": "..."}
    """
    token = get_csrf_token_from_cookie(request) or generate_csrf_token()
    return {"csrf_token": token}
