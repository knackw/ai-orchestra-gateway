"""
Pytest configuration and shared fixtures.

Sets up testing environment with proper configuration.
"""

import os
import pytest

# Set testing environment BEFORE importing app modules
os.environ["TESTING"] = "true"
os.environ["REDIS_URL"] = ""  # Force memory storage for rate limiting


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment variables before any tests run.

    This fixture runs once per test session and ensures
    all tests use in-memory rate limiting instead of Redis.
    """
    # Already set above, but ensure they're set
    os.environ["TESTING"] = "true"
    os.environ["REDIS_URL"] = ""

    yield

    # Cleanup (optional)
    pass


@pytest.fixture
def mock_supabase_client():
    """
    Create a mock Supabase client for testing.

    This can be used to mock database operations in tests.
    """
    from unittest.mock import MagicMock, AsyncMock

    client = MagicMock()
    client.table = MagicMock(return_value=client)
    client.select = MagicMock(return_value=client)
    client.insert = MagicMock(return_value=client)
    client.update = MagicMock(return_value=client)
    client.delete = MagicMock(return_value=client)
    client.eq = MagicMock(return_value=client)
    client.single = MagicMock(return_value=client)
    client.execute = MagicMock(return_value=MagicMock(data=[]))

    return client


@pytest.fixture
def mock_license_info():
    """
    Create a mock LicenseInfo object for testing authenticated endpoints.
    """
    from unittest.mock import MagicMock

    license_info = MagicMock()
    license_info.license_key = "test-license-key"
    license_info.license_uuid = "test-license-uuid"
    license_info.tenant_id = "test-tenant-id"
    license_info.app_id = "test-app-id"
    license_info.credits_remaining = 1000
    license_info.is_active = True
    license_info.expires_at = None

    return license_info


@pytest.fixture
def client():
    """
    Create a TestClient for the FastAPI application.

    This fixture provides a shared test client for all tests.
    """
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    """
    Clean up FastAPI dependency overrides after each test.

    This ensures test isolation by clearing any dependency overrides
    that were set during a test, preventing state pollution.
    """
    from app.main import app

    # Store original overrides
    original_overrides = dict(app.dependency_overrides)

    yield

    # Restore original overrides after test
    app.dependency_overrides = original_overrides
