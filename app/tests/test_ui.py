"""
Unit tests for UI Helper API endpoints.

Tests:
- Autosave configuration and operations
- Feedback widget
- Accessibility settings
- UI state persistence
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock

from app.api.v1.ui import (
    router,
    _autosave_store,
    _autosave_config_store,
    _feedback_store,
    _accessibility_store,
    _ui_state_store,
    AutosaveStatus,
    FeedbackType,
    FeedbackPriority,
    FeedbackStatus,
)
from app.core.security import get_current_license


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear in-memory stores before each test."""
    _autosave_store.clear()
    _autosave_config_store.clear()
    _feedback_store.clear()
    _accessibility_store.clear()
    _ui_state_store.clear()
    yield
    _autosave_store.clear()
    _autosave_config_store.clear()
    _feedback_store.clear()
    _accessibility_store.clear()
    _ui_state_store.clear()


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


# ============================================================================
# Autosave Config Tests
# ============================================================================

class TestAutosaveConfig:
    """Tests for autosave configuration."""

    def test_get_default_config(self, client):
        """Should return default config."""
        response = client.get("/autosave/config")
        assert response.status_code == 200

        data = response.json()
        assert data["enabled"] is True
        assert data["interval_seconds"] == 30
        assert data["max_retries"] == 3
        assert data["show_indicator"] is True

    def test_update_config(self, client):
        """Should update config."""
        response = client.put("/autosave/config", json={
            "enabled": False,
            "interval_seconds": 60,
            "max_retries": 5,
            "show_indicator": False,
            "indicator_position": "top-left",
            "save_on_blur": False
        })

        assert response.status_code == 200
        data = response.json()

        assert data["enabled"] is False
        assert data["interval_seconds"] == 60
        assert data["indicator_position"] == "top-left"

    def test_invalid_position(self, client):
        """Should reject invalid position."""
        response = client.put("/autosave/config", json={
            "enabled": True,
            "interval_seconds": 30,
            "max_retries": 3,
            "show_indicator": True,
            "indicator_position": "center",
            "save_on_blur": True
        })

        assert response.status_code == 400
        assert "position" in response.json()["detail"].lower()


# ============================================================================
# Autosave Operation Tests
# ============================================================================

class TestAutosaveOperations:
    """Tests for autosave save/load operations."""

    def test_save_data(self, client):
        """Should save data successfully."""
        response = client.post("/autosave", json={
            "entity_type": "document",
            "entity_id": "doc-123",
            "data": {"title": "Test Doc", "content": "Hello"},
            "version": 0
        })

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "saved"
        assert data["version"] == 1
        assert "saved_at" in data

    def test_conflict_detection(self, client):
        """Should detect version conflicts."""
        # First save
        client.post("/autosave", json={
            "entity_type": "document",
            "entity_id": "doc-123",
            "data": {"content": "Version 1"},
            "version": 0
        })

        # Try to save with outdated version
        response = client.post("/autosave", json={
            "entity_type": "document",
            "entity_id": "doc-123",
            "data": {"content": "Conflicting change"},
            "version": 0  # Should be 1 now
        })

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "conflict"
        assert data["version"] == 1
        assert data["conflict_data"] == {"content": "Version 1"}

    def test_get_autosave(self, client):
        """Should retrieve autosaved data."""
        # Save first
        client.post("/autosave", json={
            "entity_type": "form",
            "entity_id": "form-456",
            "data": {"field1": "value1"},
            "version": 0
        })

        # Retrieve
        response = client.get("/autosave/form/form-456")
        assert response.status_code == 200

        data = response.json()
        assert data["conflict_data"] == {"field1": "value1"}

    def test_get_nonexistent_autosave(self, client):
        """Should return 404 for non-existent autosave."""
        response = client.get("/autosave/unknown/id")
        assert response.status_code == 404

    def test_clear_autosave(self, client):
        """Should clear autosaved data."""
        # Save first
        client.post("/autosave", json={
            "entity_type": "temp",
            "entity_id": "temp-789",
            "data": {"temp": True},
            "version": 0
        })

        # Clear
        response = client.delete("/autosave/temp/temp-789")
        assert response.status_code == 204

        # Verify cleared
        get_response = client.get("/autosave/temp/temp-789")
        assert get_response.status_code == 404

    def test_version_increments(self, client):
        """Version should increment on each save."""
        for expected_version in range(1, 5):
            response = client.post("/autosave", json={
                "entity_type": "counter",
                "entity_id": "counter-1",
                "data": {"count": expected_version},
                "version": expected_version - 1
            })

            assert response.json()["version"] == expected_version


