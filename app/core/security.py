"""
Security and authentication utilities.

Provides FastAPI dependencies for API key validation.

SEC-013: Supports hashed license keys with backwards compatibility.
SEC-018: Email enumeration protection via constant-time responses.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Header, HTTPException

from app.core.database import get_supabase_client
from app.core.license_hash import (
    hash_license_key,
    verify_license_key,
    is_hashed_key,
    mask_license_key,
)
from app.core.auth_timing import (
    TimingAttackProtection,
    LICENSE_VALIDATION_TIMING,
)
from supabase import Client

logger = logging.getLogger(__name__)


class LicenseInfo:
    """License information for authenticated requests."""

    def __init__(
        self,
        license_key: str,
        license_uuid: str,  # UUID
        tenant_id: str,
        app_id: str,
        credits_remaining: int,
        is_active: bool,
        expires_at: Optional[datetime] = None,
    ):
        self.license_key = license_key
        self.license_uuid = license_uuid
        self.tenant_id = tenant_id
        self.app_id = app_id
        self.credits_remaining = credits_remaining
        self.is_active = is_active
        self.expires_at = expires_at


async def validate_license_key(license_key: str) -> LicenseInfo:
    """
    Validate license key against Supabase licenses table.

    SEC-013: Supports both hashed and plaintext license keys for backwards
    compatibility during migration. Checks plaintext first, then hash.

    SEC-018: Uses constant-time response protection to prevent timing attacks
    that could reveal whether a license key exists in the system.

    Args:
        license_key: License key to validate

    Returns:
        LicenseInfo object with license details

    Raises:
        HTTPException(403): If license is invalid, inactive, or expired
        HTTPException(500): If database error occurs
    """
    # SEC-018: Apply timing attack protection
    async with TimingAttackProtection(**LICENSE_VALIDATION_TIMING):
        try:
            client: Client = get_supabase_client()

            # SEC-013: Try plaintext lookup first (legacy support)
            response = (
                client.table("licenses")
                .select("*")
                .eq("license_key", license_key)
                .maybe_single()
                .execute()
            )

            # SEC-013: If not found, try hashed lookup
            if not response.data:
                hashed_key = hash_license_key(license_key)
                response = (
                    client.table("licenses")
                    .select("*")
                    .eq("license_key", hashed_key)
                    .maybe_single()
                    .execute()
                )

            # Check if license exists
            # SEC-018: Use generic error message to prevent enumeration
            if not response.data:
                logger.warning(f"AUTH_FAILURE: Invalid license key attempt: {mask_license_key(license_key)}")
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or expired license key",
                )

            license_data = response.data

            # Check if active
            if not license_data.get("is_active", False):
                logger.warning(
                    f"AUTH_FAILURE: Inactive license key used: {mask_license_key(license_key)}"
                )
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or expired license key",
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
                        f"AUTH_FAILURE: Expired license key used: {mask_license_key(license_key)}"
                    )
                    raise HTTPException(
                        status_code=403,
                        detail="Invalid or expired license key",
                    )

            # Check credits (optional - can be enforced in billing)
            credits_remaining = license_data.get("credits_remaining", 0)
            if credits_remaining <= 0:
                logger.warning(
                    f"AUTH_FAILURE: No credits remaining for license: {mask_license_key(license_key)}"
                )
                raise HTTPException(
                    status_code=402,
                    detail="No credits remaining. Please purchase more credits.",
                )

            # Create and return LicenseInfo
            license_info = LicenseInfo(
                license_key=license_key,
                license_uuid=license_data["id"],  # UUID
                tenant_id=license_data["tenant_id"],
                app_id=license_data.get("app_id"),
                credits_remaining=credits_remaining,
                is_active=license_data["is_active"],
                expires_at=expires_dt if expires_at else None,
            )

            logger.info(
                f"Valid license: {mask_license_key(license_key)} "
                f"(id: {license_info.license_uuid}, "
                f"tenant: {license_info.tenant_id}, "
                f"app: {license_info.app_id}, "
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


async def get_current_license_with_ip_check(
    request: "Request",
    x_license_key: Optional[str] = Header(None, alias="X-License-Key")
) -> LicenseInfo:
    """
    FastAPI dependency for validating license keys WITH IP whitelisting.
    
    This extends get_current_license by also checking the client IP
    against the tenant's allowed_ips list.
    
    Usage:
        from fastapi import Request, Depends
        
        @app.post("/protected")
        async def protected_route(
            request: Request,
            license: LicenseInfo = Depends(get_current_license_with_ip_check)
        ):
            pass
    """
    from fastapi import Request
    from app.core.ip_whitelist import validate_ip_whitelist
    
    # First validate the license
    license_info = await get_current_license(x_license_key)
    
    # Then check IP whitelist
    try:
        client: Client = get_supabase_client()
        
        # Get tenant's allowed_ips
        tenant_response = (
            client.table("tenants")
            .select("allowed_ips")
            .eq("id", license_info.tenant_id)
            .single()
            .execute()
        )
        
        if tenant_response.data:
            allowed_ips = tenant_response.data.get("allowed_ips")
            
            if not validate_ip_whitelist(request, allowed_ips):
                logger.warning(
                    f"AUTH_FAILURE: IP not in whitelist for tenant {license_info.tenant_id}"
                )
                raise HTTPException(
                    status_code=403,
                    detail="Your IP address is not authorized for this tenant.",
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking IP whitelist: {e}")
        # Don't block on IP check errors - fail open for backwards compatibility
        pass
    
    return license_info


# Type hint import for Request (avoid circular import)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fastapi import Request

