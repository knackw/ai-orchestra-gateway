"""
Unit tests for security and authentication.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.core.security import LicenseInfo, get_current_license, validate_license_key


class TestValidateLicenseKey:
    """Tests for validate_license_key function."""

    @patch("app.core.security.get_supabase_client")
    @pytest.mark.asyncio
    async def test_valid_license(self, mock_supabase):
        """Test validation with valid, active license."""
        # Mock Supabase response
        mock_response = MagicMock()
        mock_response.data = {
            "license_key": "lic_valid_123",
            "tenant_id": "tenant-uuid-123",
            "is_active": True,
            "expires_at": None,
            "credits_remaining": 1000,
        }
        
        mock_client = MagicMock()
        mock_client.table().select().eq().single().execute.return_value = mock_response
        mock_supabase.return_value = mock_client

        # Validate
        license_info = await validate_license_key("lic_valid_123")

        # Assertions
        assert isinstance(license_info, LicenseInfo)
        assert license_info.license_key == "lic_valid_123"
        assert license_info.tenant_id == "tenant-uuid-123"
        assert license_info.is_active is True
        assert license_info.expires_at is None
        assert license_info.credits_remaining == 1000

    @patch("app.core.security.get_supabase_client")
    @pytest.mark.asyncio
    async def test_valid_license_with_expiry(self, mock_supabase):
        """Test validation with valid license that expires in future."""
        future_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        mock_response = MagicMock()
        mock_response.data = {
            "license_key": "lic_expiring",
            "tenant_id": "tenant-uuid-456",
            "is_active": True,
            "expires_at": future_date.isoformat(),
            "credits_remaining": 500,
        }
        
        mock_client = MagicMock()
        mock_client.table().select().eq().single().execute.return_value = mock_response
        mock_supabase.return_value = mock_client

        license_info = await validate_license_key("lic_expiring")

        assert license_info.tenant_id == "tenant-uuid-456"
        assert license_info.expires_at is not None

    @patch("app.core.security.get_supabase_client")
    @pytest.mark.asyncio
    async def test_invalid_license_key(self, mock_supabase):
        """Test validation with non-existent license key."""
        mock_response = MagicMock()
        mock_response.data = None  # No data = license not found
        
        mock_client = MagicMock()
        mock_client.table().select().eq().single().execute.return_value = mock_response
        mock_supabase.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await validate_license_key("lic_invalid")

        assert exc_info.value.status_code == 403
        assert "Invalid license key" in exc_info.value.detail

    @patch("app.core.security.get_supabase_client")
    @pytest.mark.asyncio
    async def test_inactive_license(self, mock_supabase):
        """Test validation with inactive license."""
        mock_response = MagicMock()
        mock_response.data = {
            "license_key": "lic_inactive",
            "tenant_id": "tenant-uuid-789",
            "is_active": False,  # Inactive
            "expires_at": None,
            "credits_remaining": 100,
        }
        
        mock_client = MagicMock()
        mock_client.table().select().eq().single().execute.return_value = mock_response
        mock_supabase.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await validate_license_key("lic_inactive")

        assert exc_info.value.status_code == 403
        assert "not active" in exc_info.value.detail.lower()

    @patch("app.core.security.get_supabase_client")
    @pytest.mark.asyncio
    async def test_expired_license(self, mock_supabase):
        """Test validation with expired license."""
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        
        mock_response = MagicMock()
        mock_response.data = {
            "license_key": "lic_expired",
            "tenant_id": "tenant-uuid-012",
            "is_active": True,
            "expires_at": past_date.isoformat(),
            "credits_remaining": 1000,
        }
        
        mock_client = MagicMock()
        mock_client.table().select().eq().single().execute.return_value = mock_response
        mock_supabase.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await validate_license_key("lic_expired")

        assert exc_info.value.status_code == 403
        assert "expired" in exc_info.value.detail.lower()

    @patch("app.core.security.get_supabase_client")
    @pytest.mark.asyncio
    async def test_no_credits_remaining(self, mock_supabase):
        """Test validation with no credits remaining."""
        mock_response = MagicMock()
        mock_response.data = {
            "license_key": "lic_nocredits",
            "tenant_id": "tenant-uuid-345",
            "is_active": True,
            "expires_at": None,
            "credits_remaining": 0,  # No credits
        }
        
        mock_client = MagicMock()
        mock_client.table().select().eq().single().execute.return_value = mock_response
        mock_supabase.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await validate_license_key("lic_nocredits")

        assert exc_info.value.status_code == 402
        assert "credits" in exc_info.value.detail.lower()

    @patch("app.core.security.get_supabase_client")
    @pytest.mark.asyncio
    async def test_database_error(self, mock_supabase):
        """Test handling of database errors."""
        mock_client = MagicMock()
        mock_client.table().select().eq().single().execute.side_effect = Exception(
            "Database connection failed"
        )
        mock_supabase.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await validate_license_key("lic_test")

        assert exc_info.value.status_code == 500
        assert "Authentication error" in exc_info.value.detail


class TestGetCurrentLicense:
    """Tests for get_current_license dependency."""

    @pytest.mark.asyncio
    async def test_missing_header(self):
        """Test with missing X-License-Key header."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_license(x_license_key=None)

        assert exc_info.value.status_code == 401
        assert "Missing" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_empty_header(self):
        """Test with empty X-License-Key header."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_license(x_license_key="   ")

        assert exc_info.value.status_code == 401
        assert "Empty" in exc_info.value.detail

    @patch("app.core.security.validate_license_key")
    @pytest.mark.asyncio
    async def test_valid_header(self, mock_validate):
        """Test with valid X-License-Key header."""
        mock_license = LicenseInfo(
            license_key="lic_test",
            tenant_id="tenant-123",
            credits_remaining=1000,
            is_active=True,
        )
        mock_validate.return_value = mock_license

        result = await get_current_license(x_license_key="lic_test")

        assert result == mock_license
        mock_validate.assert_called_once_with("lic_test")


class TestLicenseInfo:
    """Tests for LicenseInfo class."""

    def test_license_info_creation(self):
        """Test creating LicenseInfo object."""
        license_info = LicenseInfo(
            license_key="lic_test",
            tenant_id="tenant-abc",
            credits_remaining=500,
            is_active=True,
            expires_at=None,
        )

        assert license_info.license_key == "lic_test"
        assert license_info.tenant_id == "tenant-abc"
        assert license_info.credits_remaining == 500
        assert license_info.is_active is True
        assert license_info.expires_at is None

    def test_license_info_with_expiry(self):
        """Test LicenseInfo with expiration date."""
        expires = datetime(2025, 12, 31, tzinfo=timezone.utc)
        license_info = LicenseInfo(
            license_key="lic_test",
            tenant_id="tenant-def",
            credits_remaining=1000,
            is_active=True,
            expires_at=expires,
        )

        assert license_info.expires_at == expires
