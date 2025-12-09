"""
Tests for SEC-011: Trusted Proxy Middleware (X-Forwarded-For Spoofing Protection)

This test suite validates that the TrustedProxyMiddleware correctly:
1. Trusts X-Forwarded-For from configured trusted proxies
2. Ignores X-Forwarded-For from untrusted sources (prevents spoofing)
3. Falls back to direct connection IP when appropriate
4. Handles complex proxy chains correctly
5. Validates IP addresses and CIDR ranges
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.core.trusted_proxy import (
    TrustedProxyMiddleware,
    get_trusted_client_ip,
    parse_trusted_proxies,
)


@pytest.fixture
def app_no_proxies():
    """FastAPI app with no trusted proxies configured."""
    app = FastAPI()

    # Add middleware with no trusted proxies
    app.add_middleware(TrustedProxyMiddleware, trusted_proxies=[])

    @app.get("/test")
    async def test_endpoint(request: Request):
        return {"client_ip": get_trusted_client_ip(request)}

    return app


@pytest.fixture
def app_with_trusted_proxies():
    """FastAPI app with trusted proxies configured."""
    app = FastAPI()

    # Add middleware with common trusted proxy networks
    trusted_proxies = [
        "10.0.0.0/8",  # Private network
        "172.16.0.0/12",  # Docker default
        "192.168.1.1",  # Single IP
        "203.0.113.0/24",  # Example network
    ]
    app.add_middleware(TrustedProxyMiddleware, trusted_proxies=trusted_proxies)

    @app.get("/test")
    async def test_endpoint(request: Request):
        return {"client_ip": get_trusted_client_ip(request)}

    return app


class TestParsingTrustedProxies:
    """Test parsing of TRUSTED_PROXIES environment variable."""

    def test_parse_empty_string(self):
        """Empty string should return empty list."""
        result = parse_trusted_proxies("")
        assert result == []

    def test_parse_single_ip(self):
        """Single IP should be parsed correctly."""
        result = parse_trusted_proxies("192.168.1.1")
        assert result == ["192.168.1.1"]

    def test_parse_multiple_ips(self):
        """Multiple IPs should be parsed correctly."""
        result = parse_trusted_proxies("192.168.1.1,10.0.0.1,172.16.0.1")
        assert result == ["192.168.1.1", "10.0.0.1", "172.16.0.1"]

    def test_parse_cidr_ranges(self):
        """CIDR ranges should be parsed correctly."""
        result = parse_trusted_proxies("10.0.0.0/8,172.16.0.0/12")
        assert result == ["10.0.0.0/8", "172.16.0.0/12"]

    def test_parse_with_whitespace(self):
        """Whitespace should be trimmed."""
        result = parse_trusted_proxies(" 192.168.1.1 , 10.0.0.1 ")
        assert result == ["192.168.1.1", "10.0.0.1"]

    def test_parse_mixed_format(self):
        """Mixed IPs and CIDRs should work."""
        result = parse_trusted_proxies("192.168.1.1,10.0.0.0/8,172.16.5.5")
        assert result == ["192.168.1.1", "10.0.0.0/8", "172.16.5.5"]


class TestNoTrustedProxies:
    """Test behavior when no trusted proxies are configured."""

    def test_direct_connection_used(self, app_no_proxies):
        """Direct connection IP should be used when no proxies configured."""
        client = TestClient(app_no_proxies)

        # Simulate direct connection from client
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()
        # TestClient uses testclient as the host
        assert "client_ip" in data

    def test_x_forwarded_for_ignored(self, app_no_proxies):
        """X-Forwarded-For should be ignored when no proxies configured."""
        client = TestClient(app_no_proxies)

        # Try to spoof IP via X-Forwarded-For
        response = client.get(
            "/test", headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8"}
        )

        assert response.status_code == 200
        data = response.json()
        # Should use direct connection IP, not the spoofed one
        assert data["client_ip"] != "1.2.3.4"


class TestTrustedProxyValidation:
    """Test validation of trusted vs untrusted proxies."""

    def test_trusted_proxy_single_ip(self, app_with_trusted_proxies):
        """X-Forwarded-For from trusted single IP should be honored."""
        # This is challenging to test with TestClient as it doesn't allow
        # controlling the remote address. We'll use a mock-based approach.

        from app.core.trusted_proxy import TrustedProxyMiddleware

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["192.168.1.1"]
        )

        # Test that the proxy is recognized as trusted
        assert middleware._is_trusted_proxy("192.168.1.1") is True
        assert middleware._is_trusted_proxy("192.168.1.2") is False

    def test_trusted_proxy_cidr_range(self):
        """X-Forwarded-For from trusted CIDR range should be honored."""
        from app.core.trusted_proxy import TrustedProxyMiddleware

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.0/8"]
        )

        # IPs within range should be trusted
        assert middleware._is_trusted_proxy("10.0.0.1") is True
        assert middleware._is_trusted_proxy("10.255.255.254") is True

        # IPs outside range should not be trusted
        assert middleware._is_trusted_proxy("11.0.0.1") is False
        assert middleware._is_trusted_proxy("192.168.1.1") is False

    def test_untrusted_proxy_ignored(self):
        """X-Forwarded-For from untrusted proxy should be ignored."""
        from app.core.trusted_proxy import TrustedProxyMiddleware

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["192.168.1.1"]
        )

        # Untrusted proxy
        assert middleware._is_trusted_proxy("203.0.113.50") is False


class TestProxyChainParsing:
    """Test parsing of complex X-Forwarded-For proxy chains."""

    def test_simple_forwarded_for(self):
        """Simple X-Forwarded-For with client and proxy."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.1"]
        )

        # Create mock request
        request = Mock()
        request.client = Mock(host="10.0.0.1")  # Trusted proxy
        request.headers = {"X-Forwarded-For": "203.0.113.50"}
        request.state = Mock()

        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "203.0.113.50"

    def test_multi_proxy_chain(self):
        """Multiple proxies in X-Forwarded-For chain."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.1", "10.0.0.2"]
        )

        # Create mock request with proxy chain
        request = Mock()
        request.client = Mock(host="10.0.0.2")  # Trusted proxy
        request.headers = {"X-Forwarded-For": "203.0.113.50, 10.0.0.1"}
        request.state = Mock()

        # Should extract the client IP (first untrusted IP from right)
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "203.0.113.50"

    def test_all_proxies_trusted(self):
        """All IPs in chain are trusted (edge case)."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.0/8"]
        )

        # Create mock request where all IPs are trusted
        request = Mock()
        request.client = Mock(host="10.0.0.2")  # Trusted
        request.headers = {"X-Forwarded-For": "10.0.0.50, 10.0.0.1"}
        request.state = Mock()

        # Should use leftmost (original client)
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "10.0.0.50"

    def test_untrusted_direct_connection(self):
        """Direct connection from untrusted source ignores X-Forwarded-For."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.1"]
        )

        # Create mock request from untrusted source
        request = Mock()
        request.client = Mock(host="203.0.113.50")  # Untrusted
        request.headers = {"X-Forwarded-For": "1.2.3.4, 5.6.7.8"}
        request.state = Mock()

        # Should use direct connection, ignoring spoofed header
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "203.0.113.50"

    def test_no_x_forwarded_for_header(self):
        """No X-Forwarded-For header uses direct connection."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.1"]
        )

        # Create mock request without X-Forwarded-For
        request = Mock()
        request.client = Mock(host="10.0.0.1")  # Trusted proxy
        request.headers = {}
        request.state = Mock()

        # Should use direct connection IP
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "10.0.0.1"


