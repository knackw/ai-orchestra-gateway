"""
Role-Based Access Control (RBAC) Service.

Provides role management and permission checking for multi-tenant access control.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Depends

from app.core.database import get_supabase_client
from app.core.security import LicenseInfo, get_current_license

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles with hierarchical permissions."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Available permissions in the system."""
    # Wildcard
    ALL = "*"

    # User management
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_ALL = "users:*"

    # App management
    APPS_READ = "apps:read"
    APPS_CREATE = "apps:create"
    APPS_UPDATE = "apps:update"
    APPS_DELETE = "apps:delete"
    APPS_ALL = "apps:*"

    # Settings management
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"
    SETTINGS_ALL = "settings:*"

    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_ALL = "analytics:*"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_UPDATE = "billing:update"
    BILLING_ALL = "billing:*"

    # Tenant management
    TENANT_READ = "tenant:read"
    TENANT_UPDATE = "tenant:update"
    TENANT_DELETE = "tenant:delete"
    TENANT_ALL = "tenant:*"


# Role hierarchy - higher roles inherit lower role permissions
ROLE_HIERARCHY = {
    Role.OWNER: [Role.ADMIN, Role.MEMBER, Role.VIEWER],
    Role.ADMIN: [Role.MEMBER, Role.VIEWER],
    Role.MEMBER: [Role.VIEWER],
    Role.VIEWER: [],
}

# Default permissions per role
ROLE_PERMISSIONS = {
    Role.OWNER: [Permission.ALL],
    Role.ADMIN: [
        Permission.USERS_ALL,
        Permission.APPS_ALL,
        Permission.SETTINGS_ALL,
        Permission.ANALYTICS_READ,
        Permission.BILLING_READ,
        Permission.TENANT_READ,
        Permission.TENANT_UPDATE,
    ],
    Role.MEMBER: [
        Permission.APPS_CREATE,
        Permission.APPS_READ,
        Permission.APPS_UPDATE,
        Permission.ANALYTICS_READ,
    ],
    Role.VIEWER: [
        Permission.APPS_READ,
        Permission.ANALYTICS_READ,
    ],
}


@dataclass
class UserRole:
    """User role information for a tenant."""
    user_id: str
    tenant_id: str
    role: Role
    granted_by: str | None = None
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool = True


