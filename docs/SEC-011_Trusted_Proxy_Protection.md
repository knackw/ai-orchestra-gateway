# SEC-011: X-Forwarded-For Spoofing Protection

**Status:** ✅ Implemented
**Version:** 1.0
**Date:** 2025-12-08

---

## Overview

This document describes the implementation of X-Forwarded-For spoofing protection through trusted proxy validation. This security feature prevents malicious clients from bypassing IP-based access controls by spoofing the `X-Forwarded-For` header.

## Problem Statement

### The Vulnerability

When applications run behind reverse proxies (Nginx, Cloudflare, load balancers), they receive the client's real IP through the `X-Forwarded-For` header rather than from the direct TCP connection. However, this header can be easily spoofed:

```http
# Attacker sends:
X-Forwarded-For: 192.168.1.1

# Application believes this is the client IP
# Bypassing IP whitelist that allows 192.168.1.0/24
```

### Impact

Without proper validation:
- **IP whitelist bypass**: Attackers can spoof internal IPs to gain unauthorized access
- **Rate limit bypass**: Different IPs can evade rate limiting
- **Audit log corruption**: False IPs in security logs make forensics impossible
- **Compliance violations**: GDPR/audit logs contain incorrect client identification

## Solution Architecture

### Trust Model

The solution implements a **zero-trust model** for X-Forwarded-For headers:

1. **Default behavior**: X-Forwarded-For headers are **IGNORED** by default
2. **Explicit trust**: Only IPs/networks in `TRUSTED_PROXIES` can set client IPs
3. **Validation chain**: Parse X-Forwarded-For from right to left, finding first untrusted IP
4. **Fallback**: Always fall back to direct connection IP if validation fails

### Request Flow

```
Client (203.0.113.50)
    ↓
Cloudflare (173.245.48.1) [Trusted]
    ↓ X-Forwarded-For: 203.0.113.50
Internal LB (10.0.0.1) [Trusted]
    ↓ X-Forwarded-For: 203.0.113.50, 173.245.48.1
Application (validates chain)
    ↓
Extracted IP: 203.0.113.50 ✅
```

### Attack Prevention

```
Attacker (203.0.113.100)
    ↓ X-Forwarded-For: 192.168.1.1 (spoofed)
Direct Connection
    ↓
Application (validates source is NOT trusted)
    ↓
Uses direct IP: 203.0.113.100 ✅
Ignores spoofed header ✅
```

## Implementation

### Components

#### 1. Trusted Proxy Middleware

**File:** `/root/Projekte/ai-orchestra-gateway/app/core/trusted_proxy.py`

**Key Features:**
- Validates X-Forwarded-For against trusted proxy list
- Supports both single IPs and CIDR ranges
- Parses complex proxy chains correctly
- Stores validated IP in `request.state.client_ip`
- Comprehensive logging for security auditing

#### 2. IP Whitelist Integration

**File:** `/root/Projekte/ai-orchestra-gateway/app/core/ip_whitelist.py`

**Changes:**
- `get_client_ip()` now uses `request.state.client_ip` (validated by middleware)
- Falls back to legacy behavior if middleware not configured
- Logs warning when middleware is not present

#### 3. Configuration

**File:** `/root/Projekte/ai-orchestra-gateway/app/core/config.py`

**New Setting:**
```python
TRUSTED_PROXIES: str = ""  # Comma-separated IPs/CIDRs
```

#### 4. Middleware Registration

**File:** `/root/Projekte/ai-orchestra-gateway/app/main.py`

**Integration:**
```python
from app.core.trusted_proxy import TrustedProxyMiddleware, parse_trusted_proxies

trusted_proxies = parse_trusted_proxies(settings.TRUSTED_PROXIES)
app.add_middleware(TrustedProxyMiddleware, trusted_proxies=trusted_proxies)
```

## Configuration

### Environment Variable

```bash
# .env file
TRUSTED_PROXIES="10.0.0.0/8,172.16.0.0/12,192.168.1.1"
```

### Common Configurations

#### Cloudflare CDN

```bash
# Get latest IPs from: https://www.cloudflare.com/ips/
TRUSTED_PROXIES="173.245.48.0/20,103.21.244.0/22,103.22.200.0/22,103.31.4.0/22,141.101.64.0/18,108.162.192.0/18,190.93.240.0/20,188.114.96.0/20,197.234.240.0/22,198.41.128.0/17,162.158.0.0/15,104.16.0.0/13,104.24.0.0/14,172.64.0.0/13,131.0.72.0/22"
```

#### AWS Load Balancer

```bash
# Internal VPC network
TRUSTED_PROXIES="10.0.0.0/8"
```

#### Docker Compose

```bash
# Docker bridge network
TRUSTED_PROXIES="172.16.0.0/12"
```

#### Nginx Reverse Proxy

```bash
# Local reverse proxy
TRUSTED_PROXIES="127.0.0.1,::1"
```

#### Multi-Layer Setup

```bash
# CDN + Load Balancer + Docker
TRUSTED_PROXIES="173.245.48.0/20,10.0.0.0/8,172.16.0.0/12"
```

## Security Considerations

### Best Practices

1. **Minimal trust**: Only add IPs/networks that MUST set X-Forwarded-For
2. **Regular updates**: Update CDN IP ranges when provider publishes changes
3. **Audit logging**: Review middleware logs for suspicious patterns
4. **Defense in depth**: Combine with other security measures (rate limiting, WAF)

