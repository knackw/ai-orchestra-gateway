"""
Unit tests for admin tenant management endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Mock admin key for testing
MOCK_ADMIN_KEY = "test_admin_key_12345"


@pytest.fixture(autouse=True)
def mock_admin_key():
    """Mock admin API key for all tests."""
    with patch("app.core.admin_auth.settings") as mock_settings:
        mock_settings.ADMIN_API_KEY = MOCK_ADMIN_KEY
        yield


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch("app.api.admin.tenants.get_supabase_client") as mock:
        yield mock


class TestAdminAuth:
    """Tests for admin authentication."""

    def test_missing_admin_key_rejected(self):
        """Test that requests without X-Admin-Key are rejected."""
        response = client.get("/admin/tenants")
        assert response.status_code == 422  # Missing required header

    def test_invalid_admin_key_rejected(self):
        """Test that invalid admin key is rejected."""
        response = client.get(
            "/admin/tenants",
            headers={"X-Admin-Key": "invalid_key"}
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
            "/admin/tenants",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY},
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
            "/admin/tenants",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY},
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
            "/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY}
        )

        assert response.status_code == 200
        assert response.json()["name"] == "ACME Corp"

    def test_get_tenant_not_found(self, mock_supabase):
        """Test getting non-existent tenant."""
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.return_value = mock_client

        response = client.get(
            "/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY}
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
            "/admin/tenants",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY}
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
            "/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY},
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
            "/admin/tenants/550e8400-e29b-41d4-a716-446655440000",
            headers={"X-Admin-Key": MOCK_ADMIN_KEY}
        )

        assert response.status_code == 204
