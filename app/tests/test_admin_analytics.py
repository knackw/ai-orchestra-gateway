import pytest
from unittest.mock import MagicMock, Mock, patch
from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app
from app.core.rbac import Role, UserRole

client = TestClient(app)

# Mock credentials
MOCK_ADMIN_KEY = "admin_test_key"
MOCK_LICENSE_KEY = "lic_test_license_key_123"
MOCK_TENANT_ID = str(uuid4())
MOCK_USER_ID = str(uuid4())


@pytest.fixture(autouse=True)
def mock_admin_auth():
    """
    Mock admin authentication for all tests.
    SEC-009: Admin routes require both X-Admin-Key and X-License-Key with admin role.
    """
    with patch("app.core.admin_auth.settings") as mock_settings, \
         patch("app.core.security.validate_license_key") as mock_validate, \
         patch("app.core.admin_auth.get_rbac_service") as mock_rbac_service:

        mock_settings.ADMIN_API_KEY = MOCK_ADMIN_KEY

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


def get_admin_headers():
    """Return headers required for admin routes (SEC-009)."""
    return {
        "X-Admin-Key": MOCK_ADMIN_KEY,
        "X-License-Key": MOCK_LICENSE_KEY,
    }


class TestAdminAnalytics:
    
    @patch("app.api.admin.analytics.get_supabase_client")
    def test_get_credit_stats(self, mock_get_client):
        """Test aggregation of credit stats."""
        # Mock Supabase response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            {"credits_total": 1000, "credits_remaining": 500},
            {"credits_total": 2000, "credits_remaining": 1500},
            {"credits_total": 500, "credits_remaining": 0}
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get(
            "/api/v1/admin/analytics/stats/credits",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        data = response.json()

        # Total Alloc: 1000 + 2000 + 500 = 3500
        # Total Rem: 500 + 1500 + 0 = 2000
        # Total Used: 3500 - 2000 = 1500

        assert data["total_allocated"] == 3500
        assert data["total_remaining"] == 2000
        assert data["total_used"] == 1500

    @patch("app.api.admin.analytics.get_supabase_client")
    def test_get_top_tenants(self, mock_get_client):
        """Test top tenants calculation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            # Tenant A: Used 500 (1000 - 500)
            {"credits_total": 1000, "credits_remaining": 500, "tenants": {"id": "t1", "name": "Tenant A"}},
            # Tenant B: Used 100 (1000 - 900)
            {"credits_total": 1000, "credits_remaining": 900, "tenants": {"id": "t2", "name": "Tenant B"}},
            # Tenant A again: Used 200 (1000 - 800)
            {"credits_total": 1000, "credits_remaining": 800, "tenants": {"id": "t1", "name": "Tenant A"}}
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get(
            "/api/v1/admin/analytics/stats/top-tenants?limit=5",
            headers=get_admin_headers()
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

        # Tenant A total usage: 500 + 200 = 700
        assert data[0]["name"] == "Tenant A"
        assert data[0]["total_usage"] == 700

        # Tenant B total usage: 100
        assert data[1]["name"] == "Tenant B"
        assert data[1]["total_usage"] == 100

    @patch("app.api.admin.analytics.get_supabase_client")
    def test_get_usage_over_time(self, mock_get_client):
        """Test usage over time endpoint using view."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            {"usage_date": "2023-01-01", "provider": "anthropic", "request_count": 10},
            {"usage_date": "2023-01-01", "provider": "scaleway", "request_count": 5}
        ]
        mock_client.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get(
            "/api/v1/admin/analytics/stats/usage-over-time",
            headers=get_admin_headers()
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["provider"] == "anthropic"

    @patch("app.api.admin.analytics.get_supabase_client")
    def test_get_provider_split(self, mock_get_client):
        """Test provider split calculation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            {"provider": "anthropic", "request_count": 100},
            {"provider": "anthropic", "request_count": 50},  # checking aggregation
            {"provider": "scaleway", "request_count": 20}
        ]
        mock_client.table.return_value.select.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get(
            "/api/v1/admin/analytics/stats/provider-split",
            headers=get_admin_headers()
        )
        assert response.status_code == 200
        data = response.json()

        # Should aggregate: anthropic=150, scaleway=20
        assert len(data) == 2
        anthropic = next(item for item in data if item["provider"] == "anthropic")
        assert anthropic["count"] == 150

    @patch("app.api.admin.analytics.get_supabase_client")
    def test_export_usage_logs(self, mock_get_client):
        """Test CSV export streaming."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        # Mocking usage logs data
        mock_response.data = [
            {
                "id": "log1", "created_at": "2023-01-01",
                "license_id": "lic1", "app_id": "app1", "tenant_id": "t1",
                "provider": "anthropic", "model": "claude",
                "prompt_length": 10, "tokens_used": 20,
                "credits_deducted": 2, "response_status": "success",
                "pii_detected": False
            }
        ]
        mock_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.get(
            "/api/v1/admin/analytics/stats/export",
            headers=get_admin_headers()
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment; filename=usage_logs.csv" in response.headers["content-disposition"]

        content = response.text
        # Check header
        assert "id,created_at,license_id" in content
        # Check data
        assert "log1,2023-01-01,lic1" in content