# ============================================================================
# Feedback Widget Tests
# ============================================================================

class TestFeedbackSubmit:
    """Tests for feedback submission."""

    def test_submit_feedback(self, client):
        """Should submit feedback successfully."""
        response = client.post("/feedback", json={
            "type": "bug",
            "title": "Button not working",
            "description": "The submit button does not respond to clicks on mobile devices.",
            "priority": "high",
            "page_url": "/dashboard",
            "allow_contact": True
        })

        assert response.status_code == 201
        data = response.json()

        assert data["type"] == "bug"
        assert data["title"] == "Button not working"
        assert data["priority"] == "high"
        assert data["status"] == "new"

    def test_feedback_types(self, client):
        """Should accept all feedback types."""
        types = ["bug", "feature", "improvement", "question", "praise", "other"]

        for fb_type in types:
            response = client.post("/feedback", json={
                "type": fb_type,
                "title": f"Test {fb_type}",
                "description": "This is a test feedback for type " + fb_type,
            })
            assert response.status_code == 201
            assert response.json()["type"] == fb_type

    def test_feedback_priorities(self, client):
        """Should accept all priority levels."""
        priorities = ["low", "medium", "high", "critical"]

        for priority in priorities:
            response = client.post("/feedback", json={
                "type": "other",
                "title": f"Test {priority}",
                "description": "This is a test feedback for priority " + priority,
                "priority": priority
            })
            assert response.status_code == 201
            assert response.json()["priority"] == priority

    def test_feedback_too_short(self, client):
        """Should reject too short description."""
        response = client.post("/feedback", json={
            "type": "bug",
            "title": "Short",
            "description": "Too short"  # Less than 10 chars
        })
        assert response.status_code == 422


class TestFeedbackList:
    """Tests for feedback listing."""

    def test_list_feedback(self, client):
        """Should list submitted feedback."""
        # Submit some feedback
        for i in range(3):
            client.post("/feedback", json={
                "type": "feature",
                "title": f"Feature {i}",
                "description": f"Description for feature request number {i}",
            })

        response = client.get("/feedback")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 3
        assert len(data["feedback"]) == 3

    def test_filter_by_type(self, client):
        """Should filter by type."""
        # Submit different types
        client.post("/feedback", json={
            "type": "bug",
            "title": "A Bug",
            "description": "This is a bug report description",
        })
        client.post("/feedback", json={
            "type": "feature",
            "title": "A Feature",
            "description": "This is a feature request description",
        })

        response = client.get("/feedback?type=bug")
        data = response.json()

        assert data["total"] == 1
        assert data["feedback"][0]["type"] == "bug"

    def test_pagination(self, client):
        """Should paginate feedback."""
        # Submit 5 items
        for i in range(5):
            client.post("/feedback", json={
                "type": "other",
                "title": f"Item {i}",
                "description": f"Description for item number {i} here",
            })

        response = client.get("/feedback?limit=2&offset=0")
        data = response.json()

        assert len(data["feedback"]) == 2
        assert data["total"] == 5
        assert data["has_more"] is True

    def test_get_single_feedback(self, client):
        """Should get single feedback item."""
        create_response = client.post("/feedback", json={
            "type": "question",
            "title": "How to use API?",
            "description": "I need help understanding how to use the API properly.",
        })
        feedback_id = create_response.json()["id"]

        response = client.get(f"/feedback/{feedback_id}")
        assert response.status_code == 200
        assert response.json()["id"] == feedback_id

    def test_get_nonexistent_feedback(self, client):
        """Should return 404 for non-existent feedback."""
        response = client.get("/feedback/nonexistent")
        assert response.status_code == 404


# ============================================================================
# Accessibility Tests
# ============================================================================

