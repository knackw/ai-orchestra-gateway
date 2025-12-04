"""
Unit tests for BillingService.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException

from app.services.billing import BillingService


class TestBillingService:
    """Tests for BillingService credit deduction."""

    @pytest.mark.asyncio
    @patch("app.services.billing.get_supabase_client")
    async def test_deduct_credits_success(self, mock_get_client):
        """Test successful credit deduction."""
        # Mock Supabase RPC response
        mock_client = Mock()
        mock_rpc = Mock()
        mock_execute = Mock()
        mock_execute.data = 500  # New balance after deduction
        mock_rpc.execute.return_value = mock_execute
        mock_client.rpc.return_value = mock_rpc
        mock_get_client.return_value = mock_client

        # Call billing service
        new_balance = await BillingService.deduct_credits("lic_test123", 50)

        # Verify
        assert new_balance == 500
        mock_client.rpc.assert_called_once_with(
            "deduct_credits",
            {"p_license_key": "lic_test123", "p_amount": 50}
        )

    @pytest.mark.asyncio
    @patch("app.services.billing.get_supabase_client")
    async def test_insufficient_credits(self, mock_get_client):
        """Test handling of insufficient credits."""
        # Mock Supabase error
        mock_client = Mock()
        mock_client.rpc.side_effect = Exception("INSUFFICIENT_CREDITS: Current balance 10 is less than required 50")
        mock_get_client.return_value = mock_client

        # Verify 402 error raised
        with pytest.raises(HTTPException) as exc_info:
            await BillingService.deduct_credits("lic_test123", 50)

        assert exc_info.value.status_code == 402
        assert "Insufficient credits" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.billing.get_supabase_client")
    async def test_invalid_license(self, mock_get_client):
        """Test handling of invalid license key."""
        # Mock Supabase error
        mock_client = Mock()
        mock_client.rpc.side_effect = Exception("INVALID_LICENSE: License key not found")
        mock_get_client.return_value = mock_client

        # Verify 403 error raised
        with pytest.raises(HTTPException) as exc_info:
            await BillingService.deduct_credits("lic_invalid", 50)

        assert exc_info.value.status_code == 403
        assert "Invalid license" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.billing.get_supabase_client")
    async def test_inactive_license(self, mock_get_client):
        """Test handling of inactive license."""
        # Mock Supabase error
        mock_client = Mock()
        mock_client.rpc.side_effect = Exception("INACTIVE_LICENSE: License is not active")
        mock_get_client.return_value = mock_client

        # Verify 403 error raised
        with pytest.raises(HTTPException) as exc_info:
            await BillingService.deduct_credits("lic_inactive", 50)

        assert exc_info.value.status_code == 403
        assert "not active" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.billing.get_supabase_client")
    async def test_expired_license(self, mock_get_client):
        """Test handling of expired license."""
        # Mock Supabase error
        mock_client = Mock()
        mock_client.rpc.side_effect = Exception("EXPIRED_LICENSE: License has expired")
        mock_get_client.return_value = mock_client

        # Verify 403 error raised
        with pytest.raises(HTTPException) as exc_info:
            await BillingService.deduct_credits("lic_expired", 50)

        assert exc_info.value.status_code == 403
        assert "expired" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.services.billing.get_supabase_client")
    async def test_database_error(self, mock_get_client):
        """Test handling of unexpected database errors."""
        # Mock unexpected error
        mock_client = Mock()
        mock_client.rpc.side_effect = Exception("Connection timeout")
        mock_get_client.return_value = mock_client

        # Verify 500 error raised
        with pytest.raises(HTTPException) as exc_info:
            await BillingService.deduct_credits("lic_test123", 50)

        assert exc_info.value.status_code == 500
        assert "Billing system error" in exc_info.value.detail
