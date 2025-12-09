"""
Trusted Proxy Middleware for X-Forwarded-For Spoofing Protection (SEC-011).

This module prevents IP spoofing attacks by validating that X-Forwarded-For
headers come only from trusted proxy sources (e.g., load balancers, CDNs).

Security Context:
    Without this protection, malicious clients can send arbitrary X-Forwarded-For
    headers to bypass IP-based access controls. This middleware ensures that only
    trusted proxies can set the client IP via X-Forwarded-For.

Architecture:
    1. Validate incoming connection against trusted proxy list
    2. If trusted: use X-Forwarded-For header (rightmost trusted IP)
    3. If untrusted: use direct connection IP only
    4. Store validated IP in request.state for downstream use
"""

import ipaddress
import logging
from typing import List, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)


class TrustedProxyMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates X-Forwarded-For headers against trusted proxy list.

    This prevents IP spoofing attacks where clients can manipulate the
    X-Forwarded-For header to bypass IP-based access controls.

    The middleware:
    1. Checks if the direct connection comes from a trusted proxy
    2. If trusted: parses X-Forwarded-For to extract real client IP
    3. If untrusted: ignores X-Forwarded-For and uses direct connection IP
    4. Stores validated IP in request.state.client_ip

    Example Configuration:
        TRUSTED_PROXIES="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

    Common Use Cases:
        - Cloudflare CDN IPs
        - AWS Load Balancer IPs
        - Docker bridge networks (172.16.0.0/12)
        - Internal load balancers
    """

    def __init__(self, app, trusted_proxies: Optional[List[str]] = None):
        """
        Initialize the trusted proxy middleware.

        Args:
            app: The FastAPI application
            trusted_proxies: List of trusted proxy IP addresses or CIDR ranges.
                           If None or empty, X-Forwarded-For is never trusted.
        """
        super().__init__(app)
        self.trusted_networks = []

        if trusted_proxies:
            for proxy in trusted_proxies:
                try:
                    # Parse as network (supports both single IPs and CIDR notation)
                    network = ipaddress.ip_network(proxy.strip(), strict=False)
                    self.trusted_networks.append(network)
                    logger.info(f"Added trusted proxy network: {network}")
                except ValueError as e:
                    logger.error(f"Invalid trusted proxy configuration: {proxy} - {e}")

        if not self.trusted_networks:
            logger.warning(
                "No trusted proxies configured. X-Forwarded-For headers will be ignored. "
                "Set TRUSTED_PROXIES environment variable if using a reverse proxy."
            )

    def _is_trusted_proxy(self, ip_str: str) -> bool:
        """
        Check if an IP address is in the trusted proxy list.

        Args:
            ip_str: IP address to check

        Returns:
            True if the IP is from a trusted proxy, False otherwise
        """
        if not self.trusted_networks:
            return False

        try:
            ip_addr = ipaddress.ip_address(ip_str)
            for network in self.trusted_networks:
                if ip_addr in network:
                    logger.debug(f"IP {ip_str} matched trusted network {network}")
                    return True
        except ValueError as e:
            logger.warning(f"Invalid IP address format: {ip_str} - {e}")
            return False

        return False

    def _extract_client_ip(self, request: Request) -> str:
        """
        Extract the real client IP from the request.

        This implements the secure IP extraction logic:
        1. Get the direct connection IP
        2. If it's from a trusted proxy, parse X-Forwarded-For
        3. Otherwise, use the direct connection IP only

        X-Forwarded-For Format:
            X-Forwarded-For: client, proxy1, proxy2

        Security Note:
            We parse from right to left, finding the first untrusted IP.
            This prevents spoofing even if the client sends fake IPs.

        Args:
            request: FastAPI request object

        Returns:
            The validated client IP address
        """
        # Get the direct connection IP (this cannot be spoofed)
        direct_ip = request.client.host if request.client else "unknown"

        # If direct connection is not from a trusted proxy, use it directly
        if not self._is_trusted_proxy(direct_ip):
            logger.debug(
                f"Direct connection from untrusted IP {direct_ip}, "
                "ignoring X-Forwarded-For header"
            )
            return direct_ip

        # Direct connection is trusted, check X-Forwarded-For
        forwarded_for = request.headers.get("X-Forwarded-For")
        if not forwarded_for:
            logger.debug(
                f"Trusted proxy {direct_ip} but no X-Forwarded-For header, "
                "using direct IP"
            )
            return direct_ip

        # Parse X-Forwarded-For chain (format: "client, proxy1, proxy2")
        ip_chain = [ip.strip() for ip in forwarded_for.split(",")]

        # Walk backwards through the chain to find the first untrusted IP
        # This is the real client IP (everything after it are trusted proxies)
        for ip in reversed(ip_chain):
            if not self._is_trusted_proxy(ip):
                logger.debug(
                    f"Extracted client IP {ip} from X-Forwarded-For "
                    f"(chain: {forwarded_for}, direct: {direct_ip})"
                )
                return ip

        # All IPs in the chain are trusted (unusual but possible)
        # Use the leftmost (original client reported by first proxy)
        client_ip = ip_chain[0]
        logger.warning(
            f"All IPs in X-Forwarded-For chain are trusted, "
            f"using leftmost: {client_ip} (chain: {forwarded_for})"
        )
        return client_ip

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and validate the client IP.

        Stores the validated client IP in request.state.client_ip
        for use by downstream middleware and route handlers.

        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain

        Returns:
            The response from downstream handlers
        """
        # Extract and validate client IP
        client_ip = self._extract_client_ip(request)

        # Store in request state for downstream use
        request.state.client_ip = client_ip

        # Log for security audit
        logger.debug(
            f"Request from validated IP: {client_ip} "
            f"(direct: {request.client.host if request.client else 'unknown'})"
        )

        # Continue processing
        response = await call_next(request)
        return response


def get_trusted_client_ip(request: Request) -> str:
    """
    Get the validated client IP from request state.

    This IP has been validated by TrustedProxyMiddleware and can be
    trusted for IP-based access control.

    Args:
        request: FastAPI request object

    Returns:
        The validated client IP address

    Usage:
        @app.get("/api/v1/resource")
        async def protected_resource(request: Request):
            client_ip = get_trusted_client_ip(request)
            # Use client_ip for IP whitelist validation
    """
    # If middleware hasn't set it, fall back to direct connection
    if hasattr(request.state, "client_ip"):
        return request.state.client_ip

    # Fallback to direct connection (middleware not configured)
    logger.warning(
        "TrustedProxyMiddleware not configured, using direct connection IP. "
        "This may be insecure if behind a reverse proxy."
    )
    return request.client.host if request.client else "unknown"


def parse_trusted_proxies(env_var: str) -> List[str]:
    """
    Parse the TRUSTED_PROXIES environment variable.

    Format: Comma-separated list of IPs or CIDR ranges
    Example: "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,203.0.113.1"

    Args:
        env_var: The environment variable string

    Returns:
        List of trusted proxy addresses/ranges
    """
    if not env_var:
        return []

    proxies = [p.strip() for p in env_var.split(",") if p.strip()]
    return proxies
