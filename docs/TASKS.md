# Implementation Tasks: AI Legal Ops

**Last Updated:** 2025-11-30  
**Status:** 🔴 Phase 1 - MVP Core in Progress  
**Target Completion:** Week 7 (Q1 2026)

---

## 📊 Executive Summary

This document tracks the implementation tasks for the **AI Legal Ops** multi-tenant AI gateway. Our immediate goal is to complete **Phase 1 (MVP Core)** within 2-3 weeks, establishing the foundational gateway infrastructure with privacy enforcement and local development capabilities.

**Current Focus:** Setting up local development environment with Supabase CLI and implementing core gateway + privacy shield logic.

**Blockers:** None  
**Team Size:** 1-2 developers  


---

## 🔴 Phase 1: Infrastructure & MVP Core (Weeks 1-3)

### 1.1 Local Development Setup

- [x] **DEV-001**: Install Supabase CLI
  - Install via `npm install supabase`
  - Initialize project with `npx supabase init`
  - Start local instance with `npx supabase start`
  - Verify Studio UI at `http://localhost:54323`
  
- [x] **DEV-002**: Create comprehensive `.env.example`
  - Document all required environment variables
  - Include Supabase local/production URLs
  - Add AI provider API keys (Anthropic, Scaleway)
  - Add Stripe test keys
  - Include example values for clarity

### 1.2 Project Structure & Infrastructure

- [x] **INFRA-001**: Initialize Python/FastAPI Project
  - Create directory structure (`app/`, `app/services/`, `app/api/`, `app/core/`, `app/tests/`)
  - Setup `pyproject.toml` with Ruff configuration
  - Configure pre-commit hooks (Ruff, pytest)
  - Create `requirements.txt` with dependencies (FastAPI, Pydantic, httpx, pytest, supabase-py)
  
- [x] **INFRA-002**: Setup Production Supabase (Frankfurt)
  - Create Supabase project in Frankfurt region
  - Generate API keys (anon, service_role)
  - Configure connection pooling
  - Test connection from local environment
  
- [x] **INFRA-003**: Configure Docker & CI/CD
  - Write production `Dockerfile` (multi-stage build)
  - Create `docker-compose.yml` for local testing
  - Setup GitHub Actions workflow (`.github/workflows/ci-cd.yaml`)
  - Configure automated linting (Ruff) + testing (pytest)
  
- [x] **INFRA-004**: Implement Health Check Endpoint
  - Create `/health` endpoint in FastAPI
  - Return database connection status
  - Include uptime metrics
  - Add to Docker healthcheck

### 1.3 Core Gateway Logic

- [x] **AI-001**: Implement Abstract Provider Interface
  - Create `app/services/ai_gateway.py`
  - Define `AIProvider` base class (Abstract)
  - Methods: `generate(prompt: str) -> tuple[str, int]` (text, token_count)
  - Add provider registry pattern
  
- [x] **AI-002**: Implement Anthropic Adapter
  - Create `AnthropicProvider` class
  - Integrate with Claude API (httpx client)
  - Handle authentication (Bearer token)
  - Parse response and extract token usage
  
- [ ] **AI-003**: Implement Scaleway Adapter (Optional)
  - Create `ScalewayProvider` class
  - Follow same interface as Anthropic
  - Add as secondary provider
  
- [x] **API-001**: Create `/v1/generate` Endpoint
  - POST endpoint accepting `{ "prompt": str, "license_key": str }`
  - Return `{ "content": str, "tokens_used": int, "credits_deducted": int }`
  - Integrate with AI Gateway
  - Add request validation (Pydantic models)
  
- [x] **API-002**: Implement API Key Validation Middleware
  - Create `app/core/security.py`
  - Validate `X-License-Key` header
  - Query Supabase for license validity
  - Return 403 if invalid/expired

### 1.4 Privacy & Security

- [x] **PRIVACY-001**: Implement DataPrivacyShield
  - Create `app/services/privacy.py`
  - Define regex patterns (Email, Phone, IBAN, German names if needed)
  - Implement `sanitize(text: str) -> tuple[str, bool]` method
  - Replace PII with placeholders (`<EMAIL_REMOVED>`)
  
- [ ] **PRIVACY-002**: Add Logging Filter
  - Create custom logging filter class
  - Apply `DataPrivacyShield.sanitize()` to all log messages
  - Configure in `app/main.py`
  - Test that PII never appears in logs
  
- [ ] **PRIVACY-003**: Write Privacy Shield Unit Tests
  - Test email detection (10+ formats)
  - Test phone number detection (German formats)
  - Test IBAN detection
  - Test edge cases (nested PII, URLs with @)
  - Achieve 100% coverage for `privacy.py`

---

## 🟡 Phase 2: Billing, Multi-Tenancy & Admin UI (Weeks 4-5)

### 2.1 Database Schema & Billing

- [ ] **DB-001**: Create Database Schema
  - Write SQL migration for `tenants`, `apps`, `licenses`, `usage_logs` tables
  - Apply to local Supabase via `supabase db push`
  - Apply to production Supabase
  - Verify schema integrity
  
