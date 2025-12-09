"""
Unit tests for UsageService.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.usage import UsageService


class TestUsageService:
    """Tests for UsageService."""

    @patch("app.services.usage.get_supabase_client")
    @pytest.mark.asyncio
    async def test_log_usage_success(self, mock_get_client):
        """Test successful usage logging."""
        # Mock Supabase client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Call service
        await UsageService.log_usage(
            license_id="license-uuid-123",
            app_id="app-uuid-123",
            tenant_id="tenant-uuid-123",
            tokens_used=100,
            credits_deducted=100,
            provider="anthropic",
            model="claude-3-5-sonnet",
            prompt_length=500,
            pii_detected=False
        )
        
        # Verify insert call
        mock_client.table.assert_called_with("usage_logs")
        mock_client.table().insert.assert_called_once()
        
        # Verify data
        call_args = mock_client.table().insert.call_args[0][0]
        assert call_args["license_id"] == "license-uuid-123"
        assert call_args["app_id"] == "app-uuid-123"
        assert call_args["tenant_id"] == "tenant-uuid-123"
        assert call_args["tokens_used"] == 100
        assert call_args["credits_deducted"] == 100
        assert call_args["provider"] == "anthropic"
        assert call_args["pii_detected"] is False
        assert call_args["response_status"] == "success"

    @patch("app.services.usage.get_supabase_client")
    @pytest.mark.asyncio
    async def test_log_usage_error_handling(self, mock_get_client):
        """Test fail-open behavior when logging fails."""
        # Mock error
        mock_get_client.side_effect = Exception("DB Connection Failed")
        
        # Should NOT raise exception (fail open)
        try:
            await UsageService.log_usage(
                license_id="license-uuid-123",
                app_id="app-uuid-123",
                tenant_id="tenant-uuid-123",
                tokens_used=100,
                credits_deducted=100,
                provider="anthropic",
                model="claude-3-5-sonnet",
                prompt_length=500,
                pii_detected=False
            )
        except Exception:
            pytest.fail("UsageService.log_usage raised exception but should fail open")
