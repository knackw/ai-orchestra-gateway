# AI Legal Ops Implementation Plan

**Last Updated:** 2025-11-29  
**Project Status:** Planning Phase  
**Current Phase:** Phase 1 (MVP Core)  
**Target Launch:** Q1 2026

---

## 🔍 Executive Summary

**AI Legal Ops** is an enterprise-grade, multi-tenant middleware platform designed to provide secure AI orchestration for SaaS applications. The system acts as a privacy-enforcing gateway between client applications and AI providers (Anthropic, Scaleway), ensuring DSGVO compliance through mandatory PII redaction, atomic billing transactions, and comprehensive tenant isolation.

### Business Value
- **For Tenants (SaaS Providers):** White-label AI integration without privacy risks
- **For End Users:** DSGVO-compliant AI services with transparent credit billing
- **For Operators:** Centralized management, audit trails, and monetization infrastructure

---

## 📊 Technical Architecture Overview

### System Components
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  SaaS Client    │────▶│  AI Legal Ops    │────▶│  AI Providers   │
│  Applications   │     │  Gateway (API)   │     │  (Anthropic)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Admin Dashboard │
                        │  (Management UI) │
                        └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Supabase        │
                        │  (PostgreSQL)    │
                        └──────────────────┘
```

### Core Services
1. **AI Gateway Service** (`app/services/ai_gateway.py`)
   - Provider abstraction (Anthropic, Scaleway)
   - Failover & retry logic
   - Request/response transformation

2. **Privacy Shield Service** (`app/services/privacy.py`)
   - PII detection (Email, Phone, IBAN, Names)
   - Regex-based redaction
   - Sanitized logging

3. **Billing Service** (`app/services/billing.py`)
   - Atomic credit deduction (Supabase RPC)
   - Usage tracking & analytics
   - Stripe integration for top-ups

4. **Admin Dashboard** (New - Phase 2)
   - Tenant management
   - License & credit monitoring
   - Analytics & audit logs

### Data Model
```sql
tenants (SaaS Providers)
  ├─ apps (Client Applications)
  │   └─ licenses (End Users)
  │       └─ usage_logs (Audit Trail)
```

---

## 🎯 Analysis Summary

### Technical Requirements
- **Runtime:** Python 3.11+ (FastAPI, Pydantic, httpx)
- **Database:** Supabase (PostgreSQL 15+, Frankfurt EU)
- **Deployment:** Docker Compose (Production), Supabase CLI (Local Dev)
- **QA:** Ruff (Linting), Pytest (100% coverage for core logic)
- **CI/CD:** GitHub Actions (automated tests + deployment)

### Regulatory & Compliance
- **DSGVO (GDPR):** EU data residency (Frankfurt), no PII to AI providers
- **Logging:** PII-sanitized logs only (DataPrivacyShield)
- **AVV:** Automated Data Processing Agreement workflows
- **Audit Trail:** Immutable usage logs for legal compliance

### Performance Targets
- **Latency:** < 200ms overhead for gateway logic
- **Availability:** 99.9% uptime (health checks, auto-restart)
- **Throughput:** Handle 100 req/s per instance (horizontal scaling via Docker)

---

## 📋 Tasks by Priority

### 🔴 Critical Priority (Phase 1 - MVP Core)

#### Infrastructure & Development Setup
- [ ] **DEV-001**: Setup Supabase CLI for local development (Docker-based)
- [ ] **DEV-002**: Create local `.env.example` with all required variables
- [ ] **INFRA-001**: Init Python/FastAPI Project Structure (Ruff + Pytest + Pre-commit)
- [ ] **INFRA-002**: Setup Production Supabase Project (Frankfurt) & Configure RLS
- [ ] **INFRA-003**: Configure Docker & CI/CD Pipeline (GitHub Actions)
- [ ] **INFRA-004**: Setup Health Check Endpoint (`/health`)

#### Core Gateway Logic
- [ ] **AI-001**: Implement Provider Interface (Abstract Base Class)
- [ ] **AI-002**: Implement Anthropic Adapter (Claude API)
- [ ] **AI-003**: Implement Scaleway Adapter (if applicable)
- [ ] **API-001**: Create `/v1/generate` Endpoint with Bearer Token Auth
- [ ] **API-002**: Implement API Key Validation Middleware

#### Privacy & Security
- [ ] **PRIVACY-001**: Implement DataPrivacyShield Class (Email, Phone, IBAN)
- [ ] **PRIVACY-002**: Add Logging Filter (Sanitize all logs)
- [ ] **PRIVACY-003**: Write Privacy Shield Unit Tests (100 test cases)

---

### 🟡 High Priority (Phase 2 - Billing & Multi-Tenancy)

#### Database Schema & Billing
- [ ] **DB-001**: Create Database Schema (tenants, apps, licenses, usage_logs)
- [ ] **DB-002**: Implement RLS Policies for Tenant Isolation
- [ ] **DB-003**: Create `deduct_credits` SQL Function (Atomic Transaction)
- [ ] **BILLING-001**: Implement Billing Service (Python wrapper for RPC)
- [ ] **BILLING-002**: Setup Tenant & API Key Management Service
- [ ] **BILLING-003**: Integrate Stripe Webhooks for Credit Top-up
- [ ] **BILLING-004**: Implement Usage Logging (Immutable Audit Trail)

#### Admin Dashboard
- [ ] **ADMIN-001**: Setup Admin UI Project (Next.js or Streamlit)
- [ ] **ADMIN-002**: Implement Tenant Management (CRUD)
- [ ] **ADMIN-003**: Implement License Management (View, Create, Deactivate)
- [ ] **ADMIN-004**: Build Credit Monitoring Dashboard (Charts)
- [ ] **ADMIN-005**: Add Usage Analytics (Top Tenants, API Calls)
- [ ] **ADMIN-006**: Implement Audit Log Viewer (Filterable)

#### Testing
- [ ] **TEST-001**: Implement Unit Tests for Billing Logic
- [ ] **TEST-002**: Implement Integration Tests (Mock AI Providers)
- [ ] **TEST-003**: Add E2E Tests for Admin Dashboard

---

### 🟢 Medium Priority (Phase 3 - Public Launch)

#### Security Hardening
- [ ] **SEC-001**: Implement Audit Logging for Privacy Events (Sanitized)
- [ ] **SEC-002**: Configure Rate Limiting (Redis-based)
- [ ] **SEC-003**: Add Request ID Tracing (for debugging)
- [ ] **SEC-004**: Implement IP Whitelisting (Optional per Tenant)

#### Legal & Compliance
- [ ] **LEGAL-001**: Implement AVV (Data Processing Agreement) Workflow
- [ ] **LEGAL-002**: Add Cookie Consent Banner (Admin UI)
- [ ] **LEGAL-003**: Generate Privacy Policy & Terms of Service

#### Monitoring & Observability
- [ ] **MONITOR-001**: Integrate Sentry for Error Tracking
- [ ] **MONITOR-002**: Setup Prometheus Metrics Exporter
- [ ] **MONITOR-003**: Create Grafana Dashboards (Latency, Errors, Credits)

---

### 🔵 Low Priority (Phase 4 - Optimization)

#### Performance & Resilience
- [ ] **AI-004**: Implement Failover Logic (Primary/Secondary Provider)
- [ ] **AI-005**: Add Retry Logic with Exponential Backoff
- [ ] **INFRA-005**: Optimize Docker Image Size (Multi-stage build)
- [ ] **API-003**: Add Response Caching Layer (Redis)

#### Advanced Features
- [ ] **ADMIN-007**: Add Multi-Language Support (i18n)
- [ ] **ADMIN-008**: Implement Role-Based Access Control (RBAC)
- [ ] **BILLING-005**: Add Invoice Generation (PDF)

---

## 🏗️ Development Workflow

### Local Development Setup

1. **Install Supabase CLI**
   ```bash
   npm install -g supabase
   supabase init
   supabase start  # Starts local PostgreSQL + Studio
   ```

2. **Setup Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Run Locally**
   ```bash
   uvicorn app.main:app --reload
   ```

### Testing Strategy
```bash
# Linting
ruff check .