### Warning Signs

Monitor logs for:
- Repeated warnings about untrusted proxies setting X-Forwarded-For
- All IPs in chain being trusted (unusual configuration)
- Direct connections claiming to be from internal IPs

### Testing in Development

```bash
# Development: No proxies (X-Forwarded-For ignored)
TRUSTED_PROXIES=""

# Development with local Nginx
TRUSTED_PROXIES="127.0.0.1"
```

## Testing

### Test Suite

**File:** `/root/Projekte/ai-orchestra-gateway/app/tests/test_trusted_proxy.py`

**Coverage:**
- Parsing of environment variable
- Trust validation for single IPs and CIDR ranges
- Proxy chain parsing (simple and complex)
- Security scenarios (spoofing attacks, multi-layer proxies)
- Edge cases (invalid IPs, IPv6, whitespace)

**Run tests:**
```bash
pytest app/tests/test_trusted_proxy.py -v
pytest app/tests/test_ip_whitelist.py -v
```

### Manual Testing

#### Test 1: Direct Connection (No Proxy)

```bash
curl -H "X-Forwarded-For: 1.2.3.4" http://localhost:8000/api/v1/resource
# Should use direct connection IP, ignore spoofed header
```

#### Test 2: Trusted Proxy

```bash
# Configure: TRUSTED_PROXIES="10.0.0.1"
# Request from 10.0.0.1 with X-Forwarded-For: 203.0.113.50
# Should extract 203.0.113.50 as client IP
```

#### Test 3: Untrusted Proxy

```bash
# Configure: TRUSTED_PROXIES="10.0.0.1"
# Request from 203.0.113.100 with X-Forwarded-For: 192.168.1.1
# Should use 203.0.113.100 (direct), ignore spoofed header
```

## Performance Impact

### Overhead

- **Minimal**: IP validation uses `ipaddress` module (C-optimized)
- **Per-request**: ~0.1ms for typical configurations (<10 trusted networks)
- **Memory**: Negligible (~1KB per trusted network)

### Optimization Tips

1. Use CIDR ranges instead of individual IPs
2. Limit trusted proxies to essential networks only
3. Place middleware early in chain (before expensive operations)

## Monitoring & Logging

### Log Levels

**DEBUG:**
- Every validated IP extraction
- Proxy chain parsing details

**INFO:**
- Trusted proxy network additions on startup

**WARNING:**
- Middleware not configured in production
- All IPs in chain are trusted (edge case)
- Invalid IP addresses in configuration

**ERROR:**
- Invalid CIDR ranges in configuration

### Example Logs

```
INFO:app.core.trusted_proxy:Added trusted proxy network: 10.0.0.0/8
INFO:app.core.trusted_proxy:Added trusted proxy network: 173.245.48.0/20

DEBUG:app.core.trusted_proxy:IP 173.245.48.1 matched trusted network 173.245.48.0/20
DEBUG:app.core.trusted_proxy:Extracted client IP 203.0.113.50 from X-Forwarded-For (chain: 203.0.113.50, 173.245.48.1, direct: 10.0.0.1)

WARNING:app.core.ip_whitelist:TrustedProxyMiddleware not configured. IP validation may be insecure.
```

## Migration Guide

### From Unprotected to Protected

**Before (vulnerable):**
```python
def get_client_ip(request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host
```

**After (secure):**
```python
# Add middleware in main.py
app.add_middleware(TrustedProxyMiddleware, trusted_proxies=parse_trusted_proxies(settings.TRUSTED_PROXIES))

# Use validated IP
def get_client_ip(request):
    if hasattr(request.state, "client_ip"):
        return request.state.client_ip
    # Fallback...
```

### Rollout Strategy

1. **Phase 1**: Deploy with empty `TRUSTED_PROXIES` (safe mode)
   - X-Forwarded-For will be ignored
   - Monitor for direct connection IPs

2. **Phase 2**: Configure trusted proxies in staging
   - Test with real proxy setup
   - Verify correct IP extraction

3. **Phase 3**: Production rollout
   - Enable trusted proxies
   - Monitor logs for warnings
   - Verify IP whitelist behavior

## Compliance

### GDPR

- **Article 32**: Technical measures to ensure security
- **Audit logging**: Correct client identification for legal compliance
- **Data accuracy**: Ensures IP-based processing uses real client IPs

### SOC 2

- **CC6.1**: Logical access controls (IP whitelisting)
- **CC7.2**: System monitoring (audit logs with accurate IPs)

## References

### Standards

- [RFC 7239](https://www.rfc-editor.org/rfc/rfc7239.html): Forwarded HTTP Extension
- [OWASP: IP Spoofing](https://owasp.org/www-community/attacks/Spoofing_Attack)

### Dependencies

- Python `ipaddress` module (standard library)
- Starlette middleware base classes

### Related Security Measures

- **SEC-009**: IP Whitelisting (tenant-level)
- **SEC-007**: Rate Limiting (IP-based)
- **SEC-010**: Error Handling (production logs)

---

## Changelog

### Version 1.0 (2025-12-08)

- Initial implementation
- Trusted proxy middleware
- IP whitelist integration
- Comprehensive test suite
- Documentation and configuration examples
