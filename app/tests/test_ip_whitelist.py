"""
Unit tests for IP Whitelisting functionality.

Tests:
- IP matching logic
- CIDR notation support
- NULL = allow all
- Empty list = block all
"""

import pytest
from unittest.mock import Mock, MagicMock

from app.core.ip_whitelist import is_ip_allowed, get_client_ip, validate_ip_whitelist


class TestIsIpAllowed:
    """Tests for the is_ip_allowed function."""

    def test_none_allows_all(self):
        """NULL allowed_ips should allow all IPs."""
        assert is_ip_allowed("192.168.1.1", None) is True
        assert is_ip_allowed("10.0.0.1", None) is True
        assert is_ip_allowed("8.8.8.8", None) is True

    def test_empty_list_blocks_all(self):
        """Empty allowed_ips list should block all IPs."""
        assert is_ip_allowed("192.168.1.1", []) is False
        assert is_ip_allowed("10.0.0.1", []) is False

    def test_exact_ip_match(self):
        """Exact IP addresses should match."""
        allowed = ["192.168.1.100", "10.0.0.50"]
        
        assert is_ip_allowed("192.168.1.100", allowed) is True
        assert is_ip_allowed("10.0.0.50", allowed) is True
        assert is_ip_allowed("192.168.1.101", allowed) is False
        assert is_ip_allowed("8.8.8.8", allowed) is False

    def test_cidr_notation(self):
        """CIDR notation should match IP ranges."""
        allowed = ["192.168.1.0/24", "10.0.0.0/8"]
        
        # Within 192.168.1.0/24
        assert is_ip_allowed("192.168.1.1", allowed) is True
        assert is_ip_allowed("192.168.1.254", allowed) is True
        
        # Outside 192.168.1.0/24
        assert is_ip_allowed("192.168.2.1", allowed) is False
        
        # Within 10.0.0.0/8 (any 10.x.x.x)
        assert is_ip_allowed("10.0.0.1", allowed) is True
        assert is_ip_allowed("10.255.255.255", allowed) is True
        
        # Outside
        assert is_ip_allowed("11.0.0.1", allowed) is False

    def test_mixed_ips_and_cidrs(self):
        """Mixed list of IPs and CIDRs should work."""
        allowed = ["8.8.8.8", "192.168.0.0/16"]
        
        assert is_ip_allowed("8.8.8.8", allowed) is True
        assert is_ip_allowed("192.168.1.1", allowed) is True
        assert is_ip_allowed("10.0.0.1", allowed) is False

    def test_invalid_client_ip(self):
        """Invalid client IP should be rejected."""
        assert is_ip_allowed("not-an-ip", ["192.168.1.0/24"]) is False
        assert is_ip_allowed("", ["192.168.1.0/24"]) is False

    def test_invalid_whitelist_entry_ignored(self):
        """Invalid entries in whitelist should be ignored, not crash."""
        allowed = ["not-valid", "192.168.1.100", "also-invalid"]
        
        # Valid IP in list should still match
        assert is_ip_allowed("192.168.1.100", allowed) is True
        # Non-matching IP should not match
        assert is_ip_allowed("192.168.1.1", allowed) is False


class TestGetClientIp:
    """Tests for extracting client IP from request."""

    def test_uses_validated_ip_from_middleware(self):
        """Should use validated IP from TrustedProxyMiddleware (SEC-011)."""
        request = Mock()
        request.state = Mock()
        request.state.client_ip = "203.0.113.50"  # Set by middleware
        request.headers = {"X-Forwarded-For": "1.2.3.4"}  # Should be ignored
        request.client = Mock()
        request.client.host = "10.0.0.1"

        # Should use validated IP from middleware
        assert get_client_ip(request) == "203.0.113.50"

    def test_x_forwarded_for_header_fallback(self):
        """Should extract IP from X-Forwarded-For header (legacy fallback)."""
        request = Mock()
        request.state = Mock(spec=[])  # No client_ip attribute
        request.headers = {"X-Forwarded-For": "203.0.113.50"}
        request.client = None

        assert get_client_ip(request) == "203.0.113.50"

    def test_x_forwarded_for_multiple_ips_fallback(self):
        """Should use first IP from X-Forwarded-For chain (legacy fallback)."""
        request = Mock()
        request.state = Mock(spec=[])  # No client_ip attribute
        request.headers = {"X-Forwarded-For": "203.0.113.50, 70.41.3.18, 150.172.238.178"}
        request.client = None

        assert get_client_ip(request) == "203.0.113.50"

    def test_direct_client(self):
        """Should fall back to direct client IP."""
        request = Mock()
        request.state = Mock(spec=[])  # No client_ip attribute
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.100"

        assert get_client_ip(request) == "192.168.1.100"

    def test_no_client_info(self):
        """Should return 'unknown' if no client info available."""
        request = Mock()
        request.state = Mock(spec=[])  # No client_ip attribute
        request.headers = {}
        request.client = None

        assert get_client_ip(request) == "unknown"


class TestValidateIpWhitelist:
    """Tests for the main validation function."""

    def test_allows_when_null(self):
        """Should allow when allowed_ips is None."""
        request = Mock()
        request.state = Mock()
        request.state.client_ip = "192.168.1.1"  # From middleware
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        assert validate_ip_whitelist(request, None) is True

    def test_blocks_when_not_in_list(self):
        """Should block when IP not in whitelist."""
        request = Mock()
        request.state = Mock()
        request.state.client_ip = "192.168.1.1"  # From middleware
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        assert validate_ip_whitelist(request, ["10.0.0.1"]) is False

    def test_allows_when_in_list(self):
        """Should allow when IP is in whitelist."""
        request = Mock()
        request.state = Mock()
        request.state.client_ip = "192.168.1.1"  # From middleware
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        assert validate_ip_whitelist(request, ["192.168.1.0/24"]) is True
