# SEC-011: Trusted Proxy Configuration - Quick Reference

**Status:** ✅ Active
**Version:** 0.8.4

---

## TL;DR

Configure `TRUSTED_PROXIES` in `.env` to prevent IP spoofing when running behind reverse proxies.

```bash
# .env
TRUSTED_PROXIES="10.0.0.0/8,172.16.0.0/12"
```

If you don't configure this, X-Forwarded-For headers will be ignored (secure default).

---

## Quick Configuration

### Local Development (No Proxy)

```bash
# No configuration needed - X-Forwarded-For ignored by default
TRUSTED_PROXIES=
```

### Local Development (Nginx/Docker)

```bash
TRUSTED_PROXIES="127.0.0.1,172.16.0.0/12"
```

### Production (Cloudflare + AWS)

```bash
# Cloudflare IPs + AWS VPC
TRUSTED_PROXIES="173.245.48.0/20,103.21.244.0/22,10.0.0.0/8"
```

### Production (Docker Compose)

```bash
# Docker bridge network
TRUSTED_PROXIES="172.16.0.0/12"
```

---

## How It Works

```
1. Client (Real IP: 203.0.113.50)
   ↓
2. Cloudflare (173.245.48.1) [Trusted]
   ↓ Adds X-Forwarded-For: 203.0.113.50
3. Load Balancer (10.0.0.1) [Trusted]
   ↓ Adds X-Forwarded-For: 203.0.113.50, 173.245.48.1
4. Application
   ↓ Validates chain
5. Extracted IP: 203.0.113.50 ✅
```

**Without Trusted Proxies:**
```
1. Attacker (Real IP: 203.0.113.100)
   ↓ Sends X-Forwarded-For: 192.168.1.1 (spoofed)
2. Application
   ↓ Direct connection not trusted
3. Uses Real IP: 203.0.113.100 ✅ (ignores spoofed header)
```

---

## Common Proxy IPs

### Cloudflare CDN

Get latest IPs: https://www.cloudflare.com/ips/

```bash
TRUSTED_PROXIES="173.245.48.0/20,103.21.244.0/22,103.22.200.0/22,103.31.4.0/22,141.101.64.0/18,108.162.192.0/18,190.93.240.0/20,188.114.96.0/20,197.234.240.0/22,198.41.128.0/17,162.158.0.0/15,104.16.0.0/13,104.24.0.0/14,172.64.0.0/13,131.0.72.0/22"
```

### AWS Private Networks

```bash
TRUSTED_PROXIES="10.0.0.0/8"      # Class A private
# or
TRUSTED_PROXIES="172.16.0.0/12"   # Class B private
# or
TRUSTED_PROXIES="192.168.0.0/16"  # Class C private
```

### Docker Networks

```bash
TRUSTED_PROXIES="172.16.0.0/12"   # Docker bridge network
```

### Local Reverse Proxy

```bash
TRUSTED_PROXIES="127.0.0.1,::1"   # Localhost IPv4 + IPv6
```

---

## Using in Code

### Get Validated Client IP

```python
from fastapi import Request
from app.core.ip_whitelist import get_client_ip

@app.get("/protected")
async def protected_resource(request: Request):
    # This IP is validated by TrustedProxyMiddleware
    client_ip = get_client_ip(request)
    # Use for IP whitelist, rate limiting, audit logging
```

### Alternative: Direct Access

```python
from app.core.trusted_proxy import get_trusted_client_ip

@app.get("/protected")
async def protected_resource(request: Request):
    client_ip = get_trusted_client_ip(request)
```

---

## Testing

### Verify Configuration

```bash
# Run tests
pytest app/tests/test_trusted_proxy.py -v

# Check logs on startup
docker-compose logs app | grep "trusted proxy"

# Expected output:
# INFO:app.core.trusted_proxy:Added trusted proxy network: 10.0.0.0/8
# INFO:app.core.trusted_proxy:Added trusted proxy network: 172.16.0.0/12
```

### Test IP Extraction

```bash
# Test direct connection (no proxy)
curl http://localhost:8000/api/v1/health

# Test with spoofed header (should be ignored)
curl -H "X-Forwarded-For: 1.2.3.4" http://localhost:8000/api/v1/health
```

---

## Troubleshooting

### Problem: IP Whitelist Not Working

**Symptom:** Users with whitelisted IPs are blocked

**Cause:** Middleware not extracting correct client IP

**Solution:**
1. Check `TRUSTED_PROXIES` includes your reverse proxy IP
2. Enable DEBUG logging to see IP extraction
3. Verify proxy is setting X-Forwarded-For header

```bash
# Check logs
docker-compose logs app | grep "client_ip"

# Expected:
# DEBUG:app.core.trusted_proxy:Extracted client IP 203.0.113.50 from X-Forwarded-For
```

### Problem: Security Warning in Logs

**Symptom:** `TrustedProxyMiddleware not configured. IP validation may be insecure.`

**Cause:** Running behind proxy but `TRUSTED_PROXIES` not set

**Solution:**
1. Set `TRUSTED_PROXIES` environment variable
2. Restart application

### Problem: All IPs Trusted Warning

**Symptom:** `All IPs in X-Forwarded-For chain are trusted`

**Cause:** Configuration includes too many networks

**Solution:**
1. Review `TRUSTED_PROXIES` configuration
2. Only include IPs of your actual proxies (not client networks)
3. This is usually a misconfiguration

---

## Security Best Practices

### ✅ DO

- Configure `TRUSTED_PROXIES` in production if behind a proxy
- Use CIDR ranges for proxy networks (e.g., `10.0.0.0/8`)
- Keep proxy IP list minimal (only actual proxies)
- Update Cloudflare IPs when they change
- Monitor logs for suspicious patterns

### ❌ DON'T

- Don't trust public IP ranges
- Don't add client networks to trusted proxies
- Don't ignore security warnings in logs
- Don't trust wildcards (not supported)
- Don't disable the middleware in production

---

## Migration Checklist

### Before Deployment

- [ ] Identify your reverse proxy IPs/networks
- [ ] Add `TRUSTED_PROXIES` to `.env` file
- [ ] Test in staging environment
- [ ] Verify IP extraction in logs
- [ ] Test IP whitelist functionality

### After Deployment

- [ ] Monitor logs for warnings
- [ ] Verify audit logs show correct client IPs
- [ ] Test rate limiting behavior
- [ ] Update documentation for ops team

---

## Performance

- **Overhead:** ~0.1ms per request
- **Memory:** Negligible (~1KB per network)
- **CPU:** Uses C-optimized `ipaddress` module

---

## Support

### Documentation

- Full docs: `/root/Projekte/ai-orchestra-gateway/docs/SEC-011_Trusted_Proxy_Protection.md`
- Implementation history: `/root/Projekte/ai-orchestra-gateway/docs/history/2025-12-08_SEC-011_Implementation.md`

### Tests

```bash
# Run all security tests
pytest app/tests/test_trusted_proxy.py app/tests/test_ip_whitelist.py -v

# Run specific test
pytest app/tests/test_trusted_proxy.py::TestSecurityScenarios::test_prevents_ip_spoofing_attack -v
```

### Monitoring

```bash
# Check middleware configuration
docker-compose exec app env | grep TRUSTED_PROXIES

# View real-time logs
docker-compose logs -f app | grep -E "trusted_proxy|client_ip"

# Check for security warnings
docker-compose logs app | grep -i warning | grep -i proxy
```

---

**Version:** 0.8.4
**Last Updated:** 2025-12-08
**Status:** Production Ready ✅