class RBACService:
    """
    Role-Based Access Control service.

    Provides methods for:
    - Checking user permissions
    - Assigning/revoking roles
    - Getting user roles
    """

    def __init__(self):
        """Initialize RBAC service."""
        self._client = None

    def _get_client(self):
        """Get Supabase client (lazy loading)."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def get_user_role(
        self,
        user_id: str,
        tenant_id: str,
    ) -> UserRole | None:
        """
        Get user's role for a specific tenant.

        Args:
            user_id: User UUID
            tenant_id: Tenant UUID

        Returns:
            UserRole if found, None otherwise
        """
        try:
            client = self._get_client()

            response = (
                client.table("user_roles")
                .select("*")
                .eq("user_id", user_id)
                .eq("tenant_id", tenant_id)
                .eq("is_active", True)
                .single()
                .execute()
            )

            if not response.data:
                return None

            data = response.data

            # Check expiration
            if data.get("expires_at"):
                expires_at = datetime.fromisoformat(
                    data["expires_at"].replace("Z", "+00:00")
                )
                if expires_at < datetime.now(expires_at.tzinfo):
                    logger.debug(f"Role expired for user {user_id} in tenant {tenant_id}")
                    return None

            return UserRole(
                user_id=data["user_id"],
                tenant_id=data["tenant_id"],
                role=Role(data["role"]),
                granted_by=data.get("granted_by"),
                granted_at=(
                    datetime.fromisoformat(data["granted_at"].replace("Z", "+00:00"))
                    if data.get("granted_at") else None
                ),
                expires_at=(
                    datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
                    if data.get("expires_at") else None
                ),
                is_active=data.get("is_active", True),
            )

        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return None

    async def assign_role(
        self,
        user_id: str,
        tenant_id: str,
        role: Role,
        granted_by: str | None = None,
        expires_at: datetime | None = None,
    ) -> bool:
        """
        Assign a role to a user for a tenant.

        Args:
            user_id: User UUID
            tenant_id: Tenant UUID
            role: Role to assign
            granted_by: User who granted the role
            expires_at: Optional expiration time

        Returns:
            True if successful
        """
        try:
            client = self._get_client()

            data = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role": role.value,
                "granted_by": granted_by,
                "is_active": True,
            }

            if expires_at:
                data["expires_at"] = expires_at.isoformat()

            # Upsert role
            response = (
                client.table("user_roles")
                .upsert(data, on_conflict="user_id,tenant_id")
                .execute()
            )

            logger.info(
                f"Assigned role '{role.value}' to user {user_id} "
                f"for tenant {tenant_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            return False

    async def revoke_role(
        self,
        user_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Revoke a user's role for a tenant.

        Args:
            user_id: User UUID
            tenant_id: Tenant UUID

        Returns:
            True if successful
        """
        try:
            client = self._get_client()

            response = (
                client.table("user_roles")
                .update({"is_active": False})
                .eq("user_id", user_id)
                .eq("tenant_id", tenant_id)
                .execute()
            )

            logger.info(f"Revoked role for user {user_id} in tenant {tenant_id}")
            return True

        except Exception as e:
            logger.error(f"Error revoking role: {e}")
            return False

    async def get_tenant_users(
        self,
        tenant_id: str,
    ) -> list[UserRole]:
        """
        Get all users with roles for a tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            List of UserRole objects
        """
        try:
            client = self._get_client()

            response = (
                client.table("user_roles")
                .select("*")
                .eq("tenant_id", tenant_id)
                .eq("is_active", True)
                .execute()
            )

            users = []
            for data in response.data or []:
                # Check expiration
                if data.get("expires_at"):
                    expires_at = datetime.fromisoformat(
                        data["expires_at"].replace("Z", "+00:00")
                    )
                    if expires_at < datetime.now(expires_at.tzinfo):
                        continue

                users.append(UserRole(
                    user_id=data["user_id"],
                    tenant_id=data["tenant_id"],
                    role=Role(data["role"]),
                    granted_by=data.get("granted_by"),
                    granted_at=(
                        datetime.fromisoformat(data["granted_at"].replace("Z", "+00:00"))
                        if data.get("granted_at") else None
                    ),
                    expires_at=(
                        datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
                        if data.get("expires_at") else None
                    ),
                    is_active=data.get("is_active", True),
                ))

            return users

        except Exception as e:
            logger.error(f"Error getting tenant users: {e}")
            return []

    def has_permission(
        self,
        role: Role,
        permission: Permission,
    ) -> bool:
        """
        Check if a role has a specific permission.

        Args:
            role: User's role
            permission: Permission to check

        Returns:
            True if role has permission
        """
        # Get direct permissions for role
        permissions = ROLE_PERMISSIONS.get(role, [])

        # Check for wildcard
        if Permission.ALL in permissions:
            return True

        # Check direct permission
        if permission in permissions:
            return True

        # Check category wildcard (e.g., "apps:*" for "apps:delete")
        permission_str = permission.value
        if ":" in permission_str:
            category = permission_str.split(":")[0]
            wildcard = Permission(f"{category}:*")
            if wildcard in permissions:
                return True

        return False

    def has_any_permission(
        self,
        role: Role,
        permissions: list[Permission],
    ) -> bool:
        """
        Check if a role has any of the specified permissions.

        Args:
            role: User's role
            permissions: List of permissions to check

        Returns:
            True if role has any permission
        """
        return any(self.has_permission(role, p) for p in permissions)

    def has_all_permissions(
        self,
        role: Role,
        permissions: list[Permission],
    ) -> bool:
        """
        Check if a role has all specified permissions.

        Args:
            role: User's role
            permissions: List of permissions to check

        Returns:
            True if role has all permissions
        """
        return all(self.has_permission(role, p) for p in permissions)

    def get_role_permissions(self, role: Role) -> list[Permission]:
        """
        Get all permissions for a role.

        Args:
            role: Role to get permissions for

        Returns:
            List of permissions
        """
        return ROLE_PERMISSIONS.get(role, [])

    @staticmethod
    def is_role_higher_or_equal(role1: Role, role2: Role) -> bool:
        """
        Check if role1 is higher or equal to role2 in hierarchy.

        Args:
            role1: First role
            role2: Second role

        Returns:
            True if role1 >= role2
        """
        if role1 == role2:
            return True

        return role2 in ROLE_HIERARCHY.get(role1, [])


