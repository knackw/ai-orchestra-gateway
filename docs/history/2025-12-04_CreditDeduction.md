# History: BILLING-001 Credit Deduction Logic

**Date:** 2025-12-04
**Task:** BILLING-001
**Status:** Completed
**Version:** 0.1.8

## Overview
Implemented atomic credit deduction system using Supabase RPC for race-condition-free billing.

## Changes

### Database
- **NEW:** `migrations/002_create_billing_functions.sql`
  - PostgreSQL RPC function `deduct_credits(license_key, amount)`
  - Atomic transaction with `FOR UPDATE` row lock
  - 4-step validation: exists, active, not expired, sufficient credits
  - Returns new balance or raises exception with error prefix

### Backend
- **NEW:** `app/services/billing.py`
  - `BillingService.deduct_credits()` - calls Supabase RPC
  - Error mapping: DB exceptions → HTTP status codes
    - 402: Insufficient credits
    - 403: Invalid/inactive/expired license
    - 500: Database errors

- **MODIFIED:** `app/api/v1/generate.py`
  - Added Step 4: Credit deduction after AI generation
  - Credits deducted ONLY after successful response
  - Billing errors propagated to user (402, 403, 500)

### Testing
- **NEW:** `app/tests/test_billing.py`
  - 6 unit tests (100% coverage)
  - Mocked Supabase client
  - Tests: success, insufficient credits, invalid/inactive/expired license, DB errors

- **MODIFIED:** `app/tests/test_generate.py`
  - Updated all 12 tests with `BillingService` mock
  - Verified billing called with correct token amount

## Test Results
```
18 passed in 3.10s
Coverage: 100% for billing.py, 100% for test_generate.py
```

## Technical Decisions

**1. Deduction Timing: AFTER Generation**
- User only pays for successful AI responses
- Better UX than pre-payment
- Small risk of "free" usage if billing fails (acceptable for MVP)

**2. Atomic RPC Function**
- PostgreSQL `FOR UPDATE` prevents race conditions
- All validation + deduction in single transaction
- Guarantees data consistency

**3. Error Codes**
- 402 Payment Required: Insufficient credits
- 403 Forbidden: Invalid/inactive/expired license
- 500 Internal Server Error: Database/unexpected errors

## Migration Status
⚠️ **Manual execution required**:
- Migration file: `migrations/002_create_billing_functions.sql`
- Execute in Supabase Dashboard → SQL Editor

## Next Steps
- Execute migration manually in Supabase
- Monitor billing logs in production
- Consider retry logic for network failures (future enhancement)
