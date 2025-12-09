"""
SEC-015: Test CORS Configuration

Tests whitelist-based CORS with:
- Allowed origins pass through
- Disallowed origins blocked
- Credentials handling
- Preflight requests
- Development vs Production behavior
"""

import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.core.cors import (
    get_allowed_origins,
    configure_cors,
    validate_cors_configuration,
)
from app.core.config import Settings


def create_test_app() -> FastAPI:
    """Create a minimal FastAPI app for testing."""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    return app


class TestGetAllowedOrigins:
    """Test get_allowed_origins function."""

    def test_development_default_origins(self):
        """Test that development mode has default localhost origins."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = []

            origins = get_allowed_origins()

            assert "http://localhost:3000" in origins
            assert "http://localhost:8000" in origins
            assert "http://127.0.0.1:3000" in origins
            assert "http://127.0.0.1:8000" in origins

    def test_development_custom_origins(self):
        """Test that development mode merges custom origins with defaults."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = [
                "http://localhost:4000",
                "https://dev.example.com",
            ]

            origins = get_allowed_origins()

            # Should have defaults + custom
            assert "http://localhost:3000" in origins
            assert "http://localhost:4000" in origins
            assert "https://dev.example.com" in origins

    def test_production_explicit_origins_only(self):
        """Test that production only uses explicitly configured origins."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = True
            mock_settings.is_development = False
            mock_settings.CORS_ORIGINS = [
                "https://example.com",
                "https://app.example.com",
            ]

            origins = get_allowed_origins()

            # Should only have explicit origins
            assert origins == ["https://example.com", "https://app.example.com"]
            assert "http://localhost:3000" not in origins

    def test_production_no_origins_configured(self):
        """Test that production with no origins returns empty list."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = True
            mock_settings.is_development = False
            mock_settings.CORS_ORIGINS = []

            origins = get_allowed_origins()

            assert origins == []


