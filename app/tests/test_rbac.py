"""
Unit tests for Role-Based Access Control (RBAC) Service.

Tests:
- Role hierarchy and permissions
- Permission checking
- Role assignment/revocation
- FastAPI dependencies
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone

from app.core.rbac import (
    Role,
    Permission,
    UserRole,
    RBACService,
    ROLE_PERMISSIONS,
    ROLE_HIERARCHY,
    RequirePermission,
    RequireRole,
    get_rbac_service,
)
from app.core.security import LicenseInfo
from fastapi import HTTPException


class TestRoleHierarchy:
    """Tests for role hierarchy."""

    def test_owner_is_highest(self):
        """Owner should be higher than all other roles."""
        assert RBACService.is_role_higher_or_equal(Role.OWNER, Role.ADMIN)
        assert RBACService.is_role_higher_or_equal(Role.OWNER, Role.MEMBER)
        assert RBACService.is_role_higher_or_equal(Role.OWNER, Role.VIEWER)

    def test_admin_is_higher_than_member(self):
        """Admin should be higher than member and viewer."""
        assert RBACService.is_role_higher_or_equal(Role.ADMIN, Role.MEMBER)
        assert RBACService.is_role_higher_or_equal(Role.ADMIN, Role.VIEWER)
        assert not RBACService.is_role_higher_or_equal(Role.ADMIN, Role.OWNER)

    def test_member_is_higher_than_viewer(self):
        """Member should be higher than viewer."""
        assert RBACService.is_role_higher_or_equal(Role.MEMBER, Role.VIEWER)
        assert not RBACService.is_role_higher_or_equal(Role.MEMBER, Role.ADMIN)
        assert not RBACService.is_role_higher_or_equal(Role.MEMBER, Role.OWNER)

    def test_viewer_is_lowest(self):
        """Viewer should be lower than all other roles."""
        assert not RBACService.is_role_higher_or_equal(Role.VIEWER, Role.OWNER)
        assert not RBACService.is_role_higher_or_equal(Role.VIEWER, Role.ADMIN)
        assert not RBACService.is_role_higher_or_equal(Role.VIEWER, Role.MEMBER)

    def test_same_role_is_equal(self):
        """Same role should be equal to itself."""
        for role in Role:
            assert RBACService.is_role_higher_or_equal(role, role)


class TestPermissions:
    """Tests for permission checking."""

    @pytest.fixture
    def rbac(self):
        """Create RBAC service instance."""
        return RBACService()

    def test_owner_has_all_permissions(self, rbac):
        """Owner should have all permissions."""
        for permission in Permission:
            assert rbac.has_permission(Role.OWNER, permission)

    def test_admin_permissions(self, rbac):
        """Admin should have user, app, settings, and read permissions."""
        # Should have
        assert rbac.has_permission(Role.ADMIN, Permission.USERS_READ)
        assert rbac.has_permission(Role.ADMIN, Permission.USERS_CREATE)
        assert rbac.has_permission(Role.ADMIN, Permission.USERS_DELETE)
        assert rbac.has_permission(Role.ADMIN, Permission.APPS_ALL)
        assert rbac.has_permission(Role.ADMIN, Permission.SETTINGS_ALL)
        assert rbac.has_permission(Role.ADMIN, Permission.ANALYTICS_READ)

        # Should NOT have
        assert not rbac.has_permission(Role.ADMIN, Permission.TENANT_DELETE)
        assert not rbac.has_permission(Role.ADMIN, Permission.BILLING_UPDATE)

    def test_member_permissions(self, rbac):
        """Member should have app create/read/update and analytics read."""
        # Should have
        assert rbac.has_permission(Role.MEMBER, Permission.APPS_CREATE)
        assert rbac.has_permission(Role.MEMBER, Permission.APPS_READ)
        assert rbac.has_permission(Role.MEMBER, Permission.APPS_UPDATE)
        assert rbac.has_permission(Role.MEMBER, Permission.ANALYTICS_READ)

        # Should NOT have
        assert not rbac.has_permission(Role.MEMBER, Permission.APPS_DELETE)
        assert not rbac.has_permission(Role.MEMBER, Permission.USERS_READ)
        assert not rbac.has_permission(Role.MEMBER, Permission.SETTINGS_READ)

    def test_viewer_permissions(self, rbac):
        """Viewer should only have read permissions."""
        # Should have
        assert rbac.has_permission(Role.VIEWER, Permission.APPS_READ)
        assert rbac.has_permission(Role.VIEWER, Permission.ANALYTICS_READ)

        # Should NOT have
        assert not rbac.has_permission(Role.VIEWER, Permission.APPS_CREATE)
        assert not rbac.has_permission(Role.VIEWER, Permission.APPS_UPDATE)
        assert not rbac.has_permission(Role.VIEWER, Permission.APPS_DELETE)
        assert not rbac.has_permission(Role.VIEWER, Permission.USERS_READ)

    def test_wildcard_permission_matching(self, rbac):
        """Wildcard permissions should match specific permissions."""
        # Admin has APPS_ALL which should match APPS_DELETE
        assert rbac.has_permission(Role.ADMIN, Permission.APPS_DELETE)
        assert rbac.has_permission(Role.ADMIN, Permission.APPS_CREATE)

    def test_has_any_permission(self, rbac):
        """has_any_permission should return True if any permission matches."""
        # Viewer can read but not delete
        assert rbac.has_any_permission(
            Role.VIEWER,
            [Permission.APPS_DELETE, Permission.APPS_READ],
        )

        # Viewer cannot create or delete
        assert not rbac.has_any_permission(
            Role.VIEWER,
            [Permission.APPS_CREATE, Permission.APPS_DELETE],
        )

    def test_has_all_permissions(self, rbac):
        """has_all_permissions should return True only if all permissions match."""
        # Admin can read and create apps
        assert rbac.has_all_permissions(
            Role.ADMIN,
            [Permission.APPS_READ, Permission.APPS_CREATE],
        )

        # Admin cannot delete tenant
        assert not rbac.has_all_permissions(
            Role.ADMIN,
            [Permission.APPS_READ, Permission.TENANT_DELETE],
        )

    def test_get_role_permissions(self, rbac):
        """Should return all permissions for a role."""
        viewer_perms = rbac.get_role_permissions(Role.VIEWER)
        assert Permission.APPS_READ in viewer_perms
        assert Permission.ANALYTICS_READ in viewer_perms
        assert len(viewer_perms) == 2


class TestRBACService:
    """Tests for RBAC service database operations."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Supabase client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def rbac(self, mock_client):
        """Create RBAC service with mock client."""
        service = RBACService()
        service._client = mock_client
        return service

    @pytest.mark.asyncio
    async def test_get_user_role_found(self, rbac, mock_client):
        """Should return UserRole when found."""
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "user_id": "user-123",
            "tenant_id": "tenant-456",
            "role": "admin",
            "granted_by": "owner-789",
            "granted_at": "2025-01-01T00:00:00+00:00",
            "expires_at": None,
            "is_active": True,
        }

        result = await rbac.get_user_role("user-123", "tenant-456")

        assert result is not None
        assert result.user_id == "user-123"
        assert result.tenant_id == "tenant-456"
        assert result.role == Role.ADMIN

    @pytest.mark.asyncio
    async def test_get_user_role_not_found(self, rbac, mock_client):
        """Should return None when role not found."""
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        result = await rbac.get_user_role("user-123", "tenant-456")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_role_expired(self, rbac, mock_client):
        """Should return None when role is expired."""
        past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "user_id": "user-123",
            "tenant_id": "tenant-456",
            "role": "admin",
            "granted_by": None,
            "granted_at": "2025-01-01T00:00:00+00:00",
            "expires_at": past_time,
            "is_active": True,
        }

        result = await rbac.get_user_role("user-123", "tenant-456")

        assert result is None

    @pytest.mark.asyncio
    async def test_assign_role_success(self, rbac, mock_client):
        """Should successfully assign role."""
        mock_client.table.return_value.upsert.return_value.execute.return_value.data = [
            {"id": "role-id-123"}
        ]

        result = await rbac.assign_role(
            user_id="user-123",
            tenant_id="tenant-456",
            role=Role.MEMBER,
            granted_by="admin-789",
        )

        assert result is True
        mock_client.table.assert_called_with("user_roles")

    @pytest.mark.asyncio
    async def test_assign_role_with_expiration(self, rbac, mock_client):
        """Should assign role with expiration."""
        mock_client.table.return_value.upsert.return_value.execute.return_value.data = [
            {"id": "role-id-123"}
        ]

        expires = datetime.now(timezone.utc) + timedelta(days=30)
        result = await rbac.assign_role(
            user_id="user-123",
            tenant_id="tenant-456",
            role=Role.MEMBER,
            expires_at=expires,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_revoke_role_success(self, rbac, mock_client):
        """Should successfully revoke role."""
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": "role-id-123"}
        ]

        result = await rbac.revoke_role("user-123", "tenant-456")

        assert result is True

    @pytest.mark.asyncio
    async def test_get_tenant_users(self, rbac, mock_client):
        """Should return all active users for tenant."""
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {
                "user_id": "user-1",
                "tenant_id": "tenant-456",
                "role": "admin",
                "granted_by": None,
                "granted_at": "2025-01-01T00:00:00+00:00",
                "expires_at": None,
                "is_active": True,
            },
            {
                "user_id": "user-2",
                "tenant_id": "tenant-456",
                "role": "viewer",
                "granted_by": "user-1",
                "granted_at": "2025-01-02T00:00:00+00:00",
                "expires_at": None,
                "is_active": True,
            },
        ]

        result = await rbac.get_tenant_users("tenant-456")

        assert len(result) == 2
        assert result[0].role == Role.ADMIN
        assert result[1].role == Role.VIEWER

    @pytest.mark.asyncio
    async def test_get_tenant_users_excludes_expired(self, rbac, mock_client):
        """Should exclude expired roles from tenant users."""
        past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {
                "user_id": "user-1",
                "tenant_id": "tenant-456",
                "role": "admin",
                "granted_by": None,
                "granted_at": "2025-01-01T00:00:00+00:00",
                "expires_at": past_time,  # Expired
                "is_active": True,
            },
        ]

        result = await rbac.get_tenant_users("tenant-456")

        assert len(result) == 0


