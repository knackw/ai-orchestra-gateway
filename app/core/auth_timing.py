"""
SEC-018: Email Enumeration Protection via Constant-Time Responses.

Prevents timing attacks that could reveal if an email/license key exists in the system
by ensuring all authentication responses take a consistent amount of time.

Usage:
    @app.post("/api/v1/auth/login")
    @constant_time_response(min_time_ms=500)
    async def login(...):
        ...
"""

import asyncio
import logging
import random
import time
from functools import wraps
from typing import Callable, Optional

from fastapi import Response

logger = logging.getLogger(__name__)


def constant_time_response(
    min_time_ms: int = 500,
    max_jitter_ms: int = 100,
    apply_to_errors: bool = True
):
    """
    Decorator that ensures endpoint responses take a constant minimum time.

    This prevents timing attacks where attackers measure response times to
    determine if emails/usernames exist in the system.

    Args:
        min_time_ms: Minimum response time in milliseconds (default: 500ms)
        max_jitter_ms: Maximum random jitter in milliseconds (default: 100ms)
                      Adds randomness to mask timing patterns
        apply_to_errors: Whether to apply timing to error responses (default: True)

    Security Notes:
        - Use on login, signup, password reset, and any endpoint that validates
          user existence
        - Combine with generic error messages that don't reveal user existence
        - Consider rate limiting to prevent brute force attacks

    Example:
        @app.post("/auth/login")
        @constant_time_response(min_time_ms=500, max_jitter_ms=100)
        async def login(email: str, password: str):
            # Validation logic here
            return {"token": "..."}
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            # Add random jitter at the start to mask patterns
            jitter = random.uniform(0, max_jitter_ms / 1000)
            await asyncio.sleep(jitter)

            # Execute the actual function
            exception_occurred = None
            result = None

            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            except Exception as e:
                exception_occurred = e
                if not apply_to_errors:
                    raise

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            min_time_sec = min_time_ms / 1000

            # Sleep for remaining time to reach minimum
            remaining_time = max(0, min_time_sec - elapsed_time)
            if remaining_time > 0:
                await asyncio.sleep(remaining_time)

            # Log timing for security monitoring (without exposing sensitive data)
            total_time = time.time() - start_time
            logger.debug(
                f"SEC-018: Response completed in {total_time*1000:.2f}ms "
                f"(min: {min_time_ms}ms, jitter: {jitter*1000:.2f}ms)"
            )

            # Re-raise exception if one occurred
            if exception_occurred:
                raise exception_occurred

            return result

        return wrapper
    return decorator


async def constant_time_compare(a: str, b: str, min_time_ms: int = 50) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.

    This is useful for comparing secrets, tokens, or credentials where
    the comparison time should not leak information about the values.

    Args:
        a: First string to compare
        b: Second string to compare
        min_time_ms: Minimum comparison time in milliseconds (default: 50ms)

    Returns:
        True if strings are equal, False otherwise

    Security Note:
        This function adds a minimum delay but the actual comparison is done
        using Python's secrets.compare_digest which is timing-safe at the
        byte level.
    """
    import secrets

    start_time = time.time()

    # Use secrets.compare_digest for constant-time comparison at byte level
    result = secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))

    # Ensure minimum time regardless of result
    elapsed_time = time.time() - start_time
    min_time_sec = min_time_ms / 1000
    remaining_time = max(0, min_time_sec - elapsed_time)

    if remaining_time > 0:
        await asyncio.sleep(remaining_time)

    return result


def generic_auth_error(
    detail: str = "Invalid credentials",
    status_code: int = 401
) -> dict:
    """
    Return a generic authentication error that doesn't leak information.

    Args:
        detail: Generic error message (default: "Invalid credentials")
        status_code: HTTP status code (default: 401)

    Returns:
        Dictionary with error details

    Security Note:
        NEVER return specific errors like:
        - "Email not found"
        - "User does not exist"
        - "Incorrect password"

        Instead use:
        - "Invalid credentials"
        - "Authentication failed"
        - "Invalid email or password"
    """
    return {
        "detail": detail,
        "status_code": status_code,
        "error_type": "authentication_error"
    }


def mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
    """
    Mask a sensitive value for logging purposes.

    Args:
        value: The sensitive value to mask
        visible_chars: Number of characters to show at the end (default: 4)

    Returns:
        Masked string (e.g., "****@example.com" or "****1234")

    Example:
        >>> mask_sensitive_value("user@example.com", 11)
        '****example.com'
        >>> mask_sensitive_value("license-key-12345", 5)
        '****12345'
    """
    if len(value) <= visible_chars:
        return "*" * len(value)

    return "*" * 4 + value[-visible_chars:]


class TimingAttackProtection:
    """
    Context manager for protecting code blocks against timing attacks.

    Usage:
        async with TimingAttackProtection(min_time_ms=500):
            user = await validate_credentials(email, password)
            if not user:
                raise HTTPException(401, "Invalid credentials")
    """

    def __init__(
        self,
        min_time_ms: int = 500,
        max_jitter_ms: int = 100
    ):
        self.min_time_ms = min_time_ms
        self.max_jitter_ms = max_jitter_ms
        self.start_time: Optional[float] = None

    async def __aenter__(self):
        """Start timing protection."""
        self.start_time = time.time()

        # Add initial random jitter
        jitter = random.uniform(0, self.max_jitter_ms / 1000)
        await asyncio.sleep(jitter)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure minimum time has elapsed."""
        if self.start_time is None:
            return False

        elapsed_time = time.time() - self.start_time
        min_time_sec = self.min_time_ms / 1000
        remaining_time = max(0, min_time_sec - elapsed_time)

        if remaining_time > 0:
            await asyncio.sleep(remaining_time)

        # Don't suppress exceptions
        return False


# Predefined timing configurations for common use cases
LOGIN_TIMING = {"min_time_ms": 500, "max_jitter_ms": 100}
SIGNUP_TIMING = {"min_time_ms": 600, "max_jitter_ms": 150}
PASSWORD_RESET_TIMING = {"min_time_ms": 500, "max_jitter_ms": 100}
LICENSE_VALIDATION_TIMING = {"min_time_ms": 300, "max_jitter_ms": 50}
