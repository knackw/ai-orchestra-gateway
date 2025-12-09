"""
Unit tests for Settings API endpoints.

Tests:
- API Key Management (CRUD, rotation)
- User Preferences
- Notification Settings
- Security Settings
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock

from app.api.v1.settings import router, _api_keys_store, _settings_store
from app.core.security import get_current_license


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear in-memory stores before each test."""
    _api_keys_store.clear()
    _settings_store.clear()
    yield
    _api_keys_store.clear()
    _settings_store.clear()


@pytest.fixture
def mock_license():
    """Create a mock license info."""
    license_info = MagicMock()
    license_info.tenant_id = "test-tenant-123"
    license_info.license_uuid = "license-uuid-123"
    license_info.app_id = "app-123"
    license_info.credits_remaining = 1000
    license_info.is_active = True
    return license_info


@pytest.fixture
def client(mock_license):
    """Create test client with mocked auth."""
    app = FastAPI()
    app.include_router(router)

    # Override the dependency
    app.dependency_overrides[get_current_license] = lambda: mock_license

    yield TestClient(app)

    # Clean up
    app.dependency_overrides.clear()


class TestAPIKeyList:
    """Tests for listing API keys."""

    def test_list_empty(self, client):
        """Should return empty list when no keys exist."""
        response = client.get("/api-keys")
        assert response.status_code == 200

        data = response.json()
        assert data["keys"] == []
        assert data["total"] == 0

    def test_list_after_create(self, client):
        """Should list created keys."""
        # Create a key first
        client.post("/api-keys", json={
            "name": "Test Key",
            "scopes": ["read"]
        })

        response = client.get("/api-keys")
        data = response.json()

        assert data["total"] == 1
        assert len(data["keys"]) == 1
        assert data["keys"][0]["name"] == "Test Key"


class TestAPIKeyCreate:
    """Tests for creating API keys."""

    def test_create_basic_key(self, client):
        """Should create a basic API key."""
        response = client.post("/api-keys", json={
            "name": "My API Key",
            "description": "For testing",
            "scopes": ["read", "write"]
        })

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "My API Key"
        assert data["description"] == "For testing"
        assert data["scopes"] == ["read", "write"]
        assert data["is_active"] is True
        assert "secret" in data  # Only returned on creation
        assert data["secret"].startswith("aog_")

    def test_create_key_with_expiry(self, client):
        """Should create key with expiration."""
        response = client.post("/api-keys", json={
            "name": "Expiring Key",
            "expires_in_days": 30
        })

        assert response.status_code == 201
        data = response.json()

        assert data["expires_at"] is not None

    def test_create_key_invalid_scope(self, client):
        """Should reject invalid scopes."""
        response = client.post("/api-keys", json={
            "name": "Bad Key",
            "scopes": ["invalid_scope"]
        })

        assert response.status_code == 400
        assert "Invalid scope" in response.json()["detail"]

    def test_create_key_empty_name(self, client):
        """Should reject empty name."""
        response = client.post("/api-keys", json={
            "name": "",
            "scopes": ["read"]
        })

        assert response.status_code == 422

    def test_secret_only_shown_once(self, client):
        """Secret should only be returned on creation."""
        # Create
        create_response = client.post("/api-keys", json={
            "name": "Secret Test",
            "scopes": ["read"]
        })
        key_id = create_response.json()["id"]

        # Get
        get_response = client.get(f"/api-keys/{key_id}")
        data = get_response.json()

        assert "secret" not in data


