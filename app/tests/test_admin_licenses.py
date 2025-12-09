"""
Unit tests for admin license management endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.api.admin.licenses import generate_license_key
from app.core.rbac import Role, UserRole

client = TestClient(app)

MOCK_ADMIN_KEY = "test_admin_key_12345"
MOCK_LICENSE_KEY = "lic_test_license_key_123"
VALID_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
VALID_LICENSE_ID = "550e8400-e29b-41d4-a716-446655440001"
MOCK_USER_ID = str(uuid4())
API_PREFIX = "/api/v1"


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
        mock_license_info.tenant_id = VALID_TENANT_ID
        mock_license_info.app_id = "test-app"
        mock_license_info.credits_remaining = 1000
        mock_license_info.is_active = True
        mock_license_info.expires_at = None
        mock_validate.return_value = mock_license_info

        # Mock RBAC service with admin role
        mock_rbac = Mock()
        mock_user_role = UserRole(
            user_id=MOCK_USER_ID,
            tenant_id=VALID_TENANT_ID,
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
    with patch("app.api.admin.licenses.get_supabase_client") as mock:
        yield mock


def get_admin_headers():
    """Return headers required for admin routes (SEC-009)."""
    return {
        "X-Admin-Key": MOCK_ADMIN_KEY,
        "X-License-Key": MOCK_LICENSE_KEY,
    }


class TestLicenseKeyGeneration:
    """Tests for license key generation."""

    def test_license_key_format(self):
        """Test that generated keys have correct format."""
        key = generate_license_key()
        assert key.startswith("lic_")
        assert len(key) > 32  # lic_ + at least 32 chars

    def test_license_keys_unique(self):
        """Test that generated keys are unique."""
        keys = {generate_license_key() for _ in range(100)}
        assert len(keys) == 100  # All unique


class TestLicenseCRUD:
    """Tests for license CRUD operations."""

    def test_create_license_success(self, mock_supabase):
        """Test successful license creation."""
        mock_client = Mock()
        # Mock tenant exists
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": VALID_TENANT_ID}]
        # Mock license creation
        mock_client.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": VALID_LICENSE_ID,
            "tenant_id": VALID_TENANT_ID,
            "license_key": "lic_test123456789",
            "credits_remaining": 10000,
            "is_active": True,
            "expires_at": None,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.post(
            f"{API_PREFIX}/admin/licenses",
            headers=get_admin_headers(),
            json={
                "tenant_id": VALID_TENANT_ID,
                "credits": 10000
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["credits_remaining"] == 10000
        assert "license_key" in data
        assert data["license_key"].startswith("lic_")

    def test_create_license_tenant_not_found(self, mock_supabase):
        """Test creating license for non-existent tenant."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.return_value = mock_client

        response = client.post(
            f"{API_PREFIX}/admin/licenses",
            headers=get_admin_headers(),
            json={
                "tenant_id": VALID_TENANT_ID,
                "credits": 10000
            }
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_license_hides_key(self, mock_supabase):
        """Test that GET license does not show license key."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            "id": VALID_LICENSE_ID,
            "tenant_id": VALID_TENANT_ID,
            "license_key": "lic_secret_key",
            "credits_remaining": 5000,
            "is_active": True,
            "expires_at": None,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.get(
            f"{API_PREFIX}/admin/licenses/{VALID_LICENSE_ID}",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["license_key"] is None  # Hidden

    def test_list_licenses(self, mock_supabase):
        """Test listing licenses."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.range.return_value.execute.return_value.data = [{
            "id": VALID_LICENSE_ID,
            "tenant_id": VALID_TENANT_ID,
            "license_key": "lic_secret",
            "credits_remaining": 5000,
            "is_active": True,
            "expires_at": None,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T10:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.get(
            f"{API_PREFIX}/admin/licenses",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["license_key"] is None  # Hidden in list

    def test_update_license_credits(self, mock_supabase):
        """Test updating license credits."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
            "id": VALID_LICENSE_ID,
            "tenant_id": VALID_TENANT_ID,
            "license_key": "lic_secret",
            "credits_remaining": 20000,
            "is_active": True,
            "expires_at": None,
            "created_at": "2025-12-04T10:00:00Z",
            "updated_at": "2025-12-04T11:00:00Z"
        }]
        mock_supabase.return_value = mock_client

        response = client.put(
            f"{API_PREFIX}/admin/licenses/{VALID_LICENSE_ID}",
            headers=get_admin_headers(),
            json={"credits_remaining": 20000}
        )

        assert response.status_code == 200
        assert response.json()["credits_remaining"] == 20000

    def test_revoke_license(self, mock_supabase):
        """Test revoking a license."""
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "test"}]
        mock_supabase.return_value = mock_client

        response = client.delete(
            f"{API_PREFIX}/admin/licenses/{VALID_LICENSE_ID}",
            headers=get_admin_headers()
        )

        assert response.status_code == 204
