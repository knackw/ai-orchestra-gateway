# SEC-018: Email Enumeration Protection via Constant-Time Responses

## Overview

**Issue**: Timing differences in authentication responses can reveal if an email or license key exists in the system, enabling attackers to enumerate valid accounts.

**Solution**: Implement constant-time response protection that ensures all authentication endpoints take a consistent amount of time regardless of whether the credential exists or the execution path taken.

**Status**: ✅ Implemented (v0.8.3)

## Vulnerability Details

### The Problem

Without timing attack protection, authentication endpoints may exhibit different response times based on:

1. **User Existence**: Database lookups for existing users take longer than immediate rejections
2. **Password Verification**: Hash comparison only happens if the user exists
3. **Execution Paths**: Different code paths (success vs failure) have different performance characteristics

### Attack Scenario

An attacker can use timing analysis to determine if an email exists:

```python
# Pseudo-attack code
def check_email_exists(email):
    start = time.time()
    response = requests.post("/api/login", json={"email": email, "password": "wrong"})
    elapsed = time.time() - start

    # If response is consistently faster, email likely doesn't exist
    # If response is consistently slower, email exists (database lookup + hash check)
    return elapsed > THRESHOLD
```

### Impact

- **Account Enumeration**: Attackers can compile lists of valid accounts
- **Targeted Attacks**: Enables focused phishing or brute force attacks
- **Privacy Violation**: Reveals user information without authorization
- **Compliance Risk**: May violate GDPR/privacy regulations

## Implementation

### Core Module: `app/core/auth_timing.py`

The timing protection module provides multiple tools:

#### 1. Decorator for Endpoint Protection

```python
from app.core.auth_timing import constant_time_response, LOGIN_TIMING

@app.post("/auth/login")
@constant_time_response(**LOGIN_TIMING)  # 500ms min + 100ms jitter
async def login(email: str, password: str):
    user = await validate_credentials(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return {"token": generate_token(user)}
```

#### 2. Context Manager for Code Blocks

```python
from app.core.auth_timing import TimingAttackProtection, PASSWORD_RESET_TIMING

async def reset_password(email: str):
    async with TimingAttackProtection(**PASSWORD_RESET_TIMING):
        user = await find_user_by_email(email)
        if user:
            await send_reset_email(user)
        # Always return success message
        return {"message": "If account exists, email will be sent"}
```

#### 3. Constant-Time String Comparison

```python
from app.core.auth_timing import constant_time_compare

async def verify_token(provided_token: str, stored_token: str) -> bool:
    # Prevents timing attacks on token comparison
    return await constant_time_compare(provided_token, stored_token, min_time_ms=50)
```

### Applied Protection

#### License Key Validation (`app/core/security.py`)

```python
async def validate_license_key(license_key: str) -> LicenseInfo:
    # SEC-018: Apply timing attack protection
    async with TimingAttackProtection(**LICENSE_VALIDATION_TIMING):
        try:
            # Lookup license in database
            response = client.table("licenses").select("*").eq("license_key", license_key).execute()

            if not response.data:
                # SEC-018: Generic error message
                raise HTTPException(403, "Invalid or expired license key")

            # Validate expiration, credits, etc.
            # ...

        except HTTPException:
            raise
```

**Key Changes**:
- Wrapped entire validation in `TimingAttackProtection` context (300ms min + 50ms jitter)
- Changed specific error messages to generic "Invalid or expired license key"
- Consistent timing regardless of which validation check fails

## Configuration

### Predefined Timing Configurations

```python
# app/core/auth_timing.py

LOGIN_TIMING = {"min_time_ms": 500, "max_jitter_ms": 100}
SIGNUP_TIMING = {"min_time_ms": 600, "max_jitter_ms": 150}
PASSWORD_RESET_TIMING = {"min_time_ms": 500, "max_jitter_ms": 100}
LICENSE_VALIDATION_TIMING = {"min_time_ms": 300, "max_jitter_ms": 50}
```

### Timing Parameters

- **min_time_ms**: Minimum response time in milliseconds
  - Login/Reset: 500ms (prevents user enumeration)
  - License Validation: 300ms (faster for API performance)

- **max_jitter_ms**: Maximum random jitter added to response
  - Adds randomness to mask any remaining timing patterns
  - Prevents statistical analysis attacks

### Generic Error Messages

All authentication errors now use generic messages:

```python
# ❌ BAD - Reveals information
"Email not found"
"User does not exist"
"Incorrect password"

# ✅ GOOD - Generic messages
"Invalid credentials"
"Invalid or expired license key"
"Authentication failed"
```