class TestAPIKeyGet:
    """Tests for getting a single API key."""

    def test_get_existing_key(self, client):
        """Should return key details."""
        # Create first
        create_response = client.post("/api-keys", json={
            "name": "Test Key",
            "scopes": ["read"]
        })
        key_id = create_response.json()["id"]

        # Get
        response = client.get(f"/api-keys/{key_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == key_id
        assert data["name"] == "Test Key"

    def test_get_nonexistent_key(self, client):
        """Should return 404 for non-existent key."""
        response = client.get("/api-keys/nonexistent")
        assert response.status_code == 404


class TestAPIKeyUpdate:
    """Tests for updating API keys."""

    def test_update_name(self, client):
        """Should update key name."""
        # Create
        create_response = client.post("/api-keys", json={
            "name": "Original Name",
            "scopes": ["read"]
        })
        key_id = create_response.json()["id"]

        # Update
        response = client.put(f"/api-keys/{key_id}", json={
            "name": "New Name"
        })

        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    def test_update_scopes(self, client):
        """Should update key scopes."""
        # Create
        create_response = client.post("/api-keys", json={
            "name": "Test Key",
            "scopes": ["read"]
        })
        key_id = create_response.json()["id"]

        # Update
        response = client.put(f"/api-keys/{key_id}", json={
            "scopes": ["read", "write", "admin"]
        })

        assert response.status_code == 200
        assert set(response.json()["scopes"]) == {"read", "write", "admin"}

    def test_deactivate_key(self, client):
        """Should deactivate key."""
        # Create
        create_response = client.post("/api-keys", json={
            "name": "Test Key",
            "scopes": ["read"]
        })
        key_id = create_response.json()["id"]

        # Deactivate
        response = client.put(f"/api-keys/{key_id}", json={
            "is_active": False
        })

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_update_invalid_scope(self, client):
        """Should reject invalid scope update."""
        # Create
        create_response = client.post("/api-keys", json={
            "name": "Test Key",
            "scopes": ["read"]
        })
        key_id = create_response.json()["id"]

        # Update with invalid scope
        response = client.put(f"/api-keys/{key_id}", json={
            "scopes": ["invalid"]
        })

        assert response.status_code == 400


class TestAPIKeyDelete:
    """Tests for deleting API keys."""

    def test_delete_key(self, client):
        """Should delete key."""
        # Create
        create_response = client.post("/api-keys", json={
            "name": "To Delete",
            "scopes": ["read"]
        })
        key_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/api-keys/{key_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api-keys/{key_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent(self, client):
        """Should return 404 for non-existent key."""
        response = client.delete("/api-keys/nonexistent")
        assert response.status_code == 404


class TestAPIKeyRotate:
    """Tests for rotating API keys."""

    def test_rotate_key(self, client):
        """Should create new key with same settings."""
        # Create
        create_response = client.post("/api-keys", json={
            "name": "Rotate Me",
            "description": "Test rotation",
            "scopes": ["read", "write"]
        })
        old_id = create_response.json()["id"]
        old_secret = create_response.json()["secret"]

        # Rotate
        response = client.post(f"/api-keys/{old_id}/rotate")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] != old_id
        assert data["secret"] != old_secret
        assert data["name"] == "Rotate Me"
        assert data["description"] == "Test rotation"
        assert data["scopes"] == ["read", "write"]

        # Old key should be gone
        old_response = client.get(f"/api-keys/{old_id}")
        assert old_response.status_code == 404

    def test_rotate_nonexistent(self, client):
        """Should return 404 for non-existent key."""
        response = client.post("/api-keys/nonexistent/rotate")
        assert response.status_code == 404


class TestUserPreferences:
    """Tests for user preferences endpoints."""

    def test_get_default_preferences(self, client):
        """Should return default preferences."""
        response = client.get("/preferences")
        assert response.status_code == 200

        data = response.json()
        assert data["theme"] == "system"
        assert data["language"] == "en"
        assert data["timezone"] == "UTC"

    def test_update_preferences(self, client):
        """Should update preferences."""
        response = client.put("/preferences", json={
            "theme": "dark",
            "language": "de",
            "timezone": "Europe/Berlin",
            "date_format": "DD.MM.YYYY",
            "items_per_page": 50
        })

        assert response.status_code == 200
        data = response.json()

        assert data["theme"] == "dark"
        assert data["language"] == "de"
        assert data["timezone"] == "Europe/Berlin"

    def test_invalid_theme(self, client):
        """Should reject invalid theme."""
        response = client.put("/preferences", json={
            "theme": "invalid",
            "language": "en",
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "items_per_page": 25
        })

        assert response.status_code == 400
        assert "Invalid theme" in response.json()["detail"]

    def test_invalid_language(self, client):
        """Should reject invalid language."""
        response = client.put("/preferences", json={
            "theme": "light",
            "language": "invalid",
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "items_per_page": 25
        })

        assert response.status_code == 400
        assert "Invalid language" in response.json()["detail"]


class TestNotificationSettings:
    """Tests for notification settings endpoints."""

    def test_get_default_notifications(self, client):
        """Should return default notification settings."""
        response = client.get("/notifications")
        assert response.status_code == 200

        data = response.json()
        assert data["email_notifications"] is True
        assert data["usage_alerts"] is True
        assert data["usage_threshold"] == 80

    def test_update_notifications(self, client):
        """Should update notification settings."""
        response = client.put("/notifications", json={
            "email_notifications": False,
            "usage_alerts": True,
            "usage_threshold": 50,
            "security_alerts": True,
            "newsletter": True,
            "weekly_summary": False
        })

        assert response.status_code == 200
        data = response.json()

        assert data["email_notifications"] is False
        assert data["usage_threshold"] == 50
        assert data["newsletter"] is True

    def test_invalid_threshold(self, client):
        """Should reject invalid usage threshold."""
        response = client.put("/notifications", json={
            "email_notifications": True,
            "usage_alerts": True,
            "usage_threshold": 150,  # Invalid
            "security_alerts": True,
            "newsletter": False,
            "weekly_summary": True
        })

        assert response.status_code == 400
        assert "threshold" in response.json()["detail"].lower()


class TestSecuritySettings:
    """Tests for security settings endpoints."""

    def test_get_default_security(self, client):
        """Should return default security settings."""
        response = client.get("/security")
        assert response.status_code == 200

        data = response.json()
        assert data["two_factor_enabled"] is False
        assert data["session_timeout_minutes"] == 60
        assert data["ip_whitelist_enabled"] is False

    def test_update_security(self, client):
        """Should update security settings."""
        response = client.put("/security", json={
            "two_factor_enabled": True,
            "session_timeout_minutes": 30,
            "ip_whitelist_enabled": True,
            "allowed_ips": ["192.168.1.0/24"],
            "require_key_rotation": True,
            "key_rotation_days": 60
        })

        assert response.status_code == 200
        data = response.json()

        assert data["two_factor_enabled"] is True
        assert data["session_timeout_minutes"] == 30
        assert data["allowed_ips"] == ["192.168.1.0/24"]

    def test_invalid_session_timeout(self, client):
        """Should reject invalid session timeout."""
        response = client.put("/security", json={
            "two_factor_enabled": False,
            "session_timeout_minutes": 2,  # Too short
            "ip_whitelist_enabled": False,
            "allowed_ips": [],
            "require_key_rotation": False,
            "key_rotation_days": 90
        })

        assert response.status_code == 400
        assert "timeout" in response.json()["detail"].lower()

    def test_invalid_rotation_days(self, client):
        """Should reject invalid key rotation days."""
        response = client.put("/security", json={
            "two_factor_enabled": False,
            "session_timeout_minutes": 60,
            "ip_whitelist_enabled": False,
            "allowed_ips": [],
            "require_key_rotation": True,
            "key_rotation_days": 3  # Too short
        })

        assert response.status_code == 400
        assert "rotation" in response.json()["detail"].lower()


class TestAllSettings:
    """Tests for combined settings endpoint."""

    def test_get_all_settings(self, client):
        """Should return all settings at once."""
        response = client.get("/all")
        assert response.status_code == 200

        data = response.json()
        assert "preferences" in data
        assert "notifications" in data
        assert "security" in data

        assert data["preferences"]["theme"] == "system"
        assert data["notifications"]["email_notifications"] is True
        assert data["security"]["two_factor_enabled"] is False

    def test_settings_persist_across_endpoints(self, client):
        """Changes should persist across all endpoints."""
        # Update preferences
        client.put("/preferences", json={
            "theme": "dark",
            "language": "de",
            "timezone": "Europe/Berlin",
            "date_format": "DD.MM.YYYY",
            "items_per_page": 100
        })

        # Check in /all
        response = client.get("/all")
        data = response.json()

        assert data["preferences"]["theme"] == "dark"
        assert data["preferences"]["language"] == "de"


class TestAPIKeyPrefixFormat:
    """Tests for API key format."""

    def test_key_format(self, client):
        """Key should have proper format."""
        response = client.post("/api-keys", json={
            "name": "Format Test",
            "scopes": ["read"]
        })

        data = response.json()

        # Full secret format: aog_XXXXXXXX_YYYYYYYYYYYYYYYYYYYY...
        assert data["secret"].startswith("aog_")
        parts = data["secret"].split("_")
        assert len(parts) == 3
        assert parts[0] == "aog"
        assert len(parts[1]) == 8  # Prefix part
        assert len(parts[2]) == 48  # Secret part

        # Prefix stored (for display)
        assert data["prefix"].startswith("aog_")

    def test_unique_keys(self, client):
        """Each key should be unique."""
        secrets = set()

        for _ in range(5):
            response = client.post("/api-keys", json={
                "name": "Unique Test",
                "scopes": ["read"]
            })
            secrets.add(response.json()["secret"])

        assert len(secrets) == 5


class TestMultipleKeysPerTenant:
    """Tests for managing multiple keys."""

    def test_create_multiple_keys(self, client):
        """Should support multiple keys per tenant."""
        for i in range(3):
            response = client.post("/api-keys", json={
                "name": f"Key {i}",
                "scopes": ["read"]
            })
            assert response.status_code == 201

        list_response = client.get("/api-keys")
        assert list_response.json()["total"] == 3

    def test_keys_isolated_by_tenant(self):
        """Keys should be isolated per tenant."""
        app = FastAPI()
        app.include_router(router)

        # Create mock for tenant 1
        mock1 = MagicMock()
        mock1.tenant_id = "tenant-1"
        app.dependency_overrides[get_current_license] = lambda: mock1

        client1 = TestClient(app)
        client1.post("/api-keys", json={"name": "Tenant 1 Key", "scopes": ["read"]})

        # Create mock for tenant 2
        mock2 = MagicMock()
        mock2.tenant_id = "tenant-2"
        app.dependency_overrides[get_current_license] = lambda: mock2

        client2 = TestClient(app)
        client2.post("/api-keys", json={"name": "Tenant 2 Key", "scopes": ["read"]})

        # Verify isolation - switch back to tenant 1
        app.dependency_overrides[get_current_license] = lambda: mock1

        response = TestClient(app).get("/api-keys")
        keys = response.json()["keys"]
        assert len(keys) == 1
        assert keys[0]["name"] == "Tenant 1 Key"

        app.dependency_overrides.clear()