class TestIPWhitelistIntegration:
    """Test integration with existing IP whitelist functionality."""

    def test_ip_whitelist_uses_validated_ip(self):
        """IP whitelist should use the validated IP from middleware."""
        from app.core.ip_whitelist import get_client_ip
        from unittest.mock import Mock

        # Create mock request with validated IP in state
        request = Mock()
        request.state = Mock()
        request.state.client_ip = "203.0.113.50"
        request.headers = {"X-Forwarded-For": "1.2.3.4"}  # Spoofed
        request.client = Mock(host="10.0.0.1")

        # get_client_ip should use the validated IP from state
        client_ip = get_client_ip(request)
        assert client_ip == "203.0.113.50"

    def test_ip_whitelist_fallback_without_middleware(self):
        """IP whitelist should fall back gracefully without middleware."""
        from app.core.ip_whitelist import get_client_ip
        from unittest.mock import Mock

        # Create mock request without validated IP (middleware not configured)
        request = Mock()
        request.state = Mock(spec=[])  # Empty state
        request.headers = {"X-Forwarded-For": "203.0.113.50"}
        request.client = Mock(host="10.0.0.1")

        # Should fall back to X-Forwarded-For (legacy behavior)
        client_ip = get_client_ip(request)
        assert client_ip == "203.0.113.50"


