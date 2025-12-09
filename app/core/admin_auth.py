"""
Admin authentication for internal API endpoints.

Provides simple bearer token authentication for admin operations.
Uses timing-safe comparison to prevent timing attacks (SEC-001).

SEC-009: Enhanced with role-based authorization to ensure admin routes
are only accessible by users with admin or owner roles.
"""

import logging
import secrets
from typing import Optional
from fastapi import Header, HTTPException, Depends

from app.core.config import settings
from app.core.security import LicenseInfo, get_current_license
from app.core.rbac import Role, get_rbac_service, UserRole

logger = logging.getLogger(__name__)


async def get_admin_key(x_admin_key: str = Header(...)) -> str:
    """
    Validate admin API key from X-Admin-Key header.

    Uses secrets.compare_digest for timing-safe comparison to prevent
    timing attacks that could leak key information.

    Args:
        x_admin_key: Admin API key from header

    Returns:
        Validated admin key

    Raises:
        HTTPException 401: Missing or invalid admin key
    """
    if not x_admin_key:
        logger.warning("Admin API access attempted without key")
        raise HTTPException(
            status_code=401,
            detail="Admin API key required"
        )

    # SEC-001 FIX: Use timing-safe comparison to prevent timing attacks
    # This ensures the comparison takes constant time regardless of
    # how many characters match, preventing information leakage
    expected_key = settings.ADMIN_API_KEY or ""
    provided_key = x_admin_key

    if not secrets.compare_digest(provided_key.encode('utf-8'), expected_key.encode('utf-8')):
        # Don't log partial key to prevent log-based information disclosure
        logger.warning("Invalid admin API key attempted")
        raise HTTPException(
            status_code=401,
            detail="Invalid admin API key"
        )

    return x_admin_key


async def verify_admin_role(
    license: LicenseInfo = Depends(get_current_license),
) -> UserRole:
    """
    SEC-009: Verify that the authenticated user has admin or owner role.

    This dependency should be used on all admin routes to ensure proper
    role-based access control beyond just API key validation.

    Args:
        license: License information from authentication

    Returns:
        UserRole object for the authenticated admin user

    Raises:
        HTTPException 403: If user does not have admin or owner role
        HTTPException 403: If user has no role assigned for the tenant
    """
    rbac = get_rbac_service()

    # Get user's role for their tenant
    user_role = await rbac.get_user_role(
        user_id=license.license_uuid,
        tenant_id=license.tenant_id,
    )

    if not user_role:
        logger.warning(
            f"SEC-009: Admin route access denied - no role found for user "
            f"{license.license_uuid} in tenant {license.tenant_id}"
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied: No role assigned to this tenant",
        )

    # Check if user has admin or owner role
    if user_role.role not in [Role.ADMIN, Role.OWNER]:
        logger.warning(
            f"SEC-009: Admin route access denied - user {license.license_uuid} "
            f"has role '{user_role.role.value}' (requires admin or owner)"
        )
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Admin or owner role required. Your role: {user_role.role.value}",
        )

    logger.info(
        f"SEC-009: Admin route access granted for user {license.license_uuid} "
        f"with role '{user_role.role.value}'"
    )

    return user_role


async def get_admin_user(
    _admin_key: str = Depends(get_admin_key),
    user_role: UserRole = Depends(verify_admin_role),
) -> UserRole:
    """
    SEC-009: Combined dependency for admin route authorization.

    Validates both:
    1. Admin API key (X-Admin-Key header)
    2. User has admin or owner role in their tenant

    This is the recommended dependency for all admin routes.

    Usage:
        @router.get("/admin/endpoint")
        async def admin_endpoint(
            admin_user: UserRole = Depends(get_admin_user)
        ):
            # Access admin_user.tenant_id, admin_user.role, etc.
            pass

    Args:
        _admin_key: Admin API key validation (auto-injected)
        user_role: User role verification (auto-injected)

    Returns:
        UserRole object for the authenticated admin user

    Raises:
        HTTPException 401: Missing or invalid admin key
        HTTPException 403: User does not have admin or owner role
    """
    return user_role
