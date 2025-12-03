"""
Security and authentication utilities.

Provides FastAPI dependencies for API key validation.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Header, HTTPException

from app.core.database import get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)


class LicenseInfo:
    """License information for authenticated requests."""

    def __init__(
        self,
        license_key: str,
        tenant_id: str,
        credits_remaining: int,
        is_active: bool,
        expires_at: Optional[datetime] = None,
    ):
        self.license_key = license_key
        self.tenant_id = tenant_id
        self.credits_remaining = credits_remaining
        self.is_active = is_active
        self.expires_at = expires_at


async def validate_license_key(license_key: str) -> LicenseInfo:
    """
    Validate license key against Supabase licenses table.

    Args:
        license_key: License key to validate

    Returns:
        LicenseInfo object with license details

    Raises:
        HTTPException(403): If license is invalid, inactive, or expired
        HTTPException(500): If database error occurs
    """
    try:
        client: Client = get_supabase_client()

        # Query licenses table
        response = (
            client.table("licenses")
            .select("*")
            .eq("license_key", license_key)
            .single()
            .execute()
        )

        # Check if license exists
        if not response.data:
            logger.warning(f"Invalid license key attempt: {license_key[:10]}...")
            raise HTTPException(
                status_code=403,
                detail="Invalid license key",
            )

        license_data = response.data

        # Check if active
        if not license_data.get("is_active", False):
            logger.warning(
                f"Inactive license key used: {license_key[:10]}..."
            )
            raise HTTPException(
                status_code=403,
                detail="License is not active",
            )

        # Check expiration
        expires_at = license_data.get("expires_at")
        if expires_at:
            # Parse expiration date
            expires_dt = datetime.fromisoformat(
                expires_at.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)

            if expires_dt < now:
                logger.warning(
                    f"Expired license key used: {license_key[:10]}..."
                )
                raise HTTPException(
                    status_code=403,
                    detail="License has expired",
                )

        # Check credits (optional - can be enforced in billing)
        credits_remaining = license_data.get("credits_remaining", 0)
        if credits_remaining <= 0:
            logger.warning(
                f"No credits remaining for license: {license_key[:10]}..."
            )
            raise HTTPException(
                status_code=402,
                detail="No credits remaining. Please purchase more credits.",
            )

        # Create and return LicenseInfo
        license_info = LicenseInfo(
            license_key=license_key,
            tenant_id=license_data["tenant_id"],
            credits_remaining=credits_remaining,
            is_active=license_data["is_active"],
            expires_at=expires_dt if expires_at else None,
        )

        logger.info(
            f"Valid license: {license_key[:10]}... "
            f"(tenant: {license_info.tenant_id}, "
            f"credits: {credits_remaining})"
        )

        return license_info

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error validating license key: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication error. Please try again later.",
        ) from e


async def get_current_license(
    x_license_key: Optional[str] = Header(None, alias="X-License-Key")
) -> LicenseInfo:
    """
    FastAPI dependency for validating license keys.

    Extracts X-License-Key header and validates it against Supabase.

    Args:
        x_license_key: License key from X-License-Key header

    Returns:
        LicenseInfo object with validated license details

    Raises:
        HTTPException(401): If X-License-Key header is missing
        HTTPException(403): If license key is invalid/inactive/expired
        HTTPException(402): If no credits remaining
        HTTPException(500): If database error occurs

    Usage:
        @app.post("/protected")
        async def protected_route(
            license: LicenseInfo = Depends(get_current_license)
        ):
            # Access license.tenant_id, license.credits_remaining, etc.
            pass
    """
    if not x_license_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-License-Key header",
        )

    if not x_license_key.strip():
        raise HTTPException(
            status_code=401,
            detail="Empty X-License-Key header",
        )

    return await validate_license_key(x_license_key)