- [ ] **DB-002**: Implement RLS Policies
  - Create RLS policies for tenant isolation
  - Ensure tenants can only access their own data
  - Test with multiple test tenants
  
- [ ] **DB-003**: Create `deduct_credits` SQL Function
  - Write PostgreSQL function for atomic credit deduction
  - Ensure transaction safety (check balance before deduct)
  - Return boolean (success/failure)
  - Test race conditions with concurrent requests
  
- [ ] **BILLING-001**: Implement Billing Service
  - Create `app/services/billing.py`
  - Python wrapper for `deduct_credits` RPC
  - Handle insufficient balance errors
  - Add retry logic for network failures
  
- [ ] **BILLING-002**: Setup Tenant & API Key Management
  - Create `/admin/tenants` CRUD endpoints (internal use only)
  - Create `/admin/licenses` CRUD endpoints
  - Generate secure API keys (UUID-based)
  - Store hashed keys in database
  
- [ ] **BILLING-003**: Integrate Stripe Webhooks
  - Implement `/webhooks/stripe` endpoint
  - Handle `checkout.session.completed` event
  - Credit tenant account on successful payment
  - Send confirmation email (optional)
  
- [ ] **BILLING-004**: Implement Usage Logging
  - Insert row into `usage_logs` after every AI call
  - Store: license_id, tokens_used, credits_deducted, timestamp
  - Make table immutable (no DELETE or UPDATE permissions)
  - Query for analytics

### 2.2 Admin Dashboard

- [ ] **ADMIN-001**: Setup Admin UI Project
  - Choose framework: Next.js (App Router) or Streamlit (Python)
  - Initialize project in `admin/` directory
  - Configure Supabase client for authentication
  
- [ ] **ADMIN-002**: Implement Tenant Management
  - Create tenants list view (table)
  - Add create tenant form
  - Add edit/deactivate tenant actions
  - Display tenant statistics (total credits used)
  
- [ ] **ADMIN-003**: Implement License Management
  - Create licenses list view (filterable by tenant)
  - Add create license form (select tenant, set plan, initial credits)
  - Add deactivate license action
  - Display license usage history
  
- [ ] **ADMIN-004**: Build Credit Monitoring Dashboard
  - Create dashboard page with charts (Chart.js or Recharts)
  - Display total credits sold vs used
  - Show top 10 tenants by usage
  - Add date range filter
  
- [ ] **ADMIN-005**: Add Usage Analytics
  - Display total API calls per day/week/month
  - Show average tokens per request
  - Display AI provider split (Anthropic vs Scaleway)
  - Export to CSV functionality
  
- [ ] **ADMIN-006**: Implement Audit Log Viewer
  - Create paginated table of `usage_logs`
  - Add filters: tenant, license, date range
  - Display: timestamp, license_key, prompt (sanitized!), tokens, credits
  - Add search functionality

### 2.3 Testing

- [ ] **TEST-001**: Unit Tests for Billing Logic
  - Test `deduct_credits` with sufficient balance
  - Test `deduct_credits` with insufficient balance
  - Test concurrent requests (race conditions)
  - Mock Supabase RPC calls
  
- [ ] **TEST-002**: Integration Tests (Mock AI Providers)
  - Mock Anthropic API responses
  - Test full request flow (API → Privacy → Gateway → Billing)
  - Test error handling (AI provider timeout)
  - Test credit deduction on successful request
  
- [ ] **TEST-003**: E2E Tests for Admin Dashboard
  - Use Playwright or Cypress
  - Test tenant creation flow
  - Test license creation and deactivation
  - Test credit top-up flow (mock Stripe)

---

## 🟢 Phase 3: Security Hardening & Public Launch (Week 6)

### 3.1 Security

- [ ] **SEC-001**: Implement Audit Logging
  - Log all privacy shield activations
  - Log all authentication failures
  - Log all credit deductions
  - Ensure logs are sanitized (no PII)
  
- [ ] **SEC-002**: Configure Rate Limiting (Redis)
  - Setup Redis instance (Docker)
  - Install `slowapi` or `fastapi-limiter`
  - Apply rate limits: 100 req/min per license
  - Return 429 on limit exceeded
  
- [ ] **SEC-003**: Add Request ID Tracing
  - Generate unique request ID per API call
  - Include in logs and responses (X-Request-ID header)
  - Enable end-to-end debugging
  
- [ ] **SEC-004**: Implement IP Whitelisting (Optional)
  - Add `allowed_ips` column to `tenants` table
  - Validate request IP against whitelist
  - Return 403 on mismatch

### 3.2 Legal & Compliance

- [ ] **LEGAL-001**: Implement AVV Workflow
  - Create AVV template (German Data Processing Agreement)
  - Add digital signature flow (DocuSign or manual)
  - Store signed AVV reference in `tenants` table
  
- [ ] **LEGAL-002**: Add Cookie Consent Banner
  - Add to Admin UI (if using cookies)
  - Comply with DSGVO requirements
  - Use consent management platform (e.g., Cookiebot)
  
