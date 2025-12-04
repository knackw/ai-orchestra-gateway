"""
Script to add Scaleway provider tests to test_generate.py
"""

# Read test file
with open('app/tests/test_generate.py', 'r') as f:
    content = f.read()

# Add new test class before the last class
new_tests = '''

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


'''

# Find insertion point (before last class)
insertion_point = content.rfind("class TestGenerateIntegration:")

if insertion_point != -1:
    # Insert new tests
    content = content[:insertion_point] + new_tests + content[insertion_point:]
    
    # Write back
    with open('app/tests/test_generate.py', 'w') as f:
        f.write(content)
    
    print("✅ Added provider selection tests to test_generate.py")
else:
    print("⚠️ Could not find insertion point")
