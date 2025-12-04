"""
Script to update test_generate.py with BillingService mocks.
"""

# Read test file
with open('app/tests/test_generate.py', 'r') as f:
    content = f.read()

# Replace pattern patches without billing
replacements = [
    (
        '    @patch("app.api.v1.generate.AnthropicProvider")\n    @patch("app.api.v1.generate.DataPrivacyShield")\n    def test_successful_generation(self, mock_shield, mock_provider):',
        '    @patch("app.api.v1.generate.BillingService")\n    @patch("app.api.v1.generate.AnthropicProvider")\n    @patch("app.api.v1.generate.DataPrivacyShield")\n    def test_successful_generation(self, mock_shield, mock_provider, mock_billing):'
    ),
   (
        '        mock_instance.generate.return_value = ("Generated response", 127)\n        mock_provider.return_value = mock_instance\n\n        response = client.post(',
        '        mock_instance.generate.return_value = ("Generated response", 127)\n        mock_provider.return_value = mock_instance\n        mock_billing.deduct_credits = AsyncMock(return_value=450)\n\n        response = client.post('
    ),
    (
        '    @patch("app.api.v1.generate.AnthropicProvider")\n    @patch("app.api.v1.generate.DataPrivacyShield")\n    def test_generation_with_pii_detected(self, mock_shield, mock_provider):',
        '    @patch("app.api.v1.generate.BillingService")\n    @patch("app.api.v1.generate.AnthropicProvider")\n    @patch("app.api.v1.generate.DataPrivacyShield")\n    def test_generation_with_pii_detected(self, mock_shield, mock_provider, mock_billing):'
    ),
    (
        '        mock_instance.generate.return_value = ("Response about meeting", 95)\n        mock_provider.return_value = mock_instance\n\n        response = client.post(\n            "/v1/generate",',
        '        mock_instance.generate.return_value = ("Response about meeting", 95)\n        mock_provider.return_value = mock_instance\n        mock_billing.deduct_credits = AsyncMock(return_value=400)\n\n        response = client.post(\n            "/v1/generate",'
    ),
    (
        '    @patch("app.api.v1.generate.AnthropicProvider")\n    @patch("app.api.v1.generate.DataPrivacyShield")\n    def test_credits_equal_tokens(self, mock_shield, mock_provider):',
        '    @patch("app.api.v1.generate.BillingService")\n    @patch("app.api.v1.generate.AnthropicProvider")\n    @patch("app.api.v1.generate.DataPrivacyShield")\n    def test_credits_equal_tokens(self, mock_shield, mock_provider, mock_billing):'
    ),
    (
        '        mock_instance.generate.return_value = ("response", 250)\n        mock_provider.return_value = mock_instance\n\n        response = client.post(',
        '        mock_instance.generate.return_value = ("response", 250)\n        mock_provider.return_value = mock_instance\n        mock_billing.deduct_credits = AsyncMock(return_value=250)\n\n        response = client.post('
    ),
    (
        '    @patch("app.api.v1.generate.AnthropicProvider")\n    def test_real_privacy_shield_integration(self, mock_provider):',
        '    @patch("app.api.v1.generate.BillingService")\n    @patch("app.api.v1.generate.AnthropicProvider")\n    def test_real_privacy_shield_integration(self, mock_provider, mock_billing):'
    ),
    (
        '        mock_instance.generate.return_value = ("Sanitized response", 100)\n        mock_provider.return_value = mock_instance\n\n        response = client.post(',
        '        mock_instance.generate.return_value = ("Sanitized response", 100)\n        mock_provider.return_value = mock_instance\n        mock_billing.deduct_credits = AsyncMock(return_value=400)\n\n        response = client.post('
    ),
]

# Apply replacements
for old, new in replacements:
    content = content.replace(old, new)

# Write back
with open('app/tests/test_generate.py', 'w') as f:
    f.write(content)

print("Updated test_generate.py with BillingService mocks")