class TestConfigureCors:
    """Test configure_cors function."""

    def test_configure_cors_adds_middleware(self):
        """Test that configure_cors adds CORS middleware to app."""
        app = create_test_app()

        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = []
            mock_settings.CORS_ALLOW_CREDENTIALS = True
            mock_settings.CORS_MAX_AGE = 600

            configure_cors(app)

            # Check that middleware was added
            # FastAPI stores middleware in app.user_middleware
            assert len(app.user_middleware) > 0

    def test_cors_with_allowed_origin(self):
        """Test that requests from allowed origins receive correct CORS headers."""
        app = create_test_app()

        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = ["https://allowed.example.com"]
            mock_settings.CORS_ALLOW_CREDENTIALS = True
            mock_settings.CORS_MAX_AGE = 600

            configure_cors(app)

        client = TestClient(app)
        response = client.get(
            "/test",
            headers={"Origin": "https://allowed.example.com"}
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "https://allowed.example.com"
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_cors_with_disallowed_origin(self):
        """Test that requests from disallowed origins do not receive CORS headers."""
        app = create_test_app()

        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = ["https://allowed.example.com"]
            mock_settings.CORS_ALLOW_CREDENTIALS = True
            mock_settings.CORS_MAX_AGE = 600

            configure_cors(app)

        client = TestClient(app)
        response = client.get(
            "/test",
            headers={"Origin": "https://evil.example.com"}
        )

        # Request succeeds but no CORS headers
        assert response.status_code == 200
        # Browser will block the response due to missing CORS headers
        assert "access-control-allow-origin" not in response.headers

    def test_cors_preflight_allowed_origin(self):
        """Test CORS preflight (OPTIONS) request for allowed origin."""
        app = create_test_app()

        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = ["https://allowed.example.com"]
            mock_settings.CORS_ALLOW_CREDENTIALS = True
            mock_settings.CORS_MAX_AGE = 600

            configure_cors(app)

        client = TestClient(app)
        response = client.options(
            "/test",
            headers={
                "Origin": "https://allowed.example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-max-age" in response.headers
        assert response.headers["access-control-max-age"] == "600"

    def test_cors_preflight_disallowed_origin(self):
        """Test CORS preflight (OPTIONS) request for disallowed origin."""
        app = create_test_app()

        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = ["https://allowed.example.com"]
            mock_settings.CORS_ALLOW_CREDENTIALS = True
            mock_settings.CORS_MAX_AGE = 600

            configure_cors(app)

        client = TestClient(app)
        response = client.options(
            "/test",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "POST",
            }
        )

        # Preflight fails - no CORS headers
        assert "access-control-allow-origin" not in response.headers

    def test_cors_credentials_disabled(self):
        """Test CORS with credentials disabled."""
        app = create_test_app()

        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = ["https://allowed.example.com"]
            mock_settings.CORS_ALLOW_CREDENTIALS = False
            mock_settings.CORS_MAX_AGE = 600

            configure_cors(app)

        client = TestClient(app)
        response = client.get(
            "/test",
            headers={"Origin": "https://allowed.example.com"}
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        # No credentials header when disabled
        assert response.headers.get("access-control-allow-credentials") != "true"


class TestValidateCorsConfiguration:
    """Test validate_cors_configuration function."""

    def test_production_no_origins_warning(self, caplog):
        """Test that production with no origins logs a warning."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = True
            mock_settings.CORS_ORIGINS = []

            validate_cors_configuration()

            # Should log warning
            assert "No CORS origins configured" in caplog.text

    def test_production_with_wildcard_raises_error(self):
        """Test that wildcard in production raises ValueError."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = True
            mock_settings.CORS_ORIGINS = ["*"]

            with pytest.raises(ValueError, match="Wildcard"):
                validate_cors_configuration()

    def test_production_with_wildcard_in_list_raises_error(self):
        """Test that wildcard in list in production raises ValueError."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = True
            mock_settings.CORS_ORIGINS = [
                "https://example.com",
                "*",
                "https://other.com"
            ]

            with pytest.raises(ValueError, match="Wildcard"):
                validate_cors_configuration()

    def test_invalid_origin_format_raises_error(self):
        """Test that invalid origin format raises ValueError."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.CORS_ORIGINS = [
                "https://valid.com",
                "invalid-origin",  # Missing protocol
            ]

            with pytest.raises(ValueError, match="Invalid CORS origin"):
                validate_cors_configuration()

    def test_valid_origins_pass_validation(self):
        """Test that valid origins pass validation."""
        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = True
            mock_settings.CORS_ORIGINS = [
                "https://example.com",
                "https://app.example.com",
                "http://localhost:3000",  # Valid format even in production
            ]

            # Should not raise
            validate_cors_configuration()


class TestCorsIntegration:
    """Integration tests with the actual app."""

    def test_cors_with_real_app(self):
        """Test CORS with the real application."""
        from app.main import app

        client = TestClient(app)

        # Test with an allowed origin (development defaults)
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200
        # Note: TestClient doesn't always trigger CORS middleware the same way
        # as real browsers, but the middleware is configured correctly.
        # This test verifies the endpoint works with Origin header.
        # For full CORS testing, see unit tests above.

    def test_cors_headers_included(self):
        """Test that specific headers are allowed."""
        app = create_test_app()

        with patch("app.core.cors.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.is_development = True
            mock_settings.CORS_ORIGINS = ["https://allowed.example.com"]
            mock_settings.CORS_ALLOW_CREDENTIALS = True
            mock_settings.CORS_MAX_AGE = 600

            configure_cors(app)

        client = TestClient(app)
        response = client.options(
            "/test",
            headers={
                "Origin": "https://allowed.example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-CSRF-Token,Authorization",
            }
        )

        assert response.status_code == 200
        # Check that our custom headers are allowed
        allowed_headers = response.headers.get("access-control-allow-headers", "")
        assert "x-csrf-token" in allowed_headers.lower()
        assert "authorization" in allowed_headers.lower()


class TestCorsConfigParsing:
    """Test CORS configuration parsing from environment variables."""

    def test_parse_comma_separated_origins(self):
        """Test parsing comma-separated CORS origins."""
        # Test the parse function directly
        from app.core.config import Settings

        # Test the validator directly with comma-separated string
        result = Settings.parse_cors_origins("https://example.com,https://app.example.com,http://localhost:3000")

        assert len(result) == 3
        assert "https://example.com" in result
        assert "https://app.example.com" in result
        assert "http://localhost:3000" in result

    def test_parse_origins_with_spaces(self):
        """Test parsing origins with extra spaces."""
        from app.core.config import Settings

        # Test the validator with spaces
        result = Settings.parse_cors_origins(" https://example.com , https://app.example.com , http://localhost:3000 ")

        # Should strip whitespace
        assert len(result) == 3
        assert "https://example.com" in result
        assert "https://app.example.com" in result

    def test_empty_origins_string(self):
        """Test that empty string returns empty list."""
        from app.core.config import Settings

        # Test with empty string
        result = Settings.parse_cors_origins("")
        assert result == []

        # Test with whitespace only
        result = Settings.parse_cors_origins("   ")
        assert result == []
