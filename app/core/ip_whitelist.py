"""
IP Whitelisting module for tenant-level access control.

Validates client IP addresses against a tenant's allowed_ips list.
Supports both individual IPs and CIDR notation.

Security Note (SEC-011):
    This module now integrates with TrustedProxyMiddleware to prevent
    X-Forwarded-For spoofing attacks. Always use get_client_ip() which
    retrieves the validated IP from request.state.
"""

import ipaddress
import logging
from typing import List, Optional

from fastapi import Request

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Extract the real client IP from request.

    SEC-011: Now uses validated IP from TrustedProxyMiddleware to prevent
    X-Forwarded-For spoofing. Falls back to legacy behavior if middleware
    is not configured.

    Returns:
        Validated client IP address
    """
    # Use validated IP from TrustedProxyMiddleware (SEC-011)
    if hasattr(request.state, "client_ip"):
        return request.state.client_ip

    # Legacy fallback (if middleware not configured)
    # WARNING: This path is vulnerable to X-Forwarded-For spoofing
    logger.warning(
        "TrustedProxyMiddleware not configured. IP validation may be insecure. "
        "Configure TRUSTED_PROXIES environment variable."
    )

    # Check for forwarded header (common in reverse proxy setups)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, first is the client
        return forwarded.split(",")[0].strip()

    # Fall back to direct connection
    if request.client:
        return request.client.host

    return "unknown"


def is_ip_allowed(client_ip: str, allowed_ips: Optional[List[str]]) -> bool:
    """
    Check if a client IP is allowed based on the whitelist.
    
    Args:
        client_ip: The IP address to check
        allowed_ips: List of allowed IPs/CIDRs, or None to allow all
        
    Returns:
        True if IP is allowed, False otherwise
        
    Rules:
        - None (not set) → Allow all IPs (default behavior)
        - Empty list [] → Block all IPs (paranoid mode)
        - List with values → Allow only matching IPs/CIDRs
    """
    # NULL = allow all (backwards compatible default)
    if allowed_ips is None:
        return True
    
    # Empty list = block all
    if len(allowed_ips) == 0:
        logger.warning(f"IP {client_ip} blocked: empty whitelist (all IPs blocked)")
        return False
    
    try:
        client_addr = ipaddress.ip_address(client_ip)
    except ValueError:
        logger.warning(f"Invalid client IP format: {client_ip}")
        return False
    
    for allowed in allowed_ips:
        try:
            # Try as network (CIDR)
            if "/" in allowed:
                network = ipaddress.ip_network(allowed, strict=False)
                if client_addr in network:
                    return True
            else:
                # Try as single IP
                if client_addr == ipaddress.ip_address(allowed):
                    return True
        except ValueError as e:
            logger.warning(f"Invalid IP/CIDR in whitelist: {allowed} - {e}")
            continue
    
    logger.warning(f"IP {client_ip} not in whitelist")
    return False


def validate_ip_whitelist(request: Request, allowed_ips: Optional[List[str]]) -> bool:
    """
    Validate the request's client IP against the allowed list.
    
    This is the main entry point for IP validation.
    
    Args:
        request: FastAPI request object
        allowed_ips: Tenant's allowed_ips from database
        
    Returns:
        True if allowed, False if blocked
    """
    client_ip = get_client_ip(request)
    return is_ip_allowed(client_ip, allowed_ips)
