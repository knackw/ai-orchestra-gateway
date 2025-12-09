import pytest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.billing import BillingService

class TestBillingService:
    
    @patch("app.services.billing.get_supabase_client")
    async def test_deduct_credits_success(self, mock_get_client):
        """Test successful credit deduction."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = 950  # New balance
        
        # Mock RPC call chain
        mock_client.rpc.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        new_balance = await BillingService.deduct_credits("lic_123", 50)
        
        assert new_balance == 950
        mock_client.rpc.assert_called_with(
            "deduct_credits", 
            {"p_license_key": "lic_123", "p_amount": 50}
        )

    @patch("app.services.billing.get_supabase_client")
    async def test_deduct_credits_insufficient(self, mock_get_client):
        """Test insufficient credits raises 402."""
        mock_client = MagicMock()
        
        # Mock RPC raising exception
        mock_client.rpc.return_value.execute.side_effect = Exception("INSUFFICIENT_CREDITS: Current balance 10 is less than required 50")
        mock_get_client.return_value = mock_client
        
        with pytest.raises(HTTPException) as exc:
            await BillingService.deduct_credits("lic_123", 50)
            
        assert exc.value.status_code == 402
        assert "Insufficient credits" in exc.value.detail

    @patch("app.services.billing.get_supabase_client")
    async def test_deduct_credits_invalid_license(self, mock_get_client):
        """Test invalid license raises 403."""
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.side_effect = Exception("INVALID_LICENSE: License key not found")
        mock_get_client.return_value = mock_client
        
        with pytest.raises(HTTPException) as exc:
            await BillingService.deduct_credits("lic_unknown", 50)
            
        assert exc.value.status_code == 403
        assert "Invalid license key" in exc.value.detail

    @patch("app.services.billing.get_supabase_client")
    async def test_add_credits_success(self, mock_get_client):
        """Test successful credit addition."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = None
        
        mock_client.rpc.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Should not raise exception
        await BillingService.add_credits("lic_123", 100)
        
        mock_client.rpc.assert_called_with(
            "add_credits", 
            {"license_key_param": "lic_123", "credits_to_add": 100}
        )

    @patch("app.services.billing.get_supabase_client")
    async def test_concurrent_deductions(self, mock_get_client):
        """Test concurrent deductions are handled (mock)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = 900
        mock_client.rpc.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Simulate 10 concurrent requests
        tasks = [BillingService.deduct_credits("lic_123", 10) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(r == 900 for r in results)
        assert mock_client.rpc.call_count == 10
