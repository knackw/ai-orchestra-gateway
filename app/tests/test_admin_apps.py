"""
Unit tests for admin apps management endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.rbac import Role, UserRole

client = TestClient(app)

# Mock admin key for testing
MOCK_ADMIN_KEY = "test_admin_key_12345"
MOCK_LICENSE_KEY = "lic_test_license_key_123"
MOCK_TENANT_ID = str(uuid4())
MOCK_USER_ID = str(uuid4())


@pytest.fixture(autouse=True)
def mock_admin_key():
    """Mock admin API key for all tests."""
    with patch("app.core.admin_auth.settings") as mock_settings:
        mock_settings.ADMIN_API_KEY = MOCK_ADMIN_KEY
        yield


@pytest.fixture(autouse=True)
def mock_license_and_rbac():
    """
    Mock license validation and RBAC for all tests.
    SEC-009: Admin routes require both license key and admin role.
    """
    with patch("app.core.security.validate_license_key") as mock_validate, \
         patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:
        # Mock license validation
        mock_license_info = Mock()
        mock_license_info.license_key = MOCK_LICENSE_KEY
        mock_license_info.license_uuid = MOCK_USER_ID
        mock_license_info.tenant_id = MOCK_TENANT_ID
        mock_license_info.app_id = "test-app"
        mock_license_info.credits_remaining = 1000
        mock_license_info.is_active = True
        mock_license_info.expires_at = None
        mock_validate.return_value = mock_license_info

        # Mock RBAC service with admin role
        mock_rbac = Mock()
        mock_user_role = UserRole(
            user_id=MOCK_USER_ID,
            tenant_id=MOCK_TENANT_ID,
            role=Role.ADMIN,
            granted_by=None,
            granted_at=None,
            expires_at=None,
            is_active=True,
        )

        async def mock_get_user_role(user_id, tenant_id):
            return mock_user_role

        mock_rbac.get_user_role = mock_get_user_role
        mock_rbac_service.return_value = mock_rbac

        yield


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch("app.api.admin.apps.get_supabase_client") as mock:
        yield mock


def get_admin_headers():
    """Return headers required for admin routes (SEC-009)."""
    return {
        "X-Admin-Key": MOCK_ADMIN_KEY,
        "X-License-Key": MOCK_LICENSE_KEY,
    }


class TestAppCRUD:
    """Tests for app CRUD operations."""

    def test_create_app_success(self, mock_supabase):
        """Test successful app creation."""
        mock_client = Mock()
        # Mock tenant existence check
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "tenant_1"}]
        # Mock app creation
        mock_client.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "app_name": "New App",
            "allowed_origins": [],
            "is_active": True,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.post(
            "/api/v1/admin/apps",
            headers=get_admin_headers(),
            json={
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "app_name": "New App"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["app_name"] == "New App"

    def test_create_app_tenant_not_found(self, mock_supabase):
        """Test creating app for non-existent tenant."""
        mock_client = Mock()
        # Mock tenant check returning empty
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.return_value = mock_client

        response = client.post(
            "/api/v1/admin/apps",
            headers=get_admin_headers(),
            json={
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "app_name": "Ghost App"
            }
        )

        assert response.status_code == 404
        assert "Tenant" in response.json()["detail"]

    def test_list_apps(self, mock_supabase):
        """Test listing apps."""
        mock_client = Mock()
        # Ensure chain support for optional filter
        # If tenant_id is NOT provided, it goes select->range->execute
        # If I want to be safe, I should configure the mock so that 'select' returns a mock that handles both 'range' and 'eq'

        # Simpler approach: Set the end result on the likely path
        # Code: query = client.table("apps").select("*") -> query.range().execute()
        mock_client.table.return_value.select.return_value.range.return_value.execute.return_value.data = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "app_name": "App 1",
                "is_active": True,
                "created_at": "2025-12-04T10:00:00Z",
                "updated_at": "2025-12-04T10:00:00Z"
            }
        ]
        mock_supabase.return_value = mock_client

        response = client.get(
            "/api/v1/admin/apps",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_app(self, mock_supabase):
        """Test getting specific app."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "app_name": "App 1",
            "is_active": True,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.get(
            "/api/v1/admin/apps/550e8400-e29b-41d4-a716-446655440001",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        assert response.json()["app_name"] == "App 1"

    def test_update_app(self, mock_supabase):
        """Test updating app."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "app_name": "Updated Name",
            "is_active": True,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.put(
            "/api/v1/admin/apps/550e8400-e29b-41d4-a716-446655440001",
            headers=get_admin_headers(),
            json={"app_name": "Updated Name"}
        )

        assert response.status_code == 200
        assert response.json()["app_name"] == "Updated Name"

    def test_delete_app(self, mock_supabase):
        """Test soft deleting app."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "550e8400-e29b-41d4-a716-446655440001"}]
        mock_supabase.return_value = mock_client

        response = client.delete(
            "/api/v1/admin/apps/550e8400-e29b-41d4-a716-446655440001",
            headers=get_admin_headers()
        )

        assert response.status_code == 204