- [ ] **LEGAL-003**: Generate Privacy Policy & ToS
  - Draft privacy policy (DSGVO-compliant)
  - Draft terms of service
  - Add to public-facing documentation

### 3.3 Monitoring & Observability

- [ ] **MONITOR-001**: Integrate Sentry for Error Tracking
  - Install `sentry-sdk[fastapi]`
  - Configure DSN in environment variables
  - Test by triggering an error
  - Set up alerts for critical errors
  
- [ ] **MONITOR-002**: Setup Prometheus Metrics Exporter
  - Install `prometheus-fastapi-instrumentator`
  - Expose `/metrics` endpoint
  - Track: request count, latency, error rate
  
- [ ] **MONITOR-003**: Create Grafana Dashboards
  - Setup Grafana instance (Docker)
  - Connect to Prometheus data source
  - Create dashboards: API latency, credits usage, errors
  - Add alerting rules

---

## 🔵 Phase 4: Optimization & Advanced Features (Week 7+)

### 4.1 Performance & Resilience

- [ ] **AI-004**: Implement Failover Logic
  - Add primary/secondary provider configuration
  - Retry with secondary if primary fails
  - Log provider switch events
  
- [ ] **AI-005**: Add Retry Logic with Exponential Backoff
  - Use `tenacity` library
  - Retry on 5xx errors (up to 3 attempts)
  - Exponential backoff: 1s, 2s, 4s
  
- [ ] **INFRA-005**: Optimize Docker Image Size
  - Use multi-stage build
  - Remove dev dependencies from production image
  - Target: < 200MB final image
  
- [ ] **API-003**: Add Response Caching Layer
  - Setup Redis for caching
  - Cache identical prompts for 1 hour
  - Deduct 0 credits for cached responses

### 4.2 Advanced Features

- [ ] **ADMIN-007**: Add Multi-Language Support (i18n)
  - Setup next-i18next or similar
  - Translate UI to English + German
  - Add language switcher
  
- [ ] **ADMIN-008**: Implement Role-Based Access Control
  - Add `roles` table (admin, viewer)
  - Restrict tenant deletion to admins only
  - Add user management UI
  
- [ ] **BILLING-005**: Add Invoice Generation
  - Generate monthly PDF invoices per tenant
  - Include: usage breakdown, total credits, payment status
  - Send via email (SendGrid/Postmark)

---

## 📅 Timeline & Milestones

| Phase | Duration | Key Deliverables | Status |
|-------|----------|------------------|--------|
| **Phase 1** (MVP Core) | Weeks 1-3 | Gateway + Privacy + Local Dev | 🔴 In Progress (0%) |
| **Phase 2** (Billing & Admin) | Weeks 4-5 | Database + Admin UI + Billing | ⚪ Not Started |
| **Phase 3** (Launch Prep) | Week 6 | Security + Monitoring + Legal | ⚪ Not Started |
| **Phase 4** (Optimization) | Week 7+ | Caching + Failover + Advanced Features | ⚪ Not Started |

### Key Milestones
- ✅ **Week 1 End:** Local dev environment ready, FastAPI boilerplate running
- ✅ **Week 2 End:** Privacy Shield + AI Gateway functional (e2e test passing)
- ✅ **Week 3 End:** Phase 1 complete, Docker deployment successful
- ✅ **Week 5 End:** Admin UI live, billing functional, first test tenant onboarded
- ✅ **Week 6 End:** Security audit passed, monitoring operational
- 🚀 **Week 7:** Public soft launch

---

## 📊 Success Metrics

### Quality Gates (Must Pass Before Next Phase)

**Phase 1 Exit Criteria:**
- ✅ 100% PII redaction in test suite (50+ test cases)
- ✅ Gateway latency < 200ms (measured via pytest-benchmark)
- ✅ All unit tests passing (90%+ coverage)
- ✅ Ruff linting passing (0 warnings)
- ✅ Docker build successful

**Phase 2 Exit Criteria:**
- ✅ 0 race conditions in billing (tested with 100 concurrent requests)
- ✅ Admin UI functional (all CRUD operations working)
- ✅ Stripe integration tested (sandbox mode)

**Phase 3 Exit Criteria:**
- ✅ Penetration test passed (no critical vulnerabilities)
- ✅ DSGVO compliance audit ready
- ✅ 99.9% uptime in staging (1 week monitoring)

### KPIs (Post-Launch)
- **Uptime:** > 99.9%
- **API Latency (P95):** < 500ms
- **Error Rate:** < 0.1%
- **Customer NPS:** > 50

---

## 🎯 Current Sprint (Week 1)

**Focus:** Setup local development environment and project structure

**This Week's Tasks:**
- [ ] **DEV-001**: Install Supabase CLI
- [x] **DEV-002**: Create `.env.example`
- [x] **INFRA-001**: Init FastAPI project
- [x] **INFRA-002**: Setup Supabase (production)

**Expected Outcome:** Development environment ready for coding

---

**Document Version:** 2.0  
**Owner:** Technical Lead  
**Last Review:** 2025-11-29
