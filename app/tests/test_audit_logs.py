import pytest
from unittest.mock import MagicMock, Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime
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


class TestAuditLogs:
    
    @patch("app.api.admin.audit_logs.get_supabase_client")
    def test_get_audit_logs_pagination(self, mock_get_client):
        """Test pagination of audit logs."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "log1", "created_at": "2023-01-01T10:00:00Z",
                "provider": "anthropic", "prompt_length": 100, 
                "tokens_used": 50, "credits_deducted": 5, 
                "pii_detected": False, "response_status": "success",
                "tenants": {"name": "Tenant A"},
                "licenses": {"license_key": "lic_1"}
            }
        ]
        mock_response.count = 100
        mock_client.table.return_value.select.return_value.range.return_value.order.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/admin/audit-logs?page=2&limit=10", headers=get_admin_headers())
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 100
        assert data["page"] == 2
        assert len(data["items"]) == 1
        assert data["items"][0]["tenant_name"] == "Tenant A"
        assert data["items"][0]["license_key"] == "lic_1"
        
        # Verify range call: page 2, limit 10 -> starts at 10, ends at 19
        mock_client.table.return_value.select.return_value.range.assert_called_with(10, 19)

    @patch("app.api.admin.audit_logs.get_supabase_client")
    def test_get_audit_logs_filter(self, mock_get_client):
        """Test filtering audit logs."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.count = 0
        
        # Build chain mock
        mock_query = MagicMock()
        mock_client.table.return_value.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.range.return_value.order.return_value.execute.return_value = mock_response
        
        mock_get_client.return_value = mock_client
        
        response = client.get("/api/v1/admin/audit-logs?tenant_id=t1&status=error", headers=get_admin_headers())
        
        assert response.status_code == 200
        
        # Verify filters applied
        # We expect two eq calls: one for tenant_id, one for status
        assert mock_query.eq.call_count == 2