class TestRequirePermissionDependency:
    """Tests for RequirePermission FastAPI dependency."""

    @pytest.fixture
    def license_info(self):
        """Create mock license info."""
        return LicenseInfo(
            license_key="test-key",
            license_uuid="user-123",
            tenant_id="tenant-456",
            app_id="app-789",
            credits_remaining=100,
            is_active=True,
        )

    @pytest.mark.asyncio
    async def test_require_permission_granted(self, license_info):
        """Should pass when user has permission."""
        with patch("app.core.rbac.get_rbac_service") as mock_get_rbac:
            rbac = MagicMock()
            rbac.get_user_role = AsyncMock(return_value=UserRole(
                user_id="user-123",
                tenant_id="tenant-456",
                role=Role.ADMIN,
            ))
            rbac.has_any_permission = MagicMock(return_value=True)
            mock_get_rbac.return_value = rbac

            dependency = RequirePermission(Permission.APPS_READ)
            # Should not raise
            await dependency(license_info)

    @pytest.mark.asyncio
    async def test_require_permission_denied(self, license_info):
        """Should raise 403 when user lacks permission."""
        with patch("app.core.rbac.get_rbac_service") as mock_get_rbac:
            rbac = MagicMock()
            rbac.get_user_role = AsyncMock(return_value=UserRole(
                user_id="user-123",
                tenant_id="tenant-456",
                role=Role.VIEWER,
            ))
            rbac.has_any_permission = MagicMock(return_value=False)
            mock_get_rbac.return_value = rbac

            dependency = RequirePermission(Permission.TENANT_DELETE)

            with pytest.raises(HTTPException) as exc_info:
                await dependency(license_info)

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_permission_no_role(self, license_info):
        """Should raise 403 when user has no role."""
        with patch("app.core.rbac.get_rbac_service") as mock_get_rbac:
            rbac = MagicMock()
            rbac.get_user_role = AsyncMock(return_value=None)
            mock_get_rbac.return_value = rbac

            dependency = RequirePermission(Permission.APPS_READ)

            with pytest.raises(HTTPException) as exc_info:
                await dependency(license_info)

            assert exc_info.value.status_code == 403
            assert "do not have access" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_all_permissions(self, license_info):
        """Should check all permissions when require_all=True."""
        with patch("app.core.rbac.get_rbac_service") as mock_get_rbac:
            rbac = MagicMock()
            rbac.get_user_role = AsyncMock(return_value=UserRole(
                user_id="user-123",
                tenant_id="tenant-456",
                role=Role.ADMIN,
            ))
            rbac.has_all_permissions = MagicMock(return_value=True)
            mock_get_rbac.return_value = rbac

            dependency = RequirePermission(
                Permission.APPS_READ,
                Permission.APPS_CREATE,
                require_all=True,
            )

            await dependency(license_info)
            rbac.has_all_permissions.assert_called_once()


