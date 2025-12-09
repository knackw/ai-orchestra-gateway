# SEC-020: Frontend Audit Logging - Quick Reference

**Version:** 0.8.5 | **Status:** ✅ Production Ready

## Quick Start

### Frontend Usage

```typescript
import { logAuditEvent, AuditEvent, auditAuth } from '@/lib/audit';

// Configure once at app startup
configureAuditLogger({
  baseUrl: '/api/v1',
  clientVersion: '2.0.0',
});

// Use helper functions
await auditAuth.loginSuccess(userId, tenantId, { method: 'email' });
await auditAuth.loginFailure({ reason: 'invalid_password' }, 'Invalid credentials');
await auditAuth.logout(userId, tenantId);
```

### Backend API

```bash
# Log an event
curl -X POST http://localhost:9001/api/v1/audit/log \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "LOGIN_SUCCESS",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    "details": {"method": "email"},
    "success": true
  }'

# Get all event types
curl http://localhost:9001/api/v1/audit/event-types
```

## Helper Functions

### Authentication
```typescript
auditAuth.loginSuccess(userId, tenantId, details?)
auditAuth.loginFailure(details?, errorMessage?)
auditAuth.logout(userId, tenantId)
auditAuth.sessionTimeout(userId, tenantId)
auditAuth.sessionRefresh(userId, tenantId)
```

### API Keys
```typescript
auditApiKeys.create(userId, tenantId, details?)
auditApiKeys.delete(userId, tenantId, details?)
auditApiKeys.rotate(userId, tenantId, details?)
```

### Settings
```typescript
auditSettings.passwordChange(userId, tenantId)
auditSettings.emailChange(userId, tenantId, details?)
auditSettings.enable2FA(userId, tenantId)
auditSettings.disable2FA(userId, tenantId)
auditSettings.profileUpdate(userId, tenantId, details?)
```

### Admin
```typescript
auditAdmin.tenantCreate(userId, tenantId, details?)
auditAdmin.tenantDelete(userId, tenantId, details?)
auditAdmin.licenseCreate(userId, tenantId, details?)
auditAdmin.licenseDelete(userId, tenantId, details?)
auditAdmin.userRoleChange(userId, tenantId, details?)
```

### Security
```typescript
auditSecurity.suspiciousActivity(userId, tenantId, details?)
auditSecurity.rateLimitExceeded(userId, details?)
auditSecurity.ipBlocked(details?)
auditSecurity.invalidSession(userId, details?)
```

## Event Types

### 🔐 Authentication (5 events)
- `LOGIN_SUCCESS` - Successful login
- `LOGIN_FAILURE` - Failed login
- `LOGOUT` - User logout
- `SESSION_TIMEOUT` - Session expired
- `SESSION_REFRESH` - Session refreshed

### 🔑 Authorization (5 events)
- `API_KEY_CREATE` - API key created
- `API_KEY_DELETE` - API key deleted
- `API_KEY_ROTATE` - API key rotated
- `PERMISSION_DENIED` - Access denied
- `ACCESS_TOKEN_REFRESH` - Token refreshed

### ⚙️ Settings (7 events)
- `PASSWORD_CHANGE` - Password changed
- `EMAIL_CHANGE` - Email changed
- `2FA_ENABLE` - 2FA enabled
- `2FA_DISABLE` - 2FA disabled
- `PROFILE_UPDATE` - Profile updated
- `NOTIFICATION_SETTINGS_CHANGE` - Notifications changed
- `LANGUAGE_CHANGE` - Language changed

### 👑 Admin (10 events)
- `TENANT_CREATE/DELETE/UPDATE`
- `LICENSE_CREATE/DELETE/UPDATE`
- `USER_ROLE_CHANGE/DELETE`
- `APP_CREATE/DELETE`

### 🛡️ Security (6 events)
- `SUSPICIOUS_ACTIVITY` - Suspicious behavior
- `RATE_LIMIT_EXCEEDED` - Rate limit hit
- `IP_BLOCKED` - IP blocked
- `MFA_CHALLENGE` - MFA challenge
- `CSRF_TOKEN_MISMATCH` - CSRF error
- `INVALID_SESSION` - Invalid session

## Configuration

