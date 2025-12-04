"""
Unit tests for /v1/generate endpoint (with API key validation).
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.security import LicenseInfo, get_current_license
from app.main import app


# Create mock license for dependency override
def get_mock_license():
    """Mock license dependency for testing."""
    return LicenseInfo(
        license_key="lic_test123",
        tenant_id="tenant-mock-123",
        credits_remaining=1000,
        is_active=True,
        expires_at=None,
    )


# Override dependency for all tests
app.dependency_overrides[get_current_license] = get_mock_license

client = TestClient(app)


class TestGenerateEndpoint:
    """Tests for /v1/generate endpoint."""

    def test_endpoint_exists(self):
        """Test that /v1/generate endpoint exists."""
        response = client.options("/v1/generate")
        assert response.status_code in [200, 405]

    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_successful_generation(self, mock_shield, mock_provider, mock_billing):
        """Test successful AI generation."""
        mock_shield.sanitize.return_value = ("sanitized prompt", False)

        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Generated response", 127)
        mock_provider.return_value = mock_instance
        mock_billing.deduct_credits = AsyncMock(return_value=450)

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Write a professional email"},
        )

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

    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_generation_with_pii_detected(self, mock_shield, mock_provider, mock_billing):
        """Test generation when PII is detected."""
        mock_shield.sanitize.return_value = (
            "Email <EMAIL_REMOVED> about meeting",
            True,
        )

        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Response about meeting", 95)
        mock_provider.return_value = mock_instance
        mock_billing.deduct_credits = AsyncMock(return_value=400)

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Email john@example.com about meeting"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["pii_detected"] is True
        assert data["tokens_used"] == 95
        assert data["credits_deducted"] == 95

    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_credits_equal_tokens(self, mock_shield, mock_provider, mock_billing):
        """Test that credits_deducted equals tokens_used (MVP 1:1)."""
        mock_shield.sanitize.return_value = ("prompt", False)

        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("response", 250)
        mock_provider.return_value = mock_instance
        mock_billing.deduct_credits = AsyncMock(return_value=250)

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Test"},
        )

        data = response.json()
        assert data["tokens_used"] == 250
        assert data["credits_deducted"] == 250


class TestGenerateValidation:
    """Tests for request validation."""

    def test_empty_prompt_rejected(self):
        """Test that empty prompt is rejected."""
        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": ""},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_missing_prompt_rejected(self):
        """Test that missing prompt is rejected."""
        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={},
        )

        assert response.status_code == 422

    def test_prompt_too_long_rejected(self):
        """Test that prompt exceeding max length is rejected."""
        long_prompt = "a" * 10001

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": long_prompt},
        )

        assert response.status_code == 422


class TestGenerateAuthentication:
    """Tests for authentication (header validation)."""

    def test_missing_license_header_rejected(self):
        """Test that missing X-License-Key header is rejected."""
        # Temporarily remove override to test auth
        app.dependency_overrides.pop(get_current_license, None)

        response = client.post(
            "/v1/generate", json={"prompt": "Test prompt"}
        )

        assert response.status_code == 401

        # Restore override
        app.dependency_overrides[get_current_license] = get_mock_license

    def test_empty_license_header_rejected(self):
        """Test that empty X-License-Key header is rejected."""
        # Temporarily remove override
        app.dependency_overrides.pop(get_current_license, None)

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": ""},
            json={"prompt": "Test"},
        )

        assert response.status_code == 401

        # Restore override
        app.dependency_overrides[get_current_license] = get_mock_license


class TestGenerateErrorHandling:
    """Tests for error handling."""

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_ai_provider_error_returns_500(self, mock_shield, mock_provider):
        """Test that AI provider errors return 500."""
        from app.services.ai_gateway import ProviderAPIError

        mock_shield.sanitize.return_value = ("prompt", False)

        mock_instance = AsyncMock()
        mock_instance.generate.side_effect = ProviderAPIError("API error")
        mock_provider.return_value = mock_instance

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Test"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "generation failed" in data["detail"].lower()

    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_unexpected_error_returns_500(self, mock_shield):
        """Test that unexpected errors return 500."""
        mock_shield.sanitize.side_effect = Exception("Unexpected error")

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Test"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data




class TestProviderSelection:
    """Tests for provider parameter."""

    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.ScalewayProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_scaleway_provider_selection(self, mock_shield, mock_scaleway, mock_billing):
        """Test generation with Scaleway provider."""
        mock_shield.sanitize.return_value = ("sanitized prompt", False)

        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Scaleway response", 80)
        mock_scaleway.return_value = mock_instance
        mock_billing.deduct_credits = AsyncMock(return_value=420)

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Test", "provider": "scaleway"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Scaleway response"
        assert data["tokens_used"] == 80

    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.DataPrivacyShield")
    def test_anthropic_provider_default(self, mock_shield, mock_anthropic, mock_billing):
        """Test that Anthropic is used by default."""
        mock_shield.sanitize.return_value = ("prompt", False)

        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Anthropic response", 100)
        mock_anthropic.return_value = mock_instance
        mock_billing.deduct_credits = AsyncMock(return_value=400)

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Test"},  # No provider specified
        )

        assert response.status_code == 200
        mock_anthropic.assert_called_once()

    def test_invalid_provider_rejected(self):
        """Test that invalid provider is rejected."""
        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Test", "provider": "invalid"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid provider" in data["detail"]


class TestGenerateIntegration:
    """Integration tests with real components."""

    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.AnthropicProvider")
    def test_real_privacy_shield_integration(self, mock_provider, mock_billing):
        """Test with real DataPrivacyShield (not mocked)."""
        mock_instance = AsyncMock()
        mock_instance.generate.return_value = ("Sanitized response", 100)
        mock_provider.return_value = mock_instance
        mock_billing.deduct_credits = AsyncMock(return_value=400)

        response = client.post(
            "/v1/generate",
            headers={"X-License-Key": "lic_test123"},
            json={"prompt": "Contact me at user@example.com or +49 123 456789"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["pii_detected"] is True

        mock_instance.generate.assert_called_once()
        call_args = mock_instance.generate.call_args[0][0]

        assert "user@example.com" not in call_args
        assert "+49 123 456789" not in call_args
        assert "<EMAIL_REMOVED>" in call_args
        assert "<PHONE_REMOVED>" in call_args