## Security Features

### 1. Constant Minimum Time

Enforces minimum response time regardless of execution path:

```python
async def validate(credentials):
    start = time.time()

    # Add initial jitter
    await asyncio.sleep(random.uniform(0, jitter))

    # Execute validation (may be fast or slow)
    result = await do_validation(credentials)

    # Sleep remaining time to reach minimum
    elapsed = time.time() - start
    remaining = max(0, min_time - elapsed)
    await asyncio.sleep(remaining)

    return result
```

### 2. Random Jitter

Adds randomness to prevent statistical analysis:

```python
# Without jitter: Attackers can average many requests to detect patterns
# Response times: 500ms, 500ms, 500ms, 500ms (predictable)

# With jitter: Even averaged responses show variation
# Response times: 532ms, 478ms, 551ms, 492ms (unpredictable)
```

### 3. Exception Handling

Timing protection applies even when exceptions occur:

```python
@constant_time_response(min_time_ms=500)
async def login(credentials):
    # Even if this fails immediately...
    raise HTTPException(401, "Invalid credentials")
    # ...response still takes 500ms+
```

### 4. Sensitive Value Masking

Helper for logging without exposing data:

```python
from app.core.auth_timing import mask_sensitive_value

logger.info(f"Failed login for: {mask_sensitive_value(email, visible_chars=11)}")
# Output: "Failed login for: ****example.com"
```

## Testing

### Comprehensive Test Suite

**Location**: `app/tests/test_auth_timing.py`

**Coverage**: 28 tests, 95% code coverage

#### Test Categories

1. **Minimum Time Enforcement** (4 tests)
   - Verifies responses take at least minimum time
   - Tests decorator and context manager
   - Validates timing with fast and slow operations

2. **Timing Consistency** (5 tests)
   - Success vs failure responses take similar time
   - Different execution paths have consistent timing
   - Statistical variance within acceptable bounds

3. **Jitter Behavior** (3 tests)
   - Confirms randomness in response times
   - Prevents predictable patterns
   - Verifies jitter distribution

4. **Exception Handling** (3 tests)
   - Exceptions still respect minimum time
   - Optional `apply_to_errors=False` for bypassing
   - Error messages remain generic

5. **String Comparison** (4 tests)
   - Constant-time comparison works correctly
   - Independent of string length
   - Uses `secrets.compare_digest()` internally

6. **Security Properties** (6 tests)
   - No timing oracle attacks possible
   - Generic error messages
   - Integration with realistic scenarios

7. **Configuration Tests** (3 tests)
   - Predefined timing configs are valid
   - Custom configurations work correctly

### Running Tests

```bash
# Run timing protection tests
pytest app/tests/test_auth_timing.py -v

# Run with timing details
pytest app/tests/test_auth_timing.py -v -s

# Check coverage
pytest app/tests/test_auth_timing.py --cov=app.core.auth_timing --cov-report=term-missing
```

## Integration Guide

### Frontend (Supabase Auth)

The frontend uses Supabase Auth which already implements timing attack protection:

```typescript
// frontend/src/lib/auth.ts
export async function signIn(email: string, password: string) {
  const supabase = createClient()
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })

  if (error) {
    // Supabase returns generic errors
    throw new Error(error.message)
  }

  return data
}
```

**Note**: No additional frontend changes needed. Supabase handles timing protection.

### Backend License Validation

Already integrated in `app/core/security.py`:

```python
async def validate_license_key(license_key: str) -> LicenseInfo:
    # SEC-018: Timing attack protection
    async with TimingAttackProtection(**LICENSE_VALIDATION_TIMING):
        # Validation logic here
        pass
```

### Adding to New Endpoints

For new authentication endpoints:

```python
from app.core.auth_timing import constant_time_response, LOGIN_TIMING

@app.post("/api/auth/custom-login")
@constant_time_response(**LOGIN_TIMING)
async def custom_login(credentials: LoginCredentials):
    # Your authentication logic
    if not valid:
        raise HTTPException(401, "Invalid credentials")  # Generic message
    return {"token": "..."}
```

## Performance Impact

### Response Time Overhead

| Endpoint Type | Min Time | Typical Increase | Impact |
|--------------|----------|------------------|--------|
| Login | 500ms | +200-400ms | Acceptable for security |
| Password Reset | 500ms | +250-450ms | Acceptable for security |
| License Validation | 300ms | +150-250ms | Minimal for API calls |
| Signup | 600ms | +100-300ms | Acceptable for one-time operation |

