import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.core.security import get_current_license, LicenseInfo
from app.services.ai_gateway import ProviderAPIError


# Override dependency to skip DB lookup
async def mock_get_current_license():
    return LicenseInfo(
        license_key="test_license_key",
        license_uuid="test_license_uuid",
        tenant_id="test_tenant_id",
        app_id="test_app_id",
        credits_remaining=1000,
        is_active=True
    )


@pytest.fixture(autouse=True)
def setup_license_override():
    """Set up license override for all tests in this module."""
    app.dependency_overrides[get_current_license] = mock_get_current_license
    yield
    # Cleanup handled by conftest.py cleanup_dependency_overrides fixture


client = TestClient(app)

class TestIntegrationFlow:
    """
    Integration tests for the /v1/generate endpoint.
    Mocks external services (AI, Billing, Usage) but tests the full FastAPI flow.
    """

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.UsageService")
    def test_generate_flow_success(self, mock_usage, mock_billing, mock_provider_cls):
        """
        Test successful generation flow:
        Request -> Privacy -> Provider -> Billing -> Usage Log -> Response
        """
        # Mock AI Provider
        mock_provider_instance = mock_provider_cls.return_value
        mock_provider_instance.generate = AsyncMock(return_value=("Hello from AI", 15))
        
        # Mock Billing (Success)
        mock_billing.deduct_credits = AsyncMock(return_value=985)
        
        # Mock Usage (Success)
        mock_usage.log_usage = AsyncMock(return_value=None)
        
        payload = {"prompt": "Hello world", "provider": "anthropic"}
        headers = {"X-License-Key": "test_license_key"} # Header required by schema but overridden by dependency
        
        response = client.post("/api/v1/generate", json=payload, headers=headers)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Hello from AI"
        assert data["tokens_used"] == 15
        assert data["credits_deducted"] == 15
        assert data["pii_detected"] is False
        
        # Verify calls
        mock_provider_instance.generate.assert_called_once()
        # License key comes from the mock_get_current_license dependency
        mock_billing.deduct_credits.assert_called_once()
        mock_usage.log_usage.assert_called_once()
        
        # Verify Usage Log arguments
        args, kwargs = mock_usage.log_usage.call_args
        assert kwargs["credits_deducted"] == 15
        assert kwargs["tokens_used"] == 15
        assert kwargs["provider"] == "anthropic"

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.BillingService")
    @patch("app.api.v1.generate.UsageService")
    def test_generate_flow_pii_detected(self, mock_usage, mock_billing, mock_provider_cls):
        """Test flow when PII is detected."""
        mock_provider_instance = mock_provider_cls.return_value
        mock_provider_instance.generate = AsyncMock(return_value=("Sanitized Response", 10))
        mock_billing.deduct_credits = AsyncMock(return_value=990)
        mock_usage.log_usage = AsyncMock()

        # Prompt with email
        payload = {"prompt": "My email is test@example.com", "provider": "anthropic"}
        
        response = client.post("/api/v1/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["pii_detected"] is True
        
        # Verify provider received sanitized prompt
        # We need to check what generate was called with
        args, _ = mock_provider_instance.generate.call_args
        assert "<EMAIL_REMOVED>" in args[0]

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.BillingService")
    def test_generate_provider_error(self, mock_billing, mock_provider_cls):
        """Test handling of AI provider errors."""
        mock_provider_instance = mock_provider_cls.return_value
        mock_provider_instance.generate = AsyncMock(side_effect=ProviderAPIError("API Down"))

        payload = {"prompt": "Hello", "provider": "anthropic"}
        response = client.post("/api/v1/generate", json=payload)

        assert response.status_code == 500
        # SEC-010: 5xx errors show generic messages in production
        assert "detail" in response.json()

        # Billing should NOT be called
        mock_billing.deduct_credits.assert_not_called()

    @patch("app.api.v1.generate.AnthropicProvider")
    @patch("app.api.v1.generate.BillingService")
    def test_generate_billing_error(self, mock_billing, mock_provider_cls):
        """Test handling of insufficient credits."""
        mock_provider_instance = mock_provider_cls.return_value
        mock_provider_instance.generate = AsyncMock(return_value=("Expensive AI", 10000))

        # Mock Billing Error
        mock_billing.deduct_credits = AsyncMock(side_effect=HTTPException(status_code=402, detail="Insufficient credits"))

        payload = {"prompt": "Hello", "provider": "anthropic"}
        response = client.post("/api/v1/generate", json=payload)

        assert response.status_code == 402
        # SEC-010: Error messages are sanitized (402 not in exposed codes)
        assert "detail" in response.json()
