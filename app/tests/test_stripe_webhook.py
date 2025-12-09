import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.api.webhooks import stripe as stripe_webhook
from app.core import config

client = TestClient(app)

# Override config dependencies
def get_settings_override():
    return config.Settings(
        SUPABASE_URL="http://test-supabase-url",
        SUPABASE_KEY="test-supabase-key",
        SUPABASE_SERVICE_ROLE_KEY="test-service-role-key",
        ANTHROPIC_API_KEY="test-anthropic-key",
        STRIPE_SECRET_KEY="test-stripe-secret",
        STRIPE_WEBHOOK_SECRET="test-webhook-secret"
    )

@pytest.fixture
def mock_settings():
    with patch("app.api.webhooks.stripe.settings", get_settings_override()):
        yield

class TestStripeWebhook:
    
    @patch("stripe.Webhook.construct_event")
    @patch("app.services.billing.BillingService.add_credits")
    def test_checkout_completed_success(self, mock_add_credits, mock_construct_event, mock_settings):
        """Test successful checkout session completion adds credits."""
        # Mock Stripe event
        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "sess_123",
                    "client_reference_id": "lic_test123",
                    "metadata": {"credits": "1000"}
                }
            }
        }
        mock_construct_event.return_value = mock_event
        mock_add_credits.return_value = None  # Success
        
        headers = {"Stripe-Signature": "t=123,v1=signature"}
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=b"payload",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"DEBUG Response: {response.json()}")

        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        
        mock_add_credits.assert_called_once_with("lic_test123", 1000)

    @patch("stripe.Webhook.construct_event")
    @patch("app.services.billing.BillingService.add_credits")
    def test_checkout_completed_no_credits(self, mock_add_credits, mock_construct_event, mock_settings):
        """Test checkout session without credits metadata does nothing."""
        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "sess_123",
                    "client_reference_id": "lic_test123",
                    "metadata": {}  # No credits info
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        headers = {"Stripe-Signature": "t=123,v1=signature"}
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=b"payload",
            headers=headers
        )
        
        # Should still return success to tell Stripe we received it
        assert response.status_code == 200
        mock_add_credits.assert_not_called()

    @patch("stripe.Webhook.construct_event")
    def test_invalid_signature_returns_400(self, mock_construct_event, mock_settings):
        """Test that invalid signature raises 400."""
        import stripe
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid sig", "sig_header")
        
        headers = {"Stripe-Signature": "invalid"}
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=b"payload",
            headers=headers
        )
        
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]

    @patch("stripe.Webhook.construct_event")
    def test_invalid_payload_returns_400(self, mock_construct_event, mock_settings):
        """Test that invalid payload raises 400."""
        mock_construct_event.side_effect = ValueError("Invalid payload")
        
        headers = {"Stripe-Signature": "t=123,v1=signature"}
        response = client.post(
            "/api/v1/webhooks/stripe",
            content=b"payload",
            headers=headers
        )
        
        assert response.status_code == 400
        assert "Invalid payload" in response.json()["detail"]
