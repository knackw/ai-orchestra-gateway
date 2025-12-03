"""
Unit tests for /v1/generate endpoint.
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestGenerateEndpoint:
    """Tests for /v1/generate endpoint."""

    def test_endpoint_exists(self):
        """Test that /v1/generate endpoint exists."""
        # OPTIONS request to check endpoint
        response = client.options("/v1/generate")
        assert response.status_code in [200, 405]  # 405 if OPTIONS not allowed

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_successful_generation(self, mock_shield, mock_provider):
        """Test successful AI generation."""
        # Mock DataPrivacyShield
        mock_shield.sanitize.return_value = ("sanitized prompt", False)

        # Mock AnthropicProvider
        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Generated response", 127)
        mock_provider.return_value = mock_instance

        # Make request
        response = client.post(
            "/v1/generate",
            json={
                "prompt": "Write a professional email",
                "license_key": "lic_test123",
            },
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert "content" in data
        assert "tokens_used" in data
        assert "credits_deducted" in data
        assert "pii_detected" in data

        assert data["content"] == "Generated response"
        assert data["tokens_used"] == 127
        assert data["credits_deducted"] == 127
        assert data["pii_detected"] is False

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_generation_with_pii_detected(self, mock_shield, mock_provider):
        """Test generation when PII is detected."""
        # Mock DataPrivacyShield - PII found
        mock_shield.sanitize.return_value = (
            "Email <EMAIL_REMOVED> about meeting",
            True,
        )

        # Mock AnthropicProvider
        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Response about meeting", 95)
        mock_provider.return_value = mock_instance

        # Make request with PII
        response = client.post(
            "/v1/generate",
            json={
                "prompt": "Email john@example.com about meeting",
                "license_key": "lic_test",
            },
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["pii_detected"] is True
        assert data["tokens_used"] == 95
        assert data["credits_deducted"] == 95

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_credits_equal_tokens(self, mock_shield, mock_provider):
        """Test that credits_deducted equals tokens_used (MVP 1:1)."""
        mock_shield.sanitize.return_value = ("prompt", False)

        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("response", 250)
        mock_provider.return_value = mock_instance

        response = client.post(
            "/v1/generate",
            json={"prompt": "Test", "license_key": "lic_test"},
        )

        data = response.json()
        assert data["tokens_used"] == 250
        assert data["credits_deducted"] == 250  # 1:1 ratio


class TestGenerateValidation:
    """Tests for request validation."""

    def test_empty_prompt_rejected(self):
        """Test that empty prompt is rejected."""
        response = client.post(
            "/v1/generate",
            json={"prompt": "", "license_key": "lic_test"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_missing_prompt_rejected(self):
        """Test that missing prompt is rejected."""
        response = client.post(
            "/v1/generate", json={"license_key": "lic_test"}
        )

        assert response.status_code == 422

    def test_missing_license_key_rejected(self):
        """Test that missing license_key is rejected."""
        response = client.post(
            "/v1/generate", json={"prompt": "Test prompt"}
        )

        assert response.status_code == 422

    def test_empty_license_key_rejected(self):
        """Test that empty license_key is rejected."""
        response = client.post(
            "/v1/generate", json={"prompt": "Test", "license_key": ""}
        )

        assert response.status_code == 422

    def test_prompt_too_long_rejected(self):
        """Test that prompt exceeding max length is rejected."""
        long_prompt = "a" * 10001  # Max is 10000

        response = client.post(
            "/v1/generate",
            json={"prompt": long_prompt, "license_key": "lic_test"},
        )

        assert response.status_code == 422


class TestGenerateErrorHandling:
    """Tests for error handling."""

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_ai_provider_error_returns_500(self, mock_shield, mock_provider):
        """Test that AI provider errors return 500."""
        from app.services.ai_gateway import ProviderAPIError

        mock_shield.sanitize.return_value = ("prompt", False)

        # Mock provider to raise error
        mock_instance = AsyncMock()
        mock_instance.generate.side_effect = ProviderAPIError(
            "API error"
        )
        mock_provider.return_value = mock_instance

        response = client.post(
            "/v1/generate",
            json={"prompt": "Test", "license_key": "lic_test"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "generation failed" in data["detail"].lower()

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_unexpected_error_returns_500(self, mock_shield, mock_provider):
        """Test that unexpected errors return 500."""
        mock_shield.sanitize.side_effect = Exception("Unexpected error")

        response = client.post(
            "/v1/generate",
            json={"prompt": "Test", "license_key": "lic_test"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestGenerateIntegration:
    """Integration tests with real components."""

    @patch("app.api.v1.generate.AnthropicProvider")
    def test_real_privacy_shield_integration(self, mock_provider):
        """Test with real DataPrivacyShield (not mocked)."""
        # Mock only the provider
        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Sanitized response", 100)
        mock_provider.return_value = mock_instance

        # Request with PII
        response = client.post(
            "/v1/generate",
            json={
                "prompt": "Contact me at user@example.com or +49 123 456789",
                "license_key": "lic_test",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Privacy shield should detect PII
        assert data["pii_detected"] is True

        # Verify sanitized prompt was sent to provider
        mock_instance.generate.assert_called_once()
        call_args = mock_instance.generate.call_args[0][0]

        # Email and phone should be removed
        assert "user@example.com" not in call_args
        assert "+49 123 456789" not in call_args
        assert "<EMAIL_REMOVED>" in call_args
        assert "<PHONE_REMOVED>" in call_args