```typescript
configureAuditLogger({
  baseUrl: '/api/v1',              // API endpoint
  clientVersion: '2.0.0',          // Frontend version
  debug: false,                    // Console logging
  enableOfflineQueue: true,        // Queue when offline
  maxQueueSize: 100,               // Max queued events
});
```

## Offline Queue

```typescript
// Get queue statistics
const stats = getOfflineQueueStats();
console.log(`Queue size: ${stats.size}, Processing: ${stats.isProcessing}`);

// Manually flush queue
await flushOfflineQueue();

// Clear queue (use with caution)
clearOfflineQueue();
```

## Database Schema

```sql
security_audit_events (
  id UUID PRIMARY KEY,
  user_id UUID,
  tenant_id UUID,
  event_type TEXT NOT NULL,
  event_category TEXT NOT NULL,  -- authentication, authorization, settings, admin, security
  severity TEXT NOT NULL,         -- info, warning, critical
  ip_address INET,
  user_agent TEXT,
  client_version TEXT,
  details JSONB,
  success BOOLEAN NOT NULL,
  error_message TEXT,
  created_at TIMESTAMP
)
```

## Rate Limiting

- **Limit:** 100 requests/minute per IP
- **Status Code:** 429 Too Many Requests
- **Applies to:** POST /api/v1/audit/log

## Security Features

- ✅ Immutable audit trail (UPDATE/DELETE blocked)
- ✅ Row-level security (users see own events)
- ✅ Client metadata capture (IP, user agent)
- ✅ Event severity classification
- ✅ Rate limiting to prevent flooding
- ✅ Offline queue for reliability

## Testing

```bash
# Backend tests
pytest app/tests/test_audit.py -v

# Frontend tests
cd frontend && npm test -- src/lib/audit.test.ts

# Test coverage
pytest app/tests/test_audit.py --cov=app.api.v1.audit
```

## Common Patterns

### Login Flow
```typescript
// On login attempt
try {
  const result = await login(email, password);
  await auditAuth.loginSuccess(result.user.id, result.user.tenant_id, {
    method: 'email',
    remember_me: rememberMe,
  });
} catch (error) {
  await auditAuth.loginFailure(
    { email, reason: error.code },
    error.message
  );
  throw error;
}
```

### API Key Management
```typescript
// On API key creation
const key = await createApiKey(name, permissions);
await auditApiKeys.create(user.id, user.tenant_id, {
  key_name: name,
  permissions,
});
```

### Settings Update
```typescript
// On password change
await changePassword(oldPassword, newPassword);
await auditSettings.passwordChange(user.id, user.tenant_id);
```

### Suspicious Activity Detection
```typescript
// On multiple failed login attempts
if (failedAttempts >= 5) {
  await auditSecurity.suspiciousActivity(user.id, user.tenant_id, {
    reason: 'multiple_failed_login_attempts',
    count: failedAttempts,
    timeframe: '5 minutes',
  });
}
```

## Troubleshooting

### Events not appearing in database
1. Check API endpoint is accessible: `GET /api/v1/audit/event-types`
2. Verify rate limit not exceeded (429 status)
3. Check network console for errors
4. Enable debug mode: `configureAuditLogger({ debug: true })`

### Offline queue not flushing
1. Check network connectivity
2. Verify queue stats: `getOfflineQueueStats()`
3. Manually flush: `await flushOfflineQueue()`
4. Check max queue size not exceeded

### Events not visible to users
1. Verify RLS policies are enabled
2. Check user_id matches authenticated user
3. Use service role for admin queries

## Files Reference

- **Migration:** `migrations/012_create_security_audit_events.sql`
- **Backend API:** `app/api/v1/audit.py`
- **Frontend Library:** `frontend/src/lib/audit.ts`
- **Backend Tests:** `app/tests/test_audit.py`
- **Frontend Tests:** `frontend/src/lib/audit.test.ts`
- **Documentation:** `docs/history/2025-12-08_SEC-020_Frontend_Audit_Logging.md`

## Support

For detailed implementation guide, see:
- `docs/history/2025-12-08_SEC-020_Frontend_Audit_Logging.md`
- `CHANGELOG.md` - Version 0.8.5

---

**Version:** 0.8.5 | **Last Updated:** 2025-12-08