class TestAccessibilityConfig:
    """Tests for accessibility configuration."""

    def test_get_default_config(self, client):
        """Should return default config."""
        response = client.get("/accessibility")
        assert response.status_code == 200

        data = response.json()
        assert data["high_contrast"] is False
        assert data["large_text"] is False
        assert data["reduce_motion"] is False
        assert data["keyboard_navigation"] is True
        assert data["font_size_scale"] == 1.0

    def test_update_config(self, client):
        """Should update config."""
        response = client.put("/accessibility", json={
            "high_contrast": True,
            "large_text": True,
            "reduce_motion": True,
            "screen_reader_optimized": True,
            "keyboard_navigation": True,
            "focus_indicators": True,
            "color_blind_mode": "protanopia",
            "font_size_scale": 1.5,
            "line_height_scale": 1.3,
            "letter_spacing": 0.05
        })

        assert response.status_code == 200
        data = response.json()

        assert data["high_contrast"] is True
        assert data["font_size_scale"] == 1.5
        assert data["color_blind_mode"] == "protanopia"

    def test_invalid_color_blind_mode(self, client):
        """Should reject invalid color blind mode."""
        response = client.put("/accessibility", json={
            "high_contrast": False,
            "large_text": False,
            "reduce_motion": False,
            "screen_reader_optimized": False,
            "keyboard_navigation": True,
            "focus_indicators": True,
            "color_blind_mode": "invalid",
            "font_size_scale": 1.0,
            "line_height_scale": 1.0,
            "letter_spacing": 0.0
        })

        assert response.status_code == 400

    def test_get_presets(self, client):
        """Should return accessibility presets."""
        response = client.get("/accessibility/presets")
        assert response.status_code == 200

        data = response.json()
        assert "default" in data
        assert "low_vision" in data
        assert "motor_impairment" in data
        assert "screen_reader" in data
        assert "dyslexia_friendly" in data

        # Verify preset structure
        assert data["low_vision"]["high_contrast"] is True
        assert data["low_vision"]["large_text"] is True


# ============================================================================
# UI State Tests
# ============================================================================

class TestUIState:
    """Tests for UI state persistence."""

    def test_get_default_state(self, client):
        """Should return default state."""
        response = client.get("/state")
        assert response.status_code == 200

        data = response.json()
        assert data["sidebar_collapsed"] is False
        assert data["active_theme"] == "system"
        assert data["table_density"] == "normal"
        assert data["tour_completed"] is False

    def test_update_state(self, client):
        """Should update state."""
        response = client.put("/state", json={
            "sidebar_collapsed": True,
            "active_theme": "dark",
            "table_density": "compact",
            "dashboard_layout": {"widgets": ["chart", "stats"]},
            "pinned_items": ["item-1", "item-2"],
            "recent_items": [],
            "tour_completed": True,
            "onboarding_step": 5
        })

        assert response.status_code == 200
        data = response.json()

        assert data["sidebar_collapsed"] is True
        assert data["active_theme"] == "dark"
        assert data["table_density"] == "compact"

    def test_invalid_theme(self, client):
        """Should reject invalid theme."""
        response = client.put("/state", json={
            "sidebar_collapsed": False,
            "active_theme": "invalid",
            "table_density": "normal",
            "pinned_items": [],
            "recent_items": [],
            "tour_completed": False,
            "onboarding_step": 0
        })

        assert response.status_code == 400
        assert "theme" in response.json()["detail"].lower()

    def test_invalid_density(self, client):
        """Should reject invalid density."""
        response = client.put("/state", json={
            "sidebar_collapsed": False,
            "active_theme": "system",
            "table_density": "invalid",
            "pinned_items": [],
            "recent_items": [],
            "tour_completed": False,
            "onboarding_step": 0
        })

        assert response.status_code == 400
        assert "density" in response.json()["detail"].lower()

    def test_patch_state(self, client):
        """Should partially update state."""
        # Set initial
        client.put("/state", json={
            "sidebar_collapsed": False,
            "active_theme": "light",
            "table_density": "normal",
            "pinned_items": [],
            "recent_items": [],
            "tour_completed": False,
            "onboarding_step": 0
        })

        # Patch
        response = client.patch("/state", json={
            "sidebar_collapsed": True
        })

        assert response.status_code == 200
        data = response.json()

        assert data["sidebar_collapsed"] is True
        assert data["active_theme"] == "light"  # Unchanged


