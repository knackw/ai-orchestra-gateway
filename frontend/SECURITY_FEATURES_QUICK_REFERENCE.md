# Security Features Quick Reference

Quick reference guide for security features implemented in SEC-021 through SEC-025.

---

## SEC-021: Security.txt

**Location:** `/public/security.txt` and `/public/.well-known/security.txt`

**What it does:** Provides security researchers with contact information for vulnerability disclosure.

**To update:**
1. Edit both files (they should be identical)
2. Update contact email, PGP key URL, and other fields
3. Update expiration date (current: 2026-12-31)

**Test:**
```bash
curl https://yourdomain.com/.well-known/security.txt
```

---

## SEC-022: HSTS Preload

**Location:** `/next.config.ts` (line 59-61)

**What it does:** Forces browsers to use HTTPS for 2 years, protecting against SSL stripping attacks.

**Current configuration:**
```typescript
'max-age=63072000; includeSubDomains; preload'
```

**To submit to preload list:**
1. Visit https://hstspreload.org/
2. Enter your domain
3. Check requirements
4. Submit

**Test:**
```bash
curl -I https://yourdomain.com | grep -i strict-transport-security
```

---

## SEC-023: Subresource Integrity (SRI)

**Location:** `/src/lib/security/sri.ts` and `/src/lib/security/sri.md`

**What it does:** Ensures external CDN resources haven't been tampered with using cryptographic hashes.

**Current status:** No external CDN resources (all self-hosted)

**To add CDN resource:**

```typescript
// 1. Generate hash
curl -s https://cdn.example.com/library.js | \
  openssl dgst -sha384 -binary | openssl base64 -A

// 2. Add to EXTERNAL_RESOURCES in sri.ts
export const EXTERNAL_RESOURCES = {
  myLibrary: {
    url: 'https://cdn.example.com/library.js',
    integrity: 'sha384-GENERATED_HASH_HERE',
    crossOrigin: 'anonymous',
    type: 'script',
  },
};

// 3. Use in component
import Script from 'next/script';
import { getScriptProps } from '@/lib/security/sri';

export default function Page() {
  return <Script {...getScriptProps('myLibrary')} />;
}
```

**Documentation:** See `/src/lib/security/sri.md` for complete guide

---

## SEC-024: WebAuthn/Passkeys

**Location:** `/src/lib/webauthn.ts`

**What it does:** Prepares for passwordless authentication using biometrics or security keys.

**Current status:** Stub implementation (functions throw "not yet implemented" errors)

**Check browser support:**

```typescript
import { isWebAuthnSupported, isPlatformAuthenticatorAvailable } from '@/lib/webauthn';

// Check if WebAuthn is available
if (isWebAuthnSupported()) {
  console.log('WebAuthn supported');
}

// Check for Face ID, Touch ID, Windows Hello
const hasPasskeys = await isPlatformAuthenticatorAvailable();
if (hasPasskeys) {
  // Show passkey option in UI
}
```

**To implement:**
1. Set up backend endpoints (`/api/webauthn/*`)
2. Uncomment production code in `webauthn.ts`
3. Test with multiple authenticators
4. See comments in file for complete implementation guide

---

## SEC-025: Privacy-Friendly Analytics

**Location:** `/src/lib/analytics.ts`

**What it does:** Cookie-free, privacy-first analytics compatible with Plausible, Umami, etc.

**Environment variables (.env.local):**
```bash
NEXT_PUBLIC_ANALYTICS_ENABLED=true
NEXT_PUBLIC_ANALYTICS_DOMAIN=yourdomain.com
NEXT_PUBLIC_ANALYTICS_ENDPOINT=https://plausible.io/api/event
```

**Track page views (automatic):**

```tsx
'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { trackPageView } from '@/lib/analytics';

export default function Layout({ children }) {
  const pathname = usePathname();

  useEffect(() => {
    trackPageView();
  }, [pathname]);

  return <>{children}</>;
}
```

**Track custom events:**

```tsx
import { trackEvent } from '@/lib/analytics';

// Simple event
<button onClick={() => trackEvent('signup_clicked')}>
  Sign Up
</button>

// Event with properties
<button onClick={() => trackEvent('plan_selected', { plan: 'pro' })}>
  Choose Pro
</button>
```

**Track outbound links:**

```tsx
import { trackOutboundLink } from '@/lib/analytics';

<a
  href="https://example.com"
  onClick={() => trackOutboundLink('https://example.com')}
>
  External Link
</a>
```

**Track file downloads:**

```tsx
import { trackFileDownload } from '@/lib/analytics';

<a
  href="/downloads/guide.pdf"
  onClick={() => trackFileDownload('guide.pdf')}
>
  Download
</a>
```