class TestRequireRoleDependency:
    """Tests for RequireRole FastAPI dependency."""

    @pytest.fixture
    def license_info(self):
        """Create mock license info."""
        return LicenseInfo(
            license_key="test-key",
            license_uuid="user-123",
            tenant_id="tenant-456",
            app_id="app-789",
            credits_remaining=100,
            is_active=True,
        )

    @pytest.mark.asyncio
    async def test_require_role_granted(self, license_info):
        """Should pass when user has sufficient role."""
        with patch("app.core.rbac.get_rbac_service") as mock_get_rbac:
            rbac = MagicMock()
            user_role = UserRole(
                user_id="user-123",
                tenant_id="tenant-456",
                role=Role.ADMIN,
            )
            rbac.get_user_role = AsyncMock(return_value=user_role)
            mock_get_rbac.return_value = rbac

            dependency = RequireRole(Role.MEMBER)  # Admin >= Member
            result = await dependency(license_info)

            assert result == user_role

    @pytest.mark.asyncio
    async def test_require_role_denied(self, license_info):
        """Should raise 403 when user has insufficient role."""
        with patch("app.core.rbac.get_rbac_service") as mock_get_rbac:
            rbac = MagicMock()
            rbac.get_user_role = AsyncMock(return_value=UserRole(
                user_id="user-123",
                tenant_id="tenant-456",
                role=Role.VIEWER,
            ))
            mock_get_rbac.return_value = rbac

            dependency = RequireRole(Role.ADMIN)

            with pytest.raises(HTTPException) as exc_info:
                await dependency(license_info)

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_owner_role(self, license_info):
        """Owner-only operations should reject non-owners."""
        with patch("app.core.rbac.get_rbac_service") as mock_get_rbac:
            rbac = MagicMock()
            rbac.get_user_role = AsyncMock(return_value=UserRole(
                user_id="user-123",
                tenant_id="tenant-456",
                role=Role.ADMIN,
            ))
            mock_get_rbac.return_value = rbac

            dependency = RequireRole(Role.OWNER)

            with pytest.raises(HTTPException) as exc_info:
                await dependency(license_info)

            assert exc_info.value.status_code == 403
            assert "owner" in str(exc_info.value.detail).lower()