# Global RBAC service instance
_rbac_service: RBACService | None = None


def get_rbac_service() -> RBACService:
    """Get the global RBAC service instance."""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


# FastAPI Dependencies

class RequirePermission:
    """
    FastAPI dependency for requiring specific permission(s).

    Usage:
        @app.delete("/tenants/{tenant_id}")
        async def delete_tenant(
            tenant_id: str,
            license: LicenseInfo = Depends(get_current_license),
            _: None = Depends(RequirePermission(Permission.TENANT_DELETE)),
        ):
            pass
    """

    def __init__(
        self,
        *permissions: Permission,
        require_all: bool = False,
    ):
        """
        Initialize permission requirement.

        Args:
            permissions: Required permission(s)
            require_all: If True, user must have ALL permissions.
                        If False, user must have ANY permission.
        """
        self.permissions = list(permissions)
        self.require_all = require_all

    async def __call__(
        self,
        license: LicenseInfo = Depends(get_current_license),
    ) -> None:
        """
        Check if current user has required permission(s).

        Raises:
            HTTPException(403): If user lacks required permission(s)
        """
        rbac = get_rbac_service()

        # Get user's role for tenant
        user_role = await rbac.get_user_role(
            user_id=license.license_uuid,  # Using license UUID as user ID
            tenant_id=license.tenant_id,
        )

        if not user_role:
            logger.warning(
                f"RBAC: No role found for user {license.license_uuid} "
                f"in tenant {license.tenant_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this tenant",
            )

        # Check permissions
        if self.require_all:
            has_access = rbac.has_all_permissions(user_role.role, self.permissions)
        else:
            has_access = rbac.has_any_permission(user_role.role, self.permissions)

        if not has_access:
            permission_names = [p.value for p in self.permissions]
            logger.warning(
                f"RBAC: User {license.license_uuid} with role {user_role.role.value} "
                f"denied access. Required: {permission_names}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {', '.join(permission_names)}",
            )

        logger.debug(
            f"RBAC: User {license.license_uuid} with role {user_role.role.value} "
            f"granted access to {[p.value for p in self.permissions]}"
        )


class RequireRole:
    """
    FastAPI dependency for requiring a minimum role level.

    Usage:
        @app.delete("/tenants/{tenant_id}")
        async def delete_tenant(
            tenant_id: str,
            license: LicenseInfo = Depends(get_current_license),
            _: None = Depends(RequireRole(Role.OWNER)),
        ):
            pass
    """

    def __init__(self, minimum_role: Role):
        """
        Initialize role requirement.

        Args:
            minimum_role: Minimum required role
        """
        self.minimum_role = minimum_role

    async def __call__(
        self,
        license: LicenseInfo = Depends(get_current_license),
    ) -> UserRole:
        """
        Check if current user has required role level.

        Returns:
            UserRole object for the authenticated user

        Raises:
            HTTPException(403): If user's role is below minimum
        """
        rbac = get_rbac_service()

        # Get user's role for tenant
        user_role = await rbac.get_user_role(
            user_id=license.license_uuid,
            tenant_id=license.tenant_id,
        )

        if not user_role:
            logger.warning(
                f"RBAC: No role found for user {license.license_uuid} "
                f"in tenant {license.tenant_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this tenant",
            )

        # Check role hierarchy
        if not RBACService.is_role_higher_or_equal(user_role.role, self.minimum_role):
            logger.warning(
                f"RBAC: User {license.license_uuid} with role {user_role.role.value} "
                f"denied access. Required minimum: {self.minimum_role.value}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient role. Required: {self.minimum_role.value} or higher",
            )

        logger.debug(
            f"RBAC: User {license.license_uuid} with role {user_role.role.value} "
            f"granted access (minimum: {self.minimum_role.value})"
        )

        return user_role


async def get_current_user_role(
    license: LicenseInfo = Depends(get_current_license),
) -> UserRole | None:
    """
    FastAPI dependency to get current user's role.

    Returns None if user has no role assigned (useful for optional role checks).
    """
    rbac = get_rbac_service()
    return await rbac.get_user_role(
        user_id=license.license_uuid,
        tenant_id=license.tenant_id,
    )