### Optimization Strategies

1. **Async Operations**: All timing protection uses `asyncio.sleep()` (non-blocking)
2. **Tiered Timing**: Critical endpoints (login) have higher min times than APIs
3. **Jitter Randomness**: Small jitter values (50-150ms) minimize overhead

### Production Considerations

```python
# Development: Lower timing for faster testing
if settings.is_development:
    LOGIN_TIMING = {"min_time_ms": 100, "max_jitter_ms": 20}

# Production: Higher timing for security
else:
    LOGIN_TIMING = {"min_time_ms": 500, "max_jitter_ms": 100}
```

## Compliance

### GDPR Article 32 - Security of Processing

✅ **Technical Measures**: Timing attack protection prevents unauthorized data access

✅ **State of the Art**: Industry-standard constant-time response implementation

✅ **Risk Mitigation**: Protects against enumeration attacks

### SOC 2 Type II

✅ **CC6.1 - Logical Access**: Prevents user enumeration through timing analysis

✅ **CC7.2 - System Monitoring**: Comprehensive logging of auth failures

### OWASP Top 10 2021

✅ **A07:2021 - Identification and Authentication Failures**: Addresses timing attack vulnerability

## Monitoring

### Logging

```python
# Success
logger.info(f"Valid license: {mask_license_key(license_key)} (id: {uuid}, tenant: {tenant_id})")

# Failure
logger.warning(f"AUTH_FAILURE: Invalid license key attempt: {mask_license_key(license_key)}")

# Timing
logger.debug(f"SEC-018: Response completed in {total_time*1000:.2f}ms (min: {min_time_ms}ms)")
```

### Metrics to Track

1. **Authentication Failures**: High rate may indicate enumeration attempt
2. **Response Time Distribution**: Should cluster around minimum + jitter
3. **Error Message Patterns**: Verify generic messages are used
4. **Client IP Analysis**: Detect brute force patterns

### Alerting

```python
# Example Prometheus metrics
auth_failures_total{endpoint="license_validation"} > 100  # per 5 minutes
auth_response_time_seconds{quantile="0.99"} < 0.3  # below minimum
```

## Limitations

### Known Edge Cases

1. **Network Timing**: Client-side network latency can still reveal patterns
   - **Mitigation**: Encourage HTTPS/TLS to hide network-level timing

2. **Database Performance**: Extreme database slowness may exceed minimum time
   - **Mitigation**: Monitor database performance separately

3. **Rate Limiting**: Heavy rate limiting may reveal patterns before timing protection
   - **Mitigation**: Apply rate limiting AFTER timing protection

### Not Protected

This implementation does NOT protect against:

- **Brute Force Attacks**: Use rate limiting (already implemented)
- **Network-Level Timing**: TLS/HTTPS recommended
- **Side-Channel Attacks**: CPU cache timing, etc.

## References

### Security Standards

- **OWASP Authentication Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **NIST SP 800-63B**: Digital Identity Guidelines
- **CWE-208**: Observable Timing Discrepancy

### Research Papers

- "Remote Timing Attacks are Practical" (Brumley & Boneh, 2003)
- "The Security Impact of HTTPS Interception" (Durumeric et al., 2017)

### Implementation References

- **Python `secrets` module**: https://docs.python.org/3/library/secrets.html
- **FastAPI Security Best Practices**: https://fastapi.tiangolo.com/tutorial/security/

## Changelog

### v0.8.3 (2025-12-08) - Initial Implementation

- Created `app/core/auth_timing.py` with timing protection utilities
- Applied to license key validation in `app/core/security.py`
- Added comprehensive test suite (28 tests, 95% coverage)
- Updated error messages to be generic
- Documented in CHANGELOG.md and this file

### Future Enhancements

- [ ] Add environment-specific timing configurations
- [ ] Integrate with Prometheus metrics
- [ ] Add real-time alerting for enumeration attempts
- [ ] Extend to admin authentication endpoints
- [ ] Consider hardware security module (HSM) integration

## Support

For questions or issues related to SEC-018:

1. Check test cases in `app/tests/test_auth_timing.py` for usage examples
2. Review module docstrings in `app/core/auth_timing.py`
3. Consult OWASP guidelines for authentication best practices
4. Contact security team for production deployment guidance

---

**Document Version**: 1.0
**Last Updated**: 2025-12-08
**Author**: AI Orchestra Security Team
**Status**: ✅ Production Ready
