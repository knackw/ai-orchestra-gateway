"""
SEC-019: Tests for authentication logout endpoints.

Tests single-device and all-device logout functionality.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient


def test_logout_missing_authorization_header(client: TestClient):
    """
    Test that logout endpoint rejects requests without Authorization header.

    SEC-019: Authentication is required for logout.
    SEC-010: Error details are sanitized in production for security.
    """
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 401
    # SEC-010: In production, error details are sanitized to prevent info leakage
    detail = response.json().get("detail", "")
    # Accept either sanitized "Unauthorized" or detailed message
    assert "Unauthorized" in detail or "Missing Authorization header" in detail or "Authorization" in detail.lower()


def test_logout_invalid_authorization_format(client: TestClient):
    """
    Test that logout endpoint rejects malformed Authorization headers.

    SEC-010: Error details are sanitized in production for security.
    """
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "InvalidFormat token123"}
    )

    assert response.status_code == 401
    # SEC-010: In production, error details are sanitized
    detail = response.json().get("detail", "")
    assert "Unauthorized" in detail or "Invalid" in detail or "Authorization" in detail.lower()


def test_logout_empty_token(client: TestClient):
    """
    Test that logout endpoint rejects empty tokens.

    SEC-010: Error details are sanitized in production for security.
    """
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer "}
    )

    assert response.status_code == 401
    # SEC-010: In production, error details are sanitized
    detail = response.json().get("detail", "")
    assert "Unauthorized" in detail or "Empty token" in detail or "token" in detail.lower()


@patch("app.api.v1.auth.get_supabase_client")
def test_logout_invalid_token(mock_get_client, client: TestClient):
    """
    Test that logout endpoint rejects invalid/expired tokens.
    """
    # Mock Supabase client to return invalid user
    mock_client = MagicMock()
    mock_client.auth.get_user.return_value = MagicMock(user=None)
    mock_get_client.return_value = mock_client

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]


@patch("app.api.v1.auth.get_supabase_client")
def test_logout_success(mock_get_client, client: TestClient):
    """
    SEC-019: Test successful logout from current device.
    """
    # Mock Supabase client
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_client.auth.get_user.return_value = MagicMock(user=mock_user)
    mock_client.auth.sign_out.return_value = None
    mock_get_client.return_value = mock_client

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out from current device"
    assert data["sessions_invalidated"] == 1

    # Verify sign_out was called
    mock_client.auth.sign_out.assert_called_once()


@patch("app.api.v1.auth.get_supabase_client")
def test_logout_database_error(mock_get_client, client: TestClient):
    """
    Test error handling when database/Supabase fails during logout.
    """
    # Mock Supabase client to raise exception
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_client.auth.get_user.return_value = MagicMock(user=mock_user)
    mock_client.auth.sign_out.side_effect = Exception("Database connection failed")
    mock_get_client.return_value = mock_client

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 500
    # Error message may be sanitized by error handling middleware
    detail = response.json()["detail"]
    assert "Logout failed" in detail or "Internal Server Error" in detail


def test_logout_all_missing_authorization_header(client: TestClient):
    """
    Test that logout-all endpoint rejects requests without Authorization header.

    SEC-019: Authentication is required for global logout.
    SEC-010: Error details are sanitized in production for security.
    """
    response = client.post("/api/v1/auth/logout-all")

    assert response.status_code == 401
    # SEC-010: In production, error details are sanitized
    detail = response.json().get("detail", "")
    assert "Unauthorized" in detail or "Missing Authorization header" in detail or "Authorization" in detail.lower()


def test_logout_all_invalid_authorization_format(client: TestClient):
    """
    Test that logout-all endpoint rejects malformed Authorization headers.

    SEC-010: Error details are sanitized in production for security.
    """
    response = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": "InvalidFormat token123"}
    )

    assert response.status_code == 401
    # SEC-010: In production, error details are sanitized
    detail = response.json().get("detail", "")
    assert "Unauthorized" in detail or "Invalid" in detail or "Authorization" in detail.lower()


@patch("app.api.v1.auth.get_supabase_client")
def test_logout_all_invalid_token(mock_get_client, client: TestClient):
    """
    Test that logout-all endpoint rejects invalid/expired tokens.
    """
    # Mock Supabase client to return invalid user
    mock_client = MagicMock()
    mock_client.auth.get_user.return_value = MagicMock(user=None)
    mock_get_client.return_value = mock_client

    response = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]


@patch("app.api.v1.auth.get_supabase_client")
def test_logout_all_success_admin_method(mock_get_client, client: TestClient):
    """
    SEC-019: Test successful global logout using admin.sign_out method.

    This is the primary method for invalidating all sessions.
    """
    # Mock Supabase client with service role
    mock_client = MagicMock()

    # First call: get_user (with anon key)
    mock_user = MagicMock()
    mock_user.id = "test-user-123"

    # We need to handle two different client instances
    # First client for user validation (anon key)
    mock_anon_client = MagicMock()
    mock_anon_client.auth.get_user.return_value = MagicMock(user=mock_user)

    # Second client for admin operations (service role)
    mock_service_client = MagicMock()
    mock_admin = MagicMock()
    mock_admin.sign_out.return_value = None
    mock_service_client.auth.admin = mock_admin

    # Mock get_supabase_client to return different clients based on use_service_role
    def get_client_side_effect(use_service_role=False):
        if use_service_role:
            return mock_service_client
        return mock_anon_client

    mock_get_client.side_effect = get_client_side_effect

    response = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out from all devices"
    assert data["sessions_invalidated"] == -1  # -1 indicates all sessions

    # Verify admin.sign_out was called with user ID
    mock_admin.sign_out.assert_called_once_with("test-user-123")


@patch("app.api.v1.auth.get_supabase_client")
def test_logout_all_fallback_rpc_method(mock_get_client, client: TestClient):
    """
    SEC-019: Test global logout fallback to RPC method.

    When admin.sign_out is not available, fallback to RPC function.
    """
    # Mock Supabase client
    mock_anon_client = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_anon_client.auth.get_user.return_value = MagicMock(user=mock_user)

    # Service role client - simulate admin.sign_out raising AttributeError
    mock_service_client = MagicMock()
    mock_admin = MagicMock()
    mock_admin.sign_out.side_effect = AttributeError("sign_out not available")
    mock_service_client.auth.admin = mock_admin

    # Mock RPC call
    mock_rpc_result = MagicMock()
    mock_rpc_result.execute.return_value = None
    mock_service_client.rpc.return_value = mock_rpc_result

    def get_client_side_effect(use_service_role=False):
        if use_service_role:
            return mock_service_client
        return mock_anon_client

    mock_get_client.side_effect = get_client_side_effect

    response = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out from all devices"
    assert data["sessions_invalidated"] == -1

    # Verify RPC was called
    mock_service_client.rpc.assert_called_once_with(
        'invalidate_all_user_sessions',
        {'target_user_id': 'test-user-123'}
    )


@patch("app.api.v1.auth.get_supabase_client")
def test_logout_all_database_error(mock_get_client, client: TestClient):
    """
    Test error handling when database/Supabase fails during global logout.
    """
    # Mock Supabase client
    mock_anon_client = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_anon_client.auth.get_user.return_value = MagicMock(user=mock_user)

    # Service role client that raises exception
    mock_service_client = MagicMock()
    mock_admin = MagicMock()
    mock_admin.sign_out.side_effect = Exception("Database connection failed")
    mock_service_client.auth.admin = mock_admin

    def get_client_side_effect(use_service_role=False):
        if use_service_role:
            return mock_service_client
        return mock_anon_client

    mock_get_client.side_effect = get_client_side_effect

    response = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": "Bearer valid-token"}
    )

    assert response.status_code == 500
    # Error message may be sanitized by error handling middleware
    detail = response.json()["detail"]
    assert "Global logout failed" in detail or "Internal Server Error" in detail


# Note: client fixture is provided by conftest.py


# Integration-style tests (optional, for when Supabase test environment is available)

@pytest.mark.skip(reason="Requires Supabase test environment")
def test_logout_integration():
    """
    Integration test for logout with real Supabase instance.

    This test is skipped by default and should only be run
    when a test Supabase environment is configured.
    """
    # TODO: Implement integration test with test Supabase instance
    pass


@pytest.mark.skip(reason="Requires Supabase test environment")
def test_logout_all_integration():
    """
    Integration test for logout-all with real Supabase instance.

    This test is skipped by default and should only be run
    when a test Supabase environment is configured.
    """
    # TODO: Implement integration test with test Supabase instance
    pass


# Security tests

def test_logout_csrf_not_required(client: TestClient):
    """
    Test that logout endpoints don't require CSRF token.

    Logout endpoints use Bearer token authentication, not session cookies,
    so CSRF protection is not needed.
    """
    with patch("app.api.v1.auth.get_supabase_client") as mock_get_client:
        mock_client = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_client.auth.get_user.return_value = MagicMock(user=mock_user)
        mock_client.auth.sign_out.return_value = None
        mock_get_client.return_value = mock_client

        # Make request without CSRF token
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer valid-token"}
        )

        # Should succeed (CSRF not required for token-based auth)
        assert response.status_code == 200


def test_logout_rate_limiting():
    """
    Test that logout endpoints have appropriate rate limiting.

    Note: This test checks that rate limiting doesn't block normal usage.
    Excessive logout attempts should be rare in production.
    """
    from app.main import app
    client = TestClient(app)

    with patch("app.api.v1.auth.get_supabase_client") as mock_get_client:
        mock_client = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_client.auth.get_user.return_value = MagicMock(user=mock_user)
        mock_client.auth.sign_out.return_value = None
        mock_get_client.return_value = mock_client

        # Make 5 logout requests
        for i in range(5):
            response = client.post(
                "/api/v1/auth/logout",
                headers={"Authorization": f"Bearer valid-token-{i}"}
            )

            # All should succeed (rate limits should be reasonable)
            assert response.status_code == 200


def test_logout_all_requires_different_permissions(client: TestClient):
    """
    Test that logout-all uses service role for admin operations.

    This ensures proper permission escalation for global logout.
    """
    with patch("app.api.v1.auth.get_supabase_client") as mock_get_client:
        mock_anon_client = MagicMock()
        mock_service_client = MagicMock()

        mock_user = MagicMock()
        mock_user.id = "test-user-123"
        mock_anon_client.auth.get_user.return_value = MagicMock(user=mock_user)

        mock_admin = MagicMock()
        mock_admin.sign_out.return_value = None
        mock_service_client.auth.admin = mock_admin

        def get_client_side_effect(use_service_role=False):
            if use_service_role:
                return mock_service_client
            return mock_anon_client

        mock_get_client.side_effect = get_client_side_effect

        response = client.post(
            "/api/v1/auth/logout-all",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200

        # Verify service role client was requested
        assert mock_get_client.call_count == 2  # Once for auth, once for admin
        mock_get_client.assert_any_call(use_service_role=True)