class TestInvalidConfiguration:
    """Test handling of invalid configurations."""

    def test_invalid_ip_in_config(self):
        """Invalid IP addresses in config should be logged and skipped."""
        from app.core.trusted_proxy import TrustedProxyMiddleware

        # Should not raise, but log warning
        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["invalid_ip", "10.0.0.1"]
        )

        # Valid IP should still be configured
        assert middleware._is_trusted_proxy("10.0.0.1") is True
        assert middleware._is_trusted_proxy("invalid_ip") is False

    def test_invalid_cidr_in_config(self):
        """Invalid CIDR ranges should be logged and skipped."""
        from app.core.trusted_proxy import TrustedProxyMiddleware

        # Should not raise, but log warning
        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.0/99", "10.0.0.0/8"]
        )

        # Valid CIDR should still be configured
        assert middleware._is_trusted_proxy("10.0.0.1") is True


class TestSecurityScenarios:
    """Test real-world security scenarios."""

    def test_prevents_ip_spoofing_attack(self):
        """Malicious client cannot spoof IP via X-Forwarded-For."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.1"]
        )

        # Attacker sends request directly with spoofed X-Forwarded-For
        request = Mock()
        request.client = Mock(host="203.0.113.100")  # Attacker's real IP
        request.headers = {
            "X-Forwarded-For": "192.168.1.1"  # Spoofed internal IP
        }
        request.state = Mock()

        # Middleware should detect untrusted proxy and use real IP
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "203.0.113.100"  # Real attacker IP
        assert client_ip != "192.168.1.1"  # Not the spoofed IP

    def test_cloudflare_like_scenario(self):
        """Simulate Cloudflare CDN forwarding real client IP."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        # Cloudflare example IP ranges (simplified)
        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["173.245.48.0/20", "103.21.244.0/22"]
        )

        # Request comes from Cloudflare with X-Forwarded-For
        request = Mock()
        request.client = Mock(host="173.245.48.1")  # Cloudflare IP
        request.headers = {"X-Forwarded-For": "198.51.100.42"}  # Real client
        request.state = Mock()

        # Should trust Cloudflare and extract real client IP
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "198.51.100.42"

    def test_docker_network_scenario(self):
        """Simulate Docker container behind reverse proxy."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        # Trust Docker bridge network
        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["172.16.0.0/12"]
        )

        # Request from reverse proxy in Docker network
        request = Mock()
        request.client = Mock(host="172.17.0.2")  # Docker bridge
        request.headers = {"X-Forwarded-For": "203.0.113.75"}  # Real client
        request.state = Mock()

        # Should trust Docker network and extract real client IP
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "203.0.113.75"

    def test_multi_layer_proxy_chain(self):
        """Complex scenario with client -> CDN -> LB -> app."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        # Trust both CDN and internal load balancer
        middleware = TrustedProxyMiddleware(
            app=Mock(),
            trusted_proxies=["173.245.48.0/20", "10.0.0.0/8", "172.16.0.0/12"],
        )

        # Request chain: Client -> Cloudflare -> Internal LB -> App
        request = Mock()
        request.client = Mock(host="10.0.0.5")  # Internal LB (trusted)
        request.headers = {
            # Client, Cloudflare, Internal LB
            "X-Forwarded-For": "198.51.100.42, 173.245.48.1, 10.0.0.5"
        }
        request.state = Mock()

        # Should extract the real client IP (first untrusted from right)
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "198.51.100.42"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_no_client_in_request(self):
        """Handle request without client attribute."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.1"]
        )

        request = Mock()
        request.client = None
        request.headers = {}
        request.state = Mock()

        # Should return "unknown"
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "unknown"

    def test_whitespace_in_forwarded_for(self):
        """Handle whitespace in X-Forwarded-For values."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(), trusted_proxies=["10.0.0.1"]
        )

        request = Mock()
        request.client = Mock(host="10.0.0.1")
        request.headers = {
            "X-Forwarded-For": " 203.0.113.50 ,  10.0.0.1  "  # Extra spaces
        }
        request.state = Mock()

        # Should handle whitespace correctly
        client_ip = middleware._extract_client_ip(request)
        assert client_ip == "203.0.113.50"

    def test_ipv6_addresses(self):
        """Handle IPv6 addresses in configuration."""
        from app.core.trusted_proxy import TrustedProxyMiddleware
        from unittest.mock import Mock

        middleware = TrustedProxyMiddleware(
            app=Mock(),
            trusted_proxies=["2001:db8::/32", "::1"],  # IPv6 range and localhost
        )

        # IPv6 addresses should be recognized
        assert middleware._is_trusted_proxy("2001:db8::1") is True
        assert middleware._is_trusted_proxy("::1") is True
        assert middleware._is_trusted_proxy("2001:db9::1") is False