class TestUserRole:
    """Tests for UserRole dataclass."""

    def test_create_user_role(self):
        """Should create UserRole with all fields."""
        now = datetime.now(timezone.utc)
        role = UserRole(
            user_id="user-123",
            tenant_id="tenant-456",
            role=Role.ADMIN,
            granted_by="owner-789",
            granted_at=now,
            expires_at=now + timedelta(days=30),
            is_active=True,
        )

        assert role.user_id == "user-123"
        assert role.tenant_id == "tenant-456"
        assert role.role == Role.ADMIN
        assert role.granted_by == "owner-789"
        assert role.is_active is True

    def test_user_role_defaults(self):
        """Should use defaults for optional fields."""
        role = UserRole(
            user_id="user-123",
            tenant_id="tenant-456",
            role=Role.VIEWER,
        )

        assert role.granted_by is None
        assert role.granted_at is None
        assert role.expires_at is None
        assert role.is_active is True


class TestRoleEnum:
    """Tests for Role enum."""

    def test_role_values(self):
        """Role values should match expected strings."""
        assert Role.OWNER.value == "owner"
        assert Role.ADMIN.value == "admin"
        assert Role.MEMBER.value == "member"
        assert Role.VIEWER.value == "viewer"

    def test_role_from_string(self):
        """Should create Role from string value."""
        assert Role("owner") == Role.OWNER
        assert Role("admin") == Role.ADMIN


class TestPermissionEnum:
    """Tests for Permission enum."""

    def test_permission_categories(self):
        """Permissions should be categorized correctly."""
        # User permissions
        assert Permission.USERS_READ.value.startswith("users:")
        assert Permission.USERS_CREATE.value.startswith("users:")

        # App permissions
        assert Permission.APPS_READ.value.startswith("apps:")
        assert Permission.APPS_DELETE.value.startswith("apps:")

        # Wildcards should end with :*
        assert Permission.USERS_ALL.value == "users:*"
        assert Permission.APPS_ALL.value == "apps:*"


class TestGetRBACService:
    """Tests for global RBAC service singleton."""

    def test_get_rbac_service_returns_instance(self):
        """Should return RBACService instance."""
        service = get_rbac_service()
        assert isinstance(service, RBACService)

    def test_get_rbac_service_singleton(self):
        """Should return same instance on multiple calls."""
        service1 = get_rbac_service()
        service2 = get_rbac_service()
        assert service1 is service2
