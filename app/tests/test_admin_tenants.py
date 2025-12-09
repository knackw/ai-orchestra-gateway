"""
Unit tests for admin tenant management endpoints.
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
    with patch("app.api.admin.tenants.get_supabase_client") as mock:
        yield mock


def get_admin_headers():
    """Return headers required for admin routes (SEC-009)."""
    return {
        "X-Admin-Key": MOCK_ADMIN_KEY,
        "X-License-Key": MOCK_LICENSE_KEY,
    }


class TestAdminAuth:
    """Tests for admin authentication."""

    def test_missing_admin_key_rejected(self):
        """Test that requests without X-Admin-Key are rejected."""
        response = client.get(
            "/api/v1/admin/tenants",
            headers={"X-License-Key": MOCK_LICENSE_KEY}  # Only license key
        )
        assert response.status_code == 422  # Missing required X-Admin-Key header

    def test_missing_license_key_rejected(self):
        """Test that requests without X-License-Key are rejected (SEC-009)."""
        response = client.get(
            "/api/v1/admin/tenants",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY}  # Only admin key
        )
        assert response.status_code == 401  # Missing X-License-Key

    def test_invalid_admin_key_rejected(self):
        """Test that invalid admin key is rejected."""
        response = client.get(
            "/api/v1/admin/tenants",
            headers={
                "X-Admin-Key": "invalid_key",
                "X-License-Key": MOCK_LICENSE_KEY,
            }
        )
        assert response.status_code == 401


class TestTenantCRUD:
    """Tests for tenant CRUD operations."""

    def test_create_tenant_success(self, mock_supabase):
        """Test successful tenant creation."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_client.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "ACME Corp",
            "email": "admin@acme.com",
            "is_active": True,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.post(
            "/api/v1/admin/tenants",
            headers=get_admin_headers(),
            json={"name": "ACME Corp", "email": "admin@acme.com"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "ACME Corp"
        assert data["email"] == "admin@acme.com"

    def test_create_tenant_duplicate_email(self, mock_supabase):
        """Test that duplicate email is rejected."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "existing"}]
        mock_supabase.return_value = mock_client

        response = client.post(
            "/api/v1/admin/tenants",
            headers=get_admin_headers(),
            json={"name": "ACME Corp", "email": "admin@acme.com"}
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_tenant_success(self, mock_supabase):
        """Test getting tenant by ID."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "ACME Corp",
            "email": "admin@acme.com",
            "is_active": True,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.get(
            "/api/v1/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        assert response.json()["name"] == "ACME Corp"

    def test_get_tenant_not_found(self, mock_supabase):
        """Test getting non-existent tenant."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.return_value = mock_client

        response = client.get(
            "/api/v1/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers=get_admin_headers()
        )

        assert response.status_code == 404

    def test_list_tenants(self, mock_supabase):
        """Test listing tenants."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.range.return_value.execute.return_value.data = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "ACME Corp",
                "email": "admin@acme.com",
                "is_active": True,
                "created_at": "2025-12-04T10:00:00Z",
                "updated_at": "2025-12-04T10:00:00Z"
            }
        ]
        mock_supabase.return_value = mock_client

        response = client.get(
            "/api/v1/admin/tenants",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_update_tenant(self, mock_supabase):
        """Test updating tenant."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "ACME Corporation",
            "email": "admin@acme.com",
            "is_active": True,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T11:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.put(
            "/api/v1/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers=get_admin_headers(),
            json={"name": "ACME Corporation"}
        )

        assert response.status_code == 200
        assert response.json()["name"] == "ACME Corporation"

    def test_delete_tenant(self, mock_supabase):
        """Test soft deleting tenant."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "test"}]
        mock_supabase.return_value = mock_client

        response = client.delete(
            "/api/v1/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers=get_admin_headers()
        )

        assert response.status_code == 204

    def test_avv_update(self, mock_supabase):
        """Test updating tenant AVV status."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "ACME Corp",
            "email": "admin@acme.com",
            "is_active": True,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T12:00:00Z",
            "avv_signed_at": "2025-12-04T12:00:00Z",
            "avv_version": "1.0"
        }]
        mock_supabase.return_value = mock_client

        response = client.post(
            "/api/v1/admin/tenants/550e8400-e29b-41d4-a716-446655440000/avv",
            headers=get_admin_headers(),
            json={"avv_version": "1.0"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["avv_version"] == "1.0"
        assert data["avv_signed_at"] is not None