class TestPinnedItems:
    """Tests for pinned items management."""

    def test_pin_item(self, client):
        """Should pin an item."""
        response = client.post("/state/pin/dashboard-chart")
        assert response.status_code == 204

        # Verify
        state_response = client.get("/state")
        assert "dashboard-chart" in state_response.json()["pinned_items"]

    def test_unpin_item(self, client):
        """Should unpin an item."""
        # Pin first
        client.post("/state/pin/to-unpin")

        # Unpin
        response = client.delete("/state/pin/to-unpin")
        assert response.status_code == 204

        # Verify
        state_response = client.get("/state")
        assert "to-unpin" not in state_response.json()["pinned_items"]

    def test_max_pinned_items(self, client):
        """Should limit pinned items to 10."""
        for i in range(15):
            client.post(f"/state/pin/item-{i}")

        state_response = client.get("/state")
        pinned = state_response.json()["pinned_items"]

        assert len(pinned) == 10
        # Should keep the most recent ones
        assert "item-14" in pinned
        assert "item-5" in pinned


class TestRecentItems:
    """Tests for recent items management."""

    def test_add_recent_item(self, client):
        """Should add recent item."""
        response = client.post("/state/recent/doc-123")
        assert response.status_code == 204

        # Verify
        state_response = client.get("/state")
        assert "doc-123" in state_response.json()["recent_items"]

    def test_recent_items_order(self, client):
        """Recent items should be in order (newest first)."""
        client.post("/state/recent/item-1")
        client.post("/state/recent/item-2")
        client.post("/state/recent/item-3")

        state_response = client.get("/state")
        recent = state_response.json()["recent_items"]

        assert recent[0] == "item-3"
        assert recent[1] == "item-2"
        assert recent[2] == "item-1"

    def test_duplicate_moves_to_front(self, client):
        """Adding existing item should move it to front."""
        client.post("/state/recent/item-1")
        client.post("/state/recent/item-2")
        client.post("/state/recent/item-1")  # Add again

        state_response = client.get("/state")
        recent = state_response.json()["recent_items"]

        assert recent[0] == "item-1"
        assert recent.count("item-1") == 1  # No duplicates

    def test_max_recent_items(self, client):
        """Should limit recent items to 20."""
        for i in range(25):
            client.post(f"/state/recent/item-{i}")

        state_response = client.get("/state")
        recent = state_response.json()["recent_items"]

        assert len(recent) == 20
        assert "item-24" in recent  # Most recent
        assert "item-0" not in recent  # Oldest removed


# ============================================================================
# Tenant Isolation Tests
# ============================================================================

class TestTenantIsolation:
    """Tests for tenant isolation."""

    def test_autosave_isolated(self):
        """Autosave data should be isolated per tenant."""
        app = FastAPI()
        app.include_router(router)

        # Create mock for tenant 1
        mock1 = MagicMock()
        mock1.tenant_id = "tenant-1"
        app.dependency_overrides[get_current_license] = lambda: mock1

        client1 = TestClient(app)
        client1.post("/autosave", json={
            "entity_type": "doc",
            "entity_id": "doc-1",
            "data": {"owner": "tenant-1"},
            "version": 0
        })

        # Create mock for tenant 2
        mock2 = MagicMock()
        mock2.tenant_id = "tenant-2"
        app.dependency_overrides[get_current_license] = lambda: mock2

        client2 = TestClient(app)
        # Should not find tenant-1's data
        response = client2.get("/autosave/doc/doc-1")
        assert response.status_code == 404

        app.dependency_overrides.clear()

    def test_feedback_isolated(self):
        """Feedback should be isolated per tenant."""
        app = FastAPI()
        app.include_router(router)

        # Create mock for tenant 1
        mock1 = MagicMock()
        mock1.tenant_id = "tenant-1"
        app.dependency_overrides[get_current_license] = lambda: mock1

        client1 = TestClient(app)
        client1.post("/feedback", json={
            "type": "bug",
            "title": "Tenant 1 Bug",
            "description": "This is tenant 1's bug report"
        })

        # Create mock for tenant 2
        mock2 = MagicMock()
        mock2.tenant_id = "tenant-2"
        app.dependency_overrides[get_current_license] = lambda: mock2

        client2 = TestClient(app)
        response = client2.get("/feedback")
        assert response.json()["total"] == 0

        app.dependency_overrides.clear()