# Unit Tests
pytest tests/ --cov=app --cov-report=term-missing

# Integration Tests
pytest tests/integration/ -v
```

---

## 📏 Task Formatting

**Kategorien:**
- `AI`: Gateway, Provider Adapters, Prompt Management
- `PRIVACY`: PII Shield, Redaction Logic
- `BILLING`: Credit System, Stripe, Usage Tracking
- `API`: FastAPI, Pydantic Models, Auth
- `INFRA`: Docker, Supabase, Redis, CI/CD
- `ADMIN`: Admin Dashboard, Tenant/License Management
- `DEV`: Local Development Setup, Tooling
- `TEST`: Unit Tests, Integration Tests, Security Tests
- `SEC`: Security Hardening, Rate Limiting, Audit Logs
- `LEGAL`: DSGVO, AVV, Privacy Policy
- `MONITOR`: Observability, Logging, Metrics

---

## 🎯 Implementation Guidelines

### Core Principles
1. **Privacy First:** Keine persönlichen Daten (PII) verlassen das System Richtung AI-Provider
2. **Security:** Strikte Tenant-Isolation und API-Key Validierung bei jedem Request
3. **Reliability:** Graceful Handling von AI-Provider Ausfällen mit Retry-Logik
4. **Auditability:** Jede Transaktion wird in `usage_logs` gespeichert (immutable)
5. **Developer Experience:** Lokale Entwicklung mit Supabase CLI (kein Cloud-Zwang)

### Code Quality Standards
- **Type Hints:** Mandatory für alle Public Functions
- **Docstrings:** Google-Style für alle Services
- **Test Coverage:** Minimum 90% für `app/services/`
- **Linting:** Ruff must pass (no warnings)

### Deployment Checklist
- [ ] All tests passing (pytest + ruff)
- [ ] Environment variables documented in `.env.example`
- [ ] Database migrations applied (Supabase)
- [ ] Health check endpoint returns 200
- [ ] Admin dashboard deployed and accessible

---

## 📊 Success Metrics

### Phase 1 (MVP)
- ✅ 100% PII redaction in test suite
- ✅ < 200ms gateway overhead
- ✅ 90%+ test coverage

### Phase 2 (Billing)
- ✅ 0 race conditions in billing (atomic RPC)
- ✅ Stripe integration functional
- ✅ Admin dashboard operational

### Phase 3 (Launch)
- ✅ 99.9% uptime
- ✅ DSGVO audit ready
- ✅ Production monitoring active

---

## 🚀 Next Steps

1. **Immediate:** Review and approve this plan
2. **Week 1:** Setup local dev environment (Supabase CLI + FastAPI)
3. **Week 2-3:** Implement MVP Core (Gateway + Privacy Shield)
4. **Week 4-5:** Build Admin Dashboard + Billing
5. **Week 6:** Security hardening + QA
6. **Week 7:** Soft launch + monitoring

---

**Document Version:** 2.0  
**Contributors:** AI Solutions Architect