**Track 404 errors:**

```tsx
import { track404 } from '@/lib/analytics';

// In 404 page
useEffect(() => {
  track404();
}, []);
```

**Check status:**

```tsx
import { getAnalyticsStatus } from '@/lib/analytics';

const status = getAnalyticsStatus();
// { enabled: true, configured: true, domain: 'example.com', debug: false }
```

---

## Common Tasks

### Update security.txt before expiration

```bash
# Edit both files
vim frontend/public/security.txt
vim frontend/public/.well-known/security.txt

# Update Expires field to new date (at least 1 year in future)
Expires: 2027-12-31T23:59:59.000Z
```

### Add new CDN resource with SRI

```bash
# 1. Generate SRI hash
curl -s https://cdn.example.com/library.js | \
  openssl dgst -sha384 -binary | openssl base64 -A

# 2. Add to EXTERNAL_RESOURCES in src/lib/security/sri.ts
# 3. Update CSP in next.config.ts if needed
# 4. Use getScriptProps() or getStyleProps() in component
```

### Enable analytics in production

```bash
# 1. Choose platform (Plausible, Umami, etc.)
# 2. Update .env.local
NEXT_PUBLIC_ANALYTICS_ENABLED=true
NEXT_PUBLIC_ANALYTICS_DOMAIN=yourdomain.com
NEXT_PUBLIC_ANALYTICS_ENDPOINT=https://plausible.io/api/event

# 3. Add tracking to root layout (see SEC-025 above)
# 4. Deploy and verify in analytics dashboard
```

### Test WebAuthn support

```typescript
import { getBrowserPasskeySupport } from '@/lib/webauthn';

const support = getBrowserPasskeySupport();
console.log(support.message); // e.g., "Chrome supports passkeys"
```

### Generate SRI hash from command line

```bash
# For remote file
curl -s https://cdn.example.com/library.js | \
  openssl dgst -sha384 -binary | openssl base64 -A

# For local file
openssl dgst -sha384 -binary library.js | openssl base64 -A

# Output: base64 hash (add "sha384-" prefix)
```

---

## Security Headers Summary (from next.config.ts)

All requests include these security headers:

| Header | Value | Purpose |
|--------|-------|---------|
| Content-Security-Policy | See next.config.ts | Prevents XSS, injection attacks |
| X-Frame-Options | DENY | Prevents clickjacking |
| X-Content-Type-Options | nosniff | Prevents MIME sniffing |
| X-XSS-Protection | 1; mode=block | Legacy XSS protection |
| Referrer-Policy | strict-origin-when-cross-origin | Controls referrer information |
| Permissions-Policy | camera=(), microphone=()... | Restricts browser features |
| Strict-Transport-Security | max-age=63072000; includeSubDomains; preload | Forces HTTPS |

---

## File Locations

```
frontend/
├── public/
│   ├── security.txt                    # SEC-021
│   └── .well-known/
│       └── security.txt                # SEC-021
├── next.config.ts                      # SEC-022 (HSTS configuration)
├── .env.local.example                  # SEC-025 (analytics config)
└── src/
    └── lib/
        ├── analytics.ts                 # SEC-025
        ├── webauthn.ts                  # SEC-024
        └── security/
            ├── sri.md                   # SEC-023 (documentation)
            └── sri.ts                   # SEC-023 (utilities)
```

---

## Quick Checks

```bash
# Check security.txt
curl https://yourdomain.com/.well-known/security.txt

# Check HSTS header
curl -I https://yourdomain.com | grep -i strict-transport-security

# Check if analytics is enabled
grep NEXT_PUBLIC_ANALYTICS_ENABLED .env.local

# Check for CDN resources (should return nothing)
grep -r "cdn\." src/
grep -r "jsdelivr" src/
grep -r "unpkg" src/

# Check WebAuthn support in browser console
isWebAuthnSupported()
```

---

## Links

- **Full Documentation:** `/frontend/SECURITY_LOW_PRIORITY_IMPLEMENTATION.md`
- **SRI Guide:** `/frontend/src/lib/security/sri.md`
- **WebAuthn:** https://webauthn.guide/
- **HSTS Preload:** https://hstspreload.org/
- **SRI Hash Generator:** https://www.srihash.org/
- **Plausible Analytics:** https://plausible.io/
- **Umami Analytics:** https://umami.is/

---

## Support

For questions or issues:
- **Security:** security@ai-orchestra.example.com
- **Development:** dev@ai-orchestra.example.com
- **Documentation:** See `SECURITY_LOW_PRIORITY_IMPLEMENTATION.md`

---

**Last Updated:** 2025-12-08
**Version:** 1.0
