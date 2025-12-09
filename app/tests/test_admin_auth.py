"""
Unit tests for SEC-009: Admin-Route Authorization.

Tests that admin routes require both:
1. Valid X-Admin-Key header
2. Admin or owner role in the user's tenant
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.rbac import Role, UserRole

client = TestClient(app)

MOCK_ADMIN_KEY = "test_admin_key_sec009"
VALID_LICENSE_KEY = "lic_test_license_key_123"
VALID_TENANT_ID = str(uuid4())
VALID_USER_ID = str(uuid4())
API_PREFIX = "/api/v1"


@pytest.fixture(autouse=True)
def mock_admin_key():
    """Mock admin API key for all tests."""
    with patch("app.core.admin_auth.settings") as mock_settings:
        mock_settings.ADMIN_API_KEY = MOCK_ADMIN_KEY
        yield


@pytest.fixture
def mock_license_validation():
    """Mock license validation to return a valid license."""
    with patch("app.core.security.validate_license_key") as mock_validate:
        mock_license_info = Mock()
        mock_license_info.license_key = VALID_LICENSE_KEY
        mock_license_info.license_uuid = VALID_USER_ID
        mock_license_info.tenant_id = VALID_TENANT_ID
        mock_license_info.app_id = "test-app"
        mock_license_info.credits_remaining = 1000
        mock_license_info.is_active = True
        mock_license_info.expires_at = None

        mock_validate.return_value = mock_license_info
        yield mock_validate


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch("app.api.admin.tenants.get_supabase_client") as mock:
        yield mock


class TestAdminKeyValidation:
    """Tests for admin API key validation (existing functionality)."""

    def test_invalid_admin_key(self, mock_license_validation):
        """Test that invalid X-Admin-Key header returns 401."""
        response = client.get(
            f"{API_PREFIX}/admin/tenants",
            headers={
                "X-Admin-Key": "wrong_key",
                "X-License-Key": VALID_LICENSE_KEY
            }
        )
        assert response.status_code == 401
        assert "Invalid admin API key" in response.json()["detail"]

    def test_valid_admin_key_without_license(self):
        """Test that valid admin key but missing license key returns 401."""
        response = client.get(
            f"{API_PREFIX}/admin/tenants",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY}
        )
        assert response.status_code == 401
        assert "Missing X-License-Key header" in response.json()["detail"]


class TestAdminRoleAuthorization:
    """Tests for SEC-009: Role-based authorization for admin routes."""

    def test_admin_role_granted_access(self, mock_license_validation, mock_supabase):
        """Test that user with admin role can access admin routes."""
        # Mock RBAC service to return admin role
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()
            mock_user_role = UserRole(
                user_id=VALID_USER_ID,
                tenant_id=VALID_TENANT_ID,
                role=Role.ADMIN,
                granted_by=None,
                granted_at=None,
                expires_at=None,
                is_active=True,
            )

            # Make get_user_role async
            async def mock_get_user_role(user_id, tenant_id):
                return mock_user_role

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            # Mock Supabase response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.data = []
            mock_client.table.return_value.select.return_value.range.return_value.execute.return_value = mock_response
            mock_supabase.return_value = mock_client

            response = client.get(
                f"{API_PREFIX}/admin/tenants",
                headers={
                    "X-Admin-Key": MOCK_ADMIN_KEY,
                    "X-License-Key": VALID_LICENSE_KEY
                }
            )

            # Should succeed (or at least not fail on authorization)
            assert response.status_code == 200

    def test_owner_role_granted_access(self, mock_license_validation, mock_supabase):
        """Test that user with owner role can access admin routes."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()
            mock_user_role = UserRole(
                user_id=VALID_USER_ID,
                tenant_id=VALID_TENANT_ID,
                role=Role.OWNER,
                granted_by=None,
                granted_at=None,
                expires_at=None,
                is_active=True,
            )

            async def mock_get_user_role(user_id, tenant_id):
                return mock_user_role

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            # Mock Supabase response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.data = []
            mock_client.table.return_value.select.return_value.range.return_value.execute.return_value = mock_response
            mock_supabase.return_value = mock_client

            response = client.get(
                f"{API_PREFIX}/admin/tenants",
                headers={
                    "X-Admin-Key": MOCK_ADMIN_KEY,
                    "X-License-Key": VALID_LICENSE_KEY
                }
            )

            assert response.status_code == 200

    def test_member_role_denied_access(self, mock_license_validation):
        """Test that user with member role is denied access to admin routes."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()
            mock_user_role = UserRole(
                user_id=VALID_USER_ID,
                tenant_id=VALID_TENANT_ID,
                role=Role.MEMBER,
                granted_by=None,
                granted_at=None,
                expires_at=None,
                is_active=True,
            )

            async def mock_get_user_role(user_id, tenant_id):
                return mock_user_role

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            response = client.get(
                f"{API_PREFIX}/admin/tenants",
                headers={
                    "X-Admin-Key": MOCK_ADMIN_KEY,
                    "X-License-Key": VALID_LICENSE_KEY
                }
            )

            assert response.status_code == 403
            assert "Admin or owner role required" in response.json()["detail"]
            assert "member" in response.json()["detail"].lower()

    def test_viewer_role_denied_access(self, mock_license_validation):
        """Test that user with viewer role is denied access to admin routes."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()
            mock_user_role = UserRole(
                user_id=VALID_USER_ID,
                tenant_id=VALID_TENANT_ID,
                role=Role.VIEWER,
                granted_by=None,
                granted_at=None,
                expires_at=None,
                is_active=True,
            )

            async def mock_get_user_role(user_id, tenant_id):
                return mock_user_role

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            response = client.get(
                f"{API_PREFIX}/admin/tenants",
                headers={
                    "X-Admin-Key": MOCK_ADMIN_KEY,
                    "X-License-Key": VALID_LICENSE_KEY
                }
            )

            assert response.status_code == 403
            assert "Admin or owner role required" in response.json()["detail"]

    def test_no_role_assigned_denied_access(self, mock_license_validation):
        """Test that user with no role assigned is denied access."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()

            async def mock_get_user_role(user_id, tenant_id):
                return None  # No role assigned

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            response = client.get(
                f"{API_PREFIX}/admin/tenants",
                headers={
                    "X-Admin-Key": MOCK_ADMIN_KEY,
                    "X-License-Key": VALID_LICENSE_KEY
                }
            )

            assert response.status_code == 403
            assert "No role assigned" in response.json()["detail"]


class TestAdminRouteCoverage:
    """Test that all admin routes are protected."""

    def test_tenant_routes_require_admin_role(self, mock_license_validation):
        """Test that all tenant management routes require admin role."""
        tenant_id = str(uuid4())

        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()

            async def mock_get_user_role(user_id, tenant_id):
                return None

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            headers = {
                "X-Admin-Key": MOCK_ADMIN_KEY,
                "X-License-Key": VALID_LICENSE_KEY
            }

            # Test all tenant endpoints
            routes = [
                ("GET", f"{API_PREFIX}/admin/tenants"),
                ("GET", f"{API_PREFIX}/admin/tenants/{tenant_id}"),
                ("PUT", f"{API_PREFIX}/admin/tenants/{tenant_id}"),
                ("DELETE", f"{API_PREFIX}/admin/tenants/{tenant_id}"),
            ]

            for method, route in routes:
                if method == "GET":
                    response = client.get(route, headers=headers)
                elif method == "PUT":
                    response = client.put(route, headers=headers, json={"name": "Test"})
                elif method == "DELETE":
                    response = client.delete(route, headers=headers)

                assert response.status_code == 403, f"Route {method} {route} should require admin role"

    def test_license_routes_require_admin_role(self, mock_license_validation):
        """Test that all license management routes require admin role."""
        license_id = str(uuid4())

        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()

            async def mock_get_user_role(user_id, tenant_id):
                return None

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            headers = {
                "X-Admin-Key": MOCK_ADMIN_KEY,
                "X-License-Key": VALID_LICENSE_KEY
            }

            routes = [
                ("GET", f"{API_PREFIX}/admin/licenses"),
                ("GET", f"{API_PREFIX}/admin/licenses/{license_id}"),
                ("PUT", f"{API_PREFIX}/admin/licenses/{license_id}"),
                ("DELETE", f"{API_PREFIX}/admin/licenses/{license_id}"),
            ]

            for method, route in routes:
                if method == "GET":
                    response = client.get(route, headers=headers)
                elif method == "PUT":
                    response = client.put(route, headers=headers, json={"credits_remaining": 100})
                elif method == "DELETE":
                    response = client.delete(route, headers=headers)

                assert response.status_code == 403, f"Route {method} {route} should require admin role"

    def test_apps_routes_require_admin_role(self, mock_license_validation):
        """Test that all app management routes require admin role."""
        app_id = str(uuid4())

        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()

            async def mock_get_user_role(user_id, tenant_id):
                return None

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            headers = {
                "X-Admin-Key": MOCK_ADMIN_KEY,
                "X-License-Key": VALID_LICENSE_KEY
            }

            routes = [
                ("GET", f"{API_PREFIX}/admin/apps"),
                ("GET", f"{API_PREFIX}/admin/apps/{app_id}"),
                ("PUT", f"{API_PREFIX}/admin/apps/{app_id}"),
                ("DELETE", f"{API_PREFIX}/admin/apps/{app_id}"),
            ]

            for method, route in routes:
                if method == "GET":
                    response = client.get(route, headers=headers)
                elif method == "PUT":
                    response = client.put(route, headers=headers, json={"app_name": "Test"})
                elif method == "DELETE":
                    response = client.delete(route, headers=headers)

                assert response.status_code == 403, f"Route {method} {route} should require admin role"

    def test_analytics_routes_require_admin_role(self, mock_license_validation):
        """Test that analytics routes require admin role."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()

            async def mock_get_user_role(user_id, tenant_id):
                return None

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            headers = {
                "X-Admin-Key": MOCK_ADMIN_KEY,
                "X-License-Key": VALID_LICENSE_KEY
            }

            routes = [
                f"{API_PREFIX}/admin/analytics/stats/credits",
                f"{API_PREFIX}/admin/analytics/stats/top-tenants",
            ]

            for route in routes:
                response = client.get(route, headers=headers)
                assert response.status_code == 403, f"Route {route} should require admin role"

    def test_audit_logs_routes_require_admin_role(self, mock_license_validation):
        """Test that audit log routes require admin role."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()

            async def mock_get_user_role(user_id, tenant_id):
                return None

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            headers = {
                "X-Admin-Key": MOCK_ADMIN_KEY,
                "X-License-Key": VALID_LICENSE_KEY
            }

            response = client.get(f"{API_PREFIX}/admin/audit-logs", headers=headers)
            assert response.status_code == 403, "Audit logs route should require admin role"


class TestUnauthorizedAccessLogging:
    """Test that unauthorized access attempts are logged."""

    def test_unauthorized_access_logged(self, mock_license_validation, caplog):
        """Test that unauthorized admin access attempts are logged."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()
            mock_user_role = UserRole(
                user_id=VALID_USER_ID,
                tenant_id=VALID_TENANT_ID,
                role=Role.VIEWER,
                granted_by=None,
                granted_at=None,
                expires_at=None,
                is_active=True,
            )

            async def mock_get_user_role(user_id, tenant_id):
                return mock_user_role

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            with caplog.at_level("WARNING"):
                response = client.get(
                    f"{API_PREFIX}/admin/tenants",
                    headers={
                        "X-Admin-Key": MOCK_ADMIN_KEY,
                        "X-License-Key": VALID_LICENSE_KEY
                    }
                )

                assert response.status_code == 403

                # Check that the denial was logged
                log_messages = [record.message for record in caplog.records]
                assert any("SEC-009" in msg and "denied" in msg.lower() for msg in log_messages)

    def test_no_role_access_logged(self, mock_license_validation, caplog):
        """Test that access attempts with no role are logged."""
        with patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
            mock_rbac = Mock()

            async def mock_get_user_role(user_id, tenant_id):
                return None

            mock_rbac.get_user_role = mock_get_user_role
            mock_rbac_service.return_value = mock_rbac

            with caplog.at_level("WARNING"):
                response = client.get(
                    f"{API_PREFIX}/admin/tenants",
                    headers={
                        "X-Admin-Key": MOCK_ADMIN_KEY,
                        "X-License-Key": VALID_LICENSE_KEY
                    }
                )

                assert response.status_code == 403

                log_messages = [record.message for record in caplog.records]
                assert any("SEC-009" in msg and "no role" in msg.lower() for msg in log_messages)
