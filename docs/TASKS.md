# Implementation Tasks: AI Legal Ops

**Last Updated:** 2025-12-09
**Status:** ✅ Phase 1-6 + Phase 9 Complete | Frontend (FRONTEND-001 to FRONTEND-019) Complete
**Target Completion:** Week 10 (Q1 2026)

---

## 📊 Executive Summary

This document tracks the implementation tasks for the **AI Legal Ops** multi-tenant AI gateway. Our immediate goal is to complete **Phase 1 (MVP Core)** within 2-3 weeks, establishing the foundational gateway infrastructure with privacy enforcement and local development capabilities.

**Current Focus:** Phase 6 Complete - All Frontend Tasks Implemented

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
  
- [x] **AI-003**: Implement Scaleway Adapter (Optional)
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
  
- [x] **PRIVACY-002**: Add Logging Filter
  - Create custom logging filter class
  - Apply `DataPrivacyShield.sanitize()` to all log messages
  - Configure in `app/main.py`
  - Test that PII never appears in logs
  
- [x] **PRIVACY-003**: Write Privacy Shield Unit Tests
  - Test email detection (10+ formats)
  - Test phone number detection (German formats)
  - Test IBAN detection
  - Test edge cases (nested PII, URLs with @)
  - Achieve 100% coverage for `privacy.py`

---

## 🟡 Phase 2: Billing, Multi-Tenancy & Admin UI (Weeks 4-5)

### 2.1 Database Schema & Billing

- [x] **DB-001**: Create Database Schema
  - Write SQL migration for `tenants`, `apps`, `licenses`, `usage_logs` tables
  - Apply to local Supabase via `supabase db push`
  - Apply to production Supabase
  - Verify schema integrity
  
- [x] **DB-002**: Implement RLS Policies
  - Create RLS policies for tenant isolation
  - Ensure tenants can only access their own data
  - Test with multiple test tenants
  
- [x] **DB-003**: Create `deduct_credits` SQL Function
  - Write PostgreSQL function for atomic credit deduction
  - Ensure transaction safety (check balance before deduct)
  - Return boolean (success/failure)
  - Test race conditions with concurrent requests
  
- [x] **BILLING-001**: Implement Billing Service
  - Create `app/services/billing.py`
  - Python wrapper for `deduct_credits` RPC
  - Handle insufficient balance errors
  - Add retry logic for network failures
  
- [x] **BILLING-002**: Setup Tenant & API Key Management
  - Create `/admin/tenants` CRUD endpoints (internal use only)
  - Create `/admin/licenses` CRUD endpoints
  - Generate secure API keys (UUID-based)
  - Store hashed keys in database
  
- [x] **BILLING-003**: Integrate Stripe Webhooks
  - Implement `/webhooks/stripe` endpoint
  - Handle `checkout.session.completed` event
  - Credit tenant account on successful payment
  - Send confirmation email (optional)
  
- [x] **BILLING-004**: Implement Usage Logging
  - Insert row into `usage_logs` after every AI call
  - Store: license_id, tokens_used, credits_deducted, timestamp
  - Make table immutable (no DELETE or UPDATE permissions)
  - Query for analytics

### 2.2 Admin Dashboard
  - Add create license form (select tenant, set plan, initial credits)
  - Add deactivate license action
  - Add deactivate license action
  - Display license usage history

- [x] **ADMIN-003**: Implement Application Management API
  - Create `/admin/apps` CRUD endpoints
  - Allow tenants to manage their own apps
  - Include validation and soft delete

  
- [x] **ADMIN-004**: Build Credit Monitoring Dashboard
  - Create dashboard page with charts (Chart.js or Recharts)
  - Display total credits sold vs used
  - Show top 10 tenants by usage
  - Add date range filter
  
- [x] **ADMIN-005**: Add Usage Analytics
  - Display total API calls per day/week/month
  - Show average tokens per request
  - Display AI provider split (Anthropic vs Scaleway)
  - Export to CSV functionality
  
- [x] **ADMIN-006**: Implement Audit Log Viewer
  - Create paginated table of `usage_logs`
  - Add filters: tenant, license, date range
  - Display: timestamp, license_key, prompt (sanitized!), tokens, credits
  - Add search functionality

### 2.3 Testing

- [x] **TEST-001**: Unit Tests for Billing Logic
  - Test `deduct_credits` with sufficient balance
  - Test `deduct_credits` with insufficient balance
  - Test concurrent requests (race conditions)
  - Mock Supabase RPC calls
  
- [x] **TEST-002**: Integration Tests (Mock AI Providers)
  - Mock Anthropic API responses
  - Test full request flow (API → Privacy → Gateway → Billing)
  - Test error handling (AI provider timeout)
  - Test credit deduction on successful request
  
- [x] **TEST-003**: E2E Tests for Admin Dashboard
  - Use Playwright or Cypress
  - Test tenant creation flow
  - Test license creation and deactivation
  - Test credit top-up flow (mock Stripe)
  - *Implemented in `app/tests/test_e2e_admin.py` with 26 comprehensive tests*

---

## 🟢 Phase 3: Security Hardening & Public Launch (Week 6)

### 3.1 Security

- [x] **SEC-001**: Implement Audit Logging
  - Log all privacy shield activations
  - Log all authentication failures
  - Log all credit deductions
  - Ensure logs are sanitized (no PII)
  
- [x] **SEC-002**: Configure Rate Limiting (Redis)
  - Setup Redis instance (Docker)
  - Install `slowapi` or `fastapi-limiter`
  - Apply rate limits: 100 req/min per license
  - Return 429 on limit exceeded
  
- [x] **SEC-003**: Add Request ID Tracing
  - Generate unique request ID per API call
  - Include in logs and responses (X-Request-ID header)
  - Enable end-to-end debugging
  
- [x] **SEC-004**: Implement IP Whitelisting (Optional)
  - Add `allowed_ips` column to `tenants` table
  - Validate request IP against whitelist
  - Return 403 on mismatch
  - *Implemented in `app/core/ip_whitelist.py` with CIDR support*

### 3.2 Legal & Compliance

- [x] **LEGAL-001**: Implement AVV Workflow (Backend)
  - Create AVV template (German Data Processing Agreement)
  - Add digital signature flow (DocuSign or manual)
  - Store signed AVV reference in `tenants` table
  
- [x] **LEGAL-002**: Add Cookie Consent Banner
  - Add to Admin UI (if using cookies)
  - Comply with DSGVO requirements
  - Use consent management platform (e.g., Cookiebot)
  - *Implemented as custom Landing Page banner*
  
- [x] **LEGAL-003**: Generate Privacy Policy & ToS
  - Draft privacy policy (DSGVO-compliant)
  - Draft terms of service
  - Add to public-facing documentation
  - *Implemented as /privacy and /terms routes*

### 3.3 Monitoring & Observability

- [x] **MONITOR-001**: Integrate Sentry for Error Tracking
  - Install `sentry-sdk[fastapi]`
  - Configure DSN in environment variables
  - Test by triggering an error
  - Set up alerts for critical errors
  
- [x] **MONITOR-002**: Setup Prometheus Metrics Exporter
  - Install `prometheus-fastapi-instrumentator`
  - Expose `/metrics` endpoint
  - Track: request count, latency, error rate
  
- [x] **MONITOR-003**: Create Grafana Dashboards
  - Setup Grafana instance (Docker)
  - Connect to Prometheus data source
  - Create dashboards: API latency, credits usage, errors
  - Add alerting rules
  - *Implemented: api_metrics.json, credits_usage.json, alerting.json*

---

## 🟣 Phase 5: Landing Pages & Public Features (Week 8+) ✅ COMPLETE

### 5.1 Static Content Pages

- [x] **PAGE-001a**: Erstelle Nutzer-Dokumentation (/docs)
  - **Priorität:** Kritisch
  - **Route:** `/docs` oder `/docs/[slug]`
  - **Zielgruppe:** Endnutzer (nicht-technisch)
  - **Inhalt-Struktur:**
    - Übersicht (Landing)
    - Erste Schritte (Account, API-Key erstellen)
    - API-Nutzung (Prompts senden, Credits verwalten)
    - Billing (Tarife, Upgrade, Zahlung)
  - **Design:**
    - Sidebar-Navigation
    - Breadcrumbs
    - "War diese Seite hilfreich?" Feedback
    - Responsive Layout
  - **SEO:** Meta-Tags, HowTo Schema
  - **Akzeptanzkriterien:**
    - Seite lädt ohne 404
    - Mindestens 5 Dokumentabschnitte sichtbar
    - Sidebar-Navigation funktioniert
    - Mobile-responsive

- [x] **PAGE-001b**: Erstelle Entwickler-Portal (/developers)
  - **Priorität:** Kritisch
  - **Route:** `/developers` oder `/developers/[slug]`
  - **Zielgruppe:** Entwickler, Integratoren (technisch)
  - **Inhalt-Struktur:**
    - Übersicht (Was kann die API?)
    - Authentifizierung (API-Keys, Scopes)
    - API-Referenz (/v1/generate, /admin/*)
    - Rate Limits & Best Practices
    - Fehlerbehandlung (HTTP Status Codes)
    - OpenAPI Spec Download
  - **Design:**
    - Drei-Spalten-Layout (Nav | Content | Code)
    - Syntax-Highlighting (Prism/Shiki)
    - Code-Beispiele (cURL, Python, JavaScript)
    - Copy-to-Clipboard
  - **Akzeptanzkriterien:**
    - Mindestens 5 API-Endpoints dokumentiert
    - Code-Beispiele in 3 Sprachen
    - OpenAPI-Spec zum Download

- [x] **PAGE-002**: Erstelle Changelog-Seite (/changelog)
  - **Priorität:** Kritisch
  - **Route:** `/changelog`
  - **Inhalt:**
    - Versionshistorie (v0.1.0 bis aktuell)
    - Neue Features pro Version
    - Bugfixes und Breaking Changes
  - **Design:** Timeline-Layout mit Version-Badges
  - **Datenquelle:** Automatisch aus `/CHANGELOG.md`
  - **Akzeptanzkriterien:**
    - Mindestens aktuelle Version angezeigt
    - Versionsnummer entspricht `VERSION` Datei

- [x] **PAGE-003**: Erstelle Kontaktseite (/contact)
  - **Priorität:** Kritisch
  - **Route:** `/contact`
  - **Inhalt:**
    - Kontaktformular (Name, E-Mail, Betreff, Nachricht)
    - Direkte Kontaktdaten
    - Support-Kategorien (Technisch, Abrechnung, Allgemein)
  - **Backend-Integration:**
    - E-Mail-Versand via Resend/SendGrid
    - Oder: Speichern in Supabase `contact_requests` Tabelle
  - **Spam-Schutz:** Honeypot-Feld, Rate Limiting
  - **Akzeptanzkriterien:**
    - Formular validiert Pflichtfelder
    - Erfolgsmeldung nach Absenden

- [x] **PAGE-004**: Erstelle Hilfe-Center (/help)
  - **Priorität:** Kritisch
  - **Route:** `/help`
  - **Inhalt:**
    - FAQ-Bereich mit Akkordeon
    - Kategorisierte Hilfe-Artikel
    - Links zu /docs und /contact
  - **FAQ-Kategorien:**
    - Allgemein (Was ist AI Legal Ops?)
    - API-Nutzung (Wie sende ich Prompts?)
    - Billing (Credits, Abrechnung)
    - Privacy (PII-Shield, DSGVO)
  - **SEO:** FAQ Schema.org Markup
  - **Akzeptanzkriterien:**
    - Mindestens 10 FAQ-Einträge
    - Akkordeon öffnet/schließt korrekt

- [x] **PAGE-005**: Erstelle Systemstatus-Seite (/status)
  - **Priorität:** Mittel
  - **Route:** `/status`
  - **Optionen:**
    - Option A: Redirect zu Statuspage.io/Betteruptime
    - Option B: Eigene Status-Seite mit Health-Checks
  - **Bei Option B - Inhalt:**
    - Service-Status (API, Database, AI Providers)
    - Uptime-Historie (letzte 30 Tage)
    - Geplante Wartungen
  - **Health-Checks:** `/health` Endpoint, Supabase, AI Provider
  - **Akzeptanzkriterien:**
    - Mindestens 3 Services angezeigt
    - Status wird automatisch aktualisiert

- [x] **PAGE-006**: Erstelle Blog-Bereich (/blog)
  - **Priorität:** Hoch
  - **Route:** `/blog` und `/blog/[slug]`
  - **Typ:** Statische Seiten mit MDX + Suchfunktion
  - **Inhalt-Kategorien:**
    - AI & Legal Tech Grundlagen
    - Praxis-Tipps (API-Integration)
    - Produkt-News (Features, Updates)
    - Tutorials
  - **Suchfunktion:** Fuse.js (client-side) oder Supabase Full-Text
  - **UI-Features:**
    - Pagination (12 Artikel/Seite)
    - RSS-Feed
    - Kategorie-Badges, Lesezeit-Anzeige
  - **Akzeptanzkriterien:**
    - Mindestens 3 Artikel vorhanden
    - Suchfunktion filtert korrekt
    - RSS-Feed ist valide

### 5.2 SEO-Optimierung (Google + KI-Chatbots)

- [x] **SEO-001**: Implementiere SEO-Optimierung
  - **Priorität:** Kritisch
  - **Dateien:**
    - `app/seo/metadata.py` (Global Metadata)
    - `app/static/sitemap.xml`
    - `app/static/robots.txt`
    - `app/static/llms.txt` (KI-Crawler Anweisungen)
  - **Ziele:**
    - Google Ranking für AI Gateway Keywords
    - Korrekte Darstellung in KI-Antworten (ChatGPT, Claude, Perplexity)
  - **Meta-Tags:**
    - Title, Description, Keywords
    - OpenGraph (og:title, og:description, og:image)
    - Twitter Cards
  - **Strukturierte Daten (Schema.org):**
    - SoftwareApplication Schema
    - FAQ Schema (für Featured Snippets)
    - Organization Schema
  - **llms.txt (KI-Crawler):**
    ```
    # AI Legal Ops - Information for AI Assistants
    ## About This Service
    AI Legal Ops is a multi-tenant AI gateway with privacy enforcement.
    ## Key Facts
    - Product: AI Gateway with PII Shield
    - Features: Multi-tenant, Billing, Privacy Enforcement
    - Compliance: DSGVO, EU Data Residency
    ```
  - **robots.txt:**
    - Erlaubt: `/`, `/docs`, `/blog`
    - Blockiert: `/admin/`, `/api/`
    - KI-Crawler explizit erlaubt (GPTBot, Claude-Web, PerplexityBot)
  - **Akzeptanzkriterien:**
    - Lighthouse SEO Score > 95
    - llms.txt unter /llms.txt erreichbar
    - Strukturierte Daten validieren ohne Fehler

### 5.3 UI-Komponenten

- [x] **UI-001**: Implementiere API-Key Verwaltung in Settings
  - **Priorität:** Kritisch
  - **Dateien:** API Route + Frontend-Komponente
  - **Funktionalitäten:**
    - Liste aller API-Keys des Users
    - "Neuen Key erstellen" Button
    - Einmaliges Anzeigen des Keys (mit Copy-Button)
    - Warnung: "Key wird nur einmal angezeigt!"
    - Löschen von Keys (mit Bestätigung)
  - **Sicherheit:**
    - Key nur einmal anzeigen
    - Rate Limiting (max 5 Keys pro User)
  - **Akzeptanzkriterien:**
    - User kann neuen Key erstellen
    - Key wird einmalig mit Copy-Button angezeigt
    - User kann Keys löschen

- [x] **UI-002**: Implementiere Autosave-Indikator
  - **Priorität:** Hoch
  - **Datei:** Komponente für Speicherstatus
  - **UI-Zustände:**
    - "idle" - Keine Änderungen
    - "saving" - Spinner + "Speichern..."
    - "saved" - Checkmark + "Gespeichert um HH:MM"
    - "error" - X-Icon + "Speichern fehlgeschlagen"
  - **Autosave-Logik:** Debounced save (2 Sekunden nach letzter Änderung)
  - **Akzeptanzkriterien:**
    - Indikator zeigt korrekten Status
    - Änderungen werden automatisch gespeichert

- [x] **UI-003**: Implementiere Feedback-Widget
  - **Priorität:** Hoch
  - **Dateien:**
    - Feedback-Button (Floating)
    - Feedback-Modal
    - API-Route `/api/feedback`
  - **Funktionalitäten:**
    - Floating Action Button unten rechts
    - Kategorie-Auswahl (Bug, Feature, Frage, Sonstiges)
    - Textarea für Beschreibung (min 20 Zeichen)
    - Optional: Screenshot-Upload, Rating (1-5 Sterne)
    - Automatisch: User-ID, URL, Browser-Info
  - **Backend:** Supabase `feedback` Tabelle
  - **Benachrichtigungen (konfigurierbar):**
    - E-Mail an Support-Adresse
    - Microsoft Teams Webhook-Integration
  - **Akzeptanzkriterien:**
    - Floating Button auf allen Dashboard-Seiten
    - Feedback wird in Datenbank gespeichert
    - E-Mail/Teams Benachrichtigung konfigurierbar

### 5.4 Accessibility

- [x] **A11Y-001**: Integriere AccessibilityPanel in Landing Page
  - **Priorität:** Mittel
  - **Problem:** AccessibilityPanel nur im Dashboard, nicht auf Landing Page
  - **Lösung:** Shared Header-Komponente oder Panel in Landing Header
  - **Features:**
    - Schriftgröße anpassen
    - Kontrast-Modus
    - LocalStorage-Persistence
  - **Akzeptanzkriterien:**
    - AccessibilityPanel auf Landing Page sichtbar
    - Einstellungen werden gespeichert

### 5.5 Implementierungsplan Phase 5

| Task | Beschreibung | Aufwand |
|------|--------------|---------|
| SEO-001 | SEO-Optimierung (Google + KI-Chatbots) | 5h |
| PAGE-001a | Nutzer-Dokumentation (/docs) | 4h |
| PAGE-001b | Entwickler-Portal (/developers) | 5h |
| PAGE-006 | Blog mit Suchfunktion (/blog) | 7h |
| PAGE-003 | Kontakt (/contact) | 3h |
| UI-001 | API-Key Settings UI | 4h |
| PAGE-002 | Changelog (/changelog) | 2h |
| PAGE-004 | Hilfe-Center (/help) | 3h |
| UI-002 | Autosave-Indikator | 2h |
| UI-003 | Feedback-Widget | 5h |
| PAGE-005 | Systemstatus (/status) | 3h |
| A11Y-001 | Landing Accessibility | 1h |

**Gesamt Phase 5:** ~44h

---

## 🔵 Phase 4: Optimization & Advanced Features (Week 7+)

### 4.1 Performance & Resilience

- [x] **AI-004**: Implement Failover Logic
  - Add primary/secondary provider configuration
  - Retry with secondary if primary fails
  - Log provider switch events
  - *Implemented in `app/services/resilient_gateway.py`*

- [x] **AI-005**: Add Retry Logic with Exponential Backoff
  - Use `tenacity` library
  - Retry on 5xx errors (up to 3 attempts)
  - Exponential backoff: 1s, 2s, 4s
  - *Implemented with circuit breaker pattern in `resilient_gateway.py`*

- [x] **INFRA-005**: Optimize Docker Image Size
  - Use multi-stage build
  - Remove dev dependencies from production image
  - Target: < 200MB final image
  - *Enhanced Dockerfile with OCI labels, dev stage, .dockerignore*

- [x] **API-003**: Add Response Caching Layer
  - Setup Redis for caching
  - Cache identical prompts for 1 hour
  - Deduct 0 credits for cached responses
  - *Implemented in `app/services/cache.py` with hash-based keys*

### 4.2 Advanced Features

- [x] **ADMIN-007**: Add Multi-Language Support (i18n)
  - Setup next-i18next or similar
  - Translate UI to English + German
  - Add language switcher
  - *Implemented in `app/core/i18n/` with EN, DE, FR, ES support*

- [x] **ADMIN-008**: Implement Role-Based Access Control
  - Add `roles` table (admin, viewer)
  - Restrict tenant deletion to admins only
  - Add user management UI
  - *Implemented in `app/core/rbac.py` with OWNER/ADMIN/MEMBER/VIEWER roles*

- [x] **BILLING-005**: Add Invoice Generation
  - Generate monthly PDF invoices per tenant
  - Include: usage breakdown, total credits, payment status
  - Send via email (SendGrid/Postmark)
  - *Implemented in `app/services/invoice.py` with PDF generation*

---

## 📅 Timeline & Milestones

| Phase | Duration | Key Deliverables | Status |
|-------|----------|------------------|--------|
| **Phase 1** (MVP Core) | Weeks 1-3 | Gateway + Privacy + Local Dev | ✅ Complete |
| **Phase 2** (Billing & Admin) | Weeks 4-5 | Database + Admin UI + Billing | ✅ Complete |
| **Phase 3** (Launch Prep) | Week 6 | Security + Monitoring + Legal | ✅ Complete |
| **Phase 4** (Optimization) | Week 7+ | Caching + Failover + Advanced Features | ✅ Complete |
| **Phase 5** (Landing Pages) | Week 8+ | Docs + Blog + SEO + Feedback | ✅ Complete |
| **Phase 6** (Frontend) | Week 9+ | Next.js + Landing + Dashboard + Auth | ✅ Complete |

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
- [x] **DEV-001**: Install Supabase CLI (Duplicate - already completed above)
- [x] **DEV-002**: Create `.env.example`
- [x] **INFRA-001**: Init FastAPI project
- [x] **INFRA-002**: Setup Supabase (production)

**Expected Outcome:** Development environment ready for coding

---

## 🟠 Phase 6: Frontend & Landing Page (Next.js)

> **Referenz:** Basiert auf `/root/Projekte/e-rechnung/docs/TASKS.md` Struktur

### 6.1 Frontend Setup

- [x] **FRONTEND-001**: Initialize Next.js Project
  - **Priorität:** Kritisch
  - **Tech Stack:**
    - Next.js 15 (App Router)
    - TypeScript
    - Tailwind CSS + shadcn/ui
    - Supabase Auth + Database
  - **Ordnerstruktur:**
    ```
    frontend/
    ├── app/
    │   ├── (landing)/           # Public Landing Pages
    │   ├── (dashboard)/         # Protected Admin Area
    │   ├── (auth)/              # Auth Pages
    │   └── api/                 # API Routes
    ├── components/
    │   ├── landing/             # Landing Page Components
    │   ├── dashboard/           # Dashboard Components
    │   ├── ui/                  # shadcn/ui Components
    │   └── shared/              # Shared Components
    ├── lib/                     # Utilities, Supabase Client
    └── public/                  # Static Assets
    ```
  - **Akzeptanzkriterien:**
    - `npm run dev` startet ohne Fehler
    - TypeScript ohne Fehler
    - Tailwind funktioniert

- [x] **FRONTEND-002**: Configure Supabase Client
  - **Priorität:** Kritisch
  - **Dateien:**
    - `lib/supabase/client.ts` (Browser)
    - `lib/supabase/server.ts` (Server Components)
    - `lib/supabase/middleware.ts` (Auth Middleware)
  - **Features:**
    - Session Management
    - Auth State Change Listener
    - Type-Safe Database Queries
  - **Akzeptanzkriterien:**
    - Verbindung zu Supabase funktioniert
    - Auth Session wird korrekt verwaltet

### 6.2 Landing Page Components

- [x] **FRONTEND-003**: Implement Landing Page Layout
  - **Priorität:** Kritisch
  - **Route:** `/` (Landing)
  - **Komponenten:**
    - `Navbar.tsx` - Navigation mit Logo, Links, CTA
    - `Hero.tsx` - Headline, Subline, CTA Buttons
    - `Features.tsx` - Feature Grid (3-6 Features)
    - `Pricing.tsx` - Tarif-Karten (Free, Pro, Enterprise)
    - `FAQ.tsx` - Akkordeon mit häufigen Fragen
    - `Testimonials.tsx` - Kundenstimmen (Slider)
    - `CTA.tsx` - Call-to-Action Section
    - `Footer.tsx` - Links, Social, Copyright
  - **Design:**
    - Mobile-First Responsive
    - Dark Mode Support
    - Smooth Scroll Anchors
  - **Akzeptanzkriterien:**
    - Alle Sektionen sichtbar
    - Responsive auf Mobile/Tablet/Desktop
    - Dark Mode funktioniert

- [x] **FRONTEND-004**: Hero Section
  - **Priorität:** Kritisch
  - **Datei:** `components/landing/Hero.tsx`
  - **Inhalt:**
    - Headline: "AI Gateway mit Datenschutz-Garantie"
    - Subline: "Multi-Tenant AI-Proxy mit PII Shield"
    - Primary CTA: "Kostenlos starten" → /signup
    - Secondary CTA: "Demo ansehen" → /demo
    - Background: Gradient oder Animated Pattern
  - **Akzeptanzkriterien:**
    - CTAs führen zu korrekten Seiten
    - Animation läuft flüssig

- [x] **FRONTEND-005**: Features Section
  - **Priorität:** Hoch
  - **Datei:** `components/landing/Features.tsx`
  - **Features zu zeigen:**
    1. 🛡️ **PII Shield** - Automatische Erkennung & Redaktion von PII
    2. 🏢 **Multi-Tenant** - Isolierte Mandanten mit eigenen Credits
    3. 💳 **Pay-per-Use** - Credit-basierte Abrechnung
    4. 🔄 **Provider Failover** - Automatischer Wechsel bei Ausfall
    5. 📊 **Usage Analytics** - Detaillierte Nutzungsstatistiken
    6. 🇪🇺 **DSGVO-konform** - EU Data Residency
  - **Design:** 3-spaltig auf Desktop, 1-spaltig auf Mobile
  - **Akzeptanzkriterien:**
    - Alle 6 Features mit Icons
    - Responsive Grid

- [x] **FRONTEND-006**: Pricing Section
  - **Priorität:** Hoch
  - **Datei:** `components/landing/Pricing.tsx`
  - **Tarife:**
    - **Starter** (€0/Monat): 100 Credits, 1 API Key, Community Support
    - **Professional** (€49/Monat): 10.000 Credits, 10 API Keys, Priority Support
    - **Enterprise** (Auf Anfrage): Unlimited, Custom, Dedicated Support
  - **Design:**
    - Highlighted "Empfohlen" Badge für Pro
    - Jährlich/Monatlich Toggle (20% Rabatt)
  - **Akzeptanzkriterien:**
    - Preise korrekt angezeigt
    - CTAs führen zu Checkout

- [x] **FRONTEND-007**: FAQ Section
  - **Priorität:** Mittel
  - **Datei:** `components/landing/FAQ.tsx`
  - **Fragen:**
    1. Was ist AI Legal Ops?
    2. Wie funktioniert der PII Shield?
    3. Welche AI-Provider werden unterstützt?
    4. Wie wird abgerechnet?
    5. Ist die API DSGVO-konform?
    6. Gibt es eine Testphase?
  - **Design:** shadcn/ui Accordion
  - **Akzeptanzkriterien:**
    - Akkordeon öffnet/schließt smooth
    - Schema.org FAQ Markup

- [x] **FRONTEND-008**: Testimonials Section
  - **Priorität:** Niedrig
  - **Datei:** `components/landing/Testimonials.tsx`
  - **Design:**
    - Slider/Carousel mit 3-5 Testimonials
    - Foto, Name, Firma, Zitat
  - **Akzeptanzkriterien:**
    - Slider funktioniert
    - Auto-Play mit Pause on Hover

- [x] **FRONTEND-009**: Footer Component
  - **Priorität:** Mittel
  - **Datei:** `components/landing/Footer.tsx`
  - **Inhalt:**
    - Logo + Tagline
    - Links: Docs, Blog, Changelog, Status
    - Legal: Impressum, Datenschutz, AGB
    - Social: GitHub, Twitter/X, LinkedIn
    - Copyright: © 2025 AI Legal Ops
  - **Akzeptanzkriterien:**
    - Alle Links funktionieren
    - Responsive Layout

### 6.3 Authentication Pages

- [x] **FRONTEND-010**: Login Page
  - **Priorität:** Kritisch
  - **Route:** `/login`
  - **Features:**
    - Email + Password Login
    - "Passwort vergessen" Link
    - Social Login (Google, GitHub) - Optional
    - "Noch kein Konto?" Link zu /signup
  - **Validierung:**
    - Email-Format
    - Passwort min. 8 Zeichen
  - **Nach Login:** Redirect zu /dashboard
  - **Akzeptanzkriterien:**
    - Login funktioniert mit Supabase Auth
    - Fehler werden angezeigt

- [x] **FRONTEND-011**: Signup Page
  - **Priorität:** Kritisch
  - **Route:** `/signup`
  - **Features:**
    - Name, Email, Password
    - Password Confirm
    - AGB + Datenschutz Checkbox
    - Email Verification Flow
  - **Nach Signup:** Email-Bestätigung senden
  - **Akzeptanzkriterien:**
    - Registrierung funktioniert
    - Verification Email wird gesendet

- [x] **FRONTEND-012**: Password Reset Flow
  - **Priorität:** Hoch
  - **Routes:**
    - `/forgot-password` - Email eingeben
    - `/reset-password` - Neues Passwort setzen (Token-basiert)
  - **Flow:**
    1. User gibt Email ein
    2. Reset-Link per Email
    3. User setzt neues Passwort
  - **Akzeptanzkriterien:**
    - Reset-Email wird gesendet
    - Passwort kann geändert werden

- [x] **FRONTEND-013**: Email Verification Page
  - **Priorität:** Hoch
  - **Route:** `/verify-email`
  - **Inhalt:**
    - "Bitte bestätigen Sie Ihre Email"
    - "Email erneut senden" Button
    - Auto-Redirect nach Bestätigung
  - **Akzeptanzkriterien:**
    - Resend funktioniert
    - Redirect nach Verification

### 6.4 Dashboard Layout & Navigation

- [x] **FRONTEND-014**: Dashboard Layout
  - **Priorität:** Kritisch
  - **Route:** `/dashboard/*`
  - **Komponenten:**
    - `DashboardLayout.tsx` - Wrapper mit Sidebar
    - `Sidebar.tsx` - Navigation (collapsible)
    - `Header.tsx` - Breadcrumbs, User Menu, Notifications
    - `MobileNav.tsx` - Mobile Drawer Navigation
  - **Sidebar-Items:**
    - 🏠 Dashboard (Overview)
    - 🔑 API Keys
    - 📊 Usage & Analytics
    - 💳 Billing
    - ⚙️ Settings
    - 📖 Documentation
  - **Akzeptanzkriterien:**
    - Sidebar collapsed state persists
    - Breadcrumbs korrekt
    - Mobile Navigation funktioniert

- [x] **FRONTEND-015**: Dashboard Overview Page
  - **Priorität:** Kritisch
  - **Route:** `/dashboard`
  - **Widgets:**
    - Credit Balance (Anzeige + Top-Up Button)
    - Usage Chart (letzte 30 Tage)
    - Quick Stats (Total Requests, Avg Tokens, Error Rate)
    - Recent Activity (letzte 5 API Calls)
  - **Akzeptanzkriterien:**
    - Daten werden live aus API geladen
    - Charts rendern korrekt

- [x] **FRONTEND-016**: API Keys Management Page
  - **Priorität:** Kritisch
  - **Route:** `/dashboard/api-keys`
  - **Features:**
    - Liste aller API Keys (Name, Created, Last Used, Status)
    - "Neuen Key erstellen" Dialog
    - Einmaliges Anzeigen des Keys mit Copy Button
    - Key rotieren (neuen generieren, alten invalidieren)
    - Key löschen (mit Bestätigung)
  - **Akzeptanzkriterien:**
    - CRUD für API Keys funktioniert
    - Key wird nur einmal angezeigt

- [x] **FRONTEND-017**: Usage & Analytics Page
  - **Priorität:** Hoch
  - **Route:** `/dashboard/usage`
  - **Charts:**
    - Requests per Day (Line Chart)
    - Tokens Used (Bar Chart)
    - Credits Consumed (Area Chart)
    - Provider Split (Pie Chart)
  - **Filters:**
    - Date Range (7d, 30d, 90d, Custom)
    - API Key Filter
  - **Export:** CSV Download
  - **Akzeptanzkriterien:**
    - Charts laden Daten korrekt
    - Filter funktionieren
    - Export generiert valide CSV

- [x] **FRONTEND-018**: Billing Page
  - **Priorität:** Hoch
  - **Route:** `/dashboard/billing`
  - **Sections:**
    - Current Plan (mit Upgrade Button)
    - Credit Balance (mit Top-Up Button)
    - Payment Methods (Stripe Integration)
    - Invoices (Liste mit PDF Download)
  - **Stripe Integration:**
    - Checkout Session für Credit Purchase
    - Customer Portal für Subscription Management
  - **Akzeptanzkriterien:**
    - Stripe Checkout funktioniert
    - Invoices können heruntergeladen werden

- [x] **FRONTEND-019**: Settings Page
  - **Priorität:** Mittel
  - **Route:** `/dashboard/settings`
  - **Tabs:**
    - **Profile:** Name, Email, Avatar
    - **Security:** Password Change, 2FA (Optional)
    - **Notifications:** Email Preferences
    - **Preferences:** Language, Theme, Timezone
  - **Akzeptanzkriterien:**
    - Profil kann aktualisiert werden
    - Passwort kann geändert werden
    - Preferences werden gespeichert

### 6.5 Design System & Theming

- [x] **DESIGN-001**: Setup Design System
  - **Priorität:** Kritisch
  - **Dateien:**
    - `tailwind.config.ts` - Custom Colors, Fonts
    - `app/globals.css` - CSS Variables
    - `components/ui/*` - shadcn/ui Components
  - **Farben:**
    - Primary: Blau (#2563eb)
    - Secondary: Grau
    - Accent: Türkis
    - Error: Rot
    - Success: Grün
  - **Akzeptanzkriterien:**
    - Konsistente Farben überall
    - CSS Variables für Theming

- [x] **DESIGN-002**: Implement Dark Mode
  - **Priorität:** Hoch
  - **Datei:** `components/ThemeProvider.tsx`
  - **Features:**
    - System Preference Detection
    - Manual Toggle (Light/Dark/System)
    - LocalStorage Persistence
    - next-themes Integration
  - **Akzeptanzkriterien:**
    - Toggle funktioniert
    - Preference wird gespeichert
    - Kein Flash on Load

- [x] **DESIGN-003**: Responsive Breakpoints
  - **Priorität:** Hoch
  - **Breakpoints:**
    - `sm`: 640px (Mobile)
    - `md`: 768px (Tablet)
    - `lg`: 1024px (Desktop)
    - `xl`: 1280px (Large Desktop)
  - **Testing:** Alle Seiten auf allen Breakpoints
  - **Akzeptanzkriterien:**
    - Keine horizontalen Scrollbars
    - Touch-friendly auf Mobile

### 6.6 Internationalization (i18n)

- [x] **I18N-001**: Setup next-intl
  - **Priorität:** Mittel
  - **Dateien:**
    - `i18n/request.ts` - Locale Detection
    - `messages/de.json` - German Translations
    - `messages/en.json` - English Translations
  - **Features:**
    - URL-based Routing (`/de/`, `/en/`)
    - Language Switcher Component
    - Fallback to German
  - **Akzeptanzkriterien:**
    - Sprache kann gewechselt werden
    - Alle UI-Texte übersetzt

### 6.7 Accessibility (A11Y)

- [x] **A11Y-002**: Implement Accessibility Panel
  - **Priorität:** Mittel
  - **Datei:** `components/AccessibilityPanel.tsx`
  - **Features:**
    - Font Size Adjustment (80% - 150%)
    - High Contrast Mode
    - Reduced Motion
    - Focus Indicators
  - **Persistence:** LocalStorage
  - **Akzeptanzkriterien:**
    - Settings werden angewendet
    - Settings bleiben nach Reload

- [x] **A11Y-003**: WCAG 2.1 AA Compliance
  - **Priorität:** Hoch
  - **Checks:**
    - Alle Images haben alt-Text
    - Fokus-Management korrekt
    - Keyboard Navigation
    - Color Contrast (4.5:1 minimum)
    - ARIA Labels wo nötig
  - **Testing:** axe-core, Lighthouse
  - **Akzeptanzkriterien:**
    - Lighthouse Accessibility Score > 90
    - Keine axe-core Errors

### 6.8 Admin Dashboard (Superadmin)

> **Hinweis:** Diese Seiten sind nur für Admins/Superadmins sichtbar (RBAC-geschützt)

- [ ] **ADMIN-009**: Tenant Management UI
  - **Priorität:** Kritisch
  - **Route:** `/admin/tenants`
  - **Features:**
    - Liste aller Tenants (Name, Plan, Credits, Status, Created)
    - Tenant erstellen (Name, Email, Plan)
    - Tenant bearbeiten (Plan upgraden, Credits hinzufügen)
    - Tenant deaktivieren/aktivieren
    - Tenant löschen (Soft Delete mit Bestätigung)
  - **Filters:** Status, Plan, Suchfeld
  - **Akzeptanzkriterien:**
    - CRUD für Tenants funktioniert
    - Nur Admins haben Zugriff

- [ ] **ADMIN-010**: License/API Key Management UI (für Tenants)
  - **Priorität:** Kritisch
  - **Route:** `/admin/licenses`
  - **Features:**
    - Liste aller Licenses (Key masked, Tenant, Plan, Credits, Status)
    - License für Tenant erstellen
    - Credits manuell hinzufügen
    - License aktivieren/deaktivieren
    - License löschen (revoke)
    - Usage History pro License anzeigen
  - **Bulk Actions:**
    - Mehrere Licenses auswählen
    - Bulk Credit Top-Up
    - Bulk Deaktivieren
  - **Akzeptanzkriterien:**
    - Admin kann API Keys für jeden Tenant erstellen
    - Credits können manuell vergeben werden

- [ ] **ADMIN-011**: User Management UI
  - **Priorität:** Hoch
  - **Route:** `/admin/users`
  - **Features:**
    - Liste aller Users (Email, Role, Tenant, Last Login, Status)
    - User zu Tenant zuweisen
    - Role ändern (Owner, Admin, Member, Viewer)
    - User deaktivieren/aktivieren
    - Password Reset auslösen
  - **Akzeptanzkriterien:**
    - RBAC wird korrekt angewendet
    - User können Tenants zugewiesen werden

- [ ] **ADMIN-012**: Audit Log Viewer UI
  - **Priorität:** Hoch
  - **Route:** `/admin/audit-logs`
  - **Features:**
    - Paginated Table aller Logs
    - Filter: Tenant, License, Action Type, Date Range
    - Columns: Timestamp, Tenant, License, Action, Details, IP
    - Detail-View für einzelne Log-Einträge
    - Export zu CSV
  - **Log Types:**
    - API Calls (Prompt sanitized!)
    - Credit Deductions
    - Login/Logout Events
    - Admin Actions (Tenant/License CRUD)
  - **Akzeptanzkriterien:**
    - Logs werden ohne PII angezeigt
    - Filter und Pagination funktionieren

- [ ] **ADMIN-013**: System Settings UI
  - **Priorität:** Mittel
  - **Route:** `/admin/settings`
  - **Sections:**
    - **General:** App Name, Logo, Support Email
    - **Billing:** Default Plans, Credit Pricing, Stripe Config
    - **AI Providers:** Provider Status, API Key Status (masked)
    - **Security:** Rate Limits, IP Whitelist Global
    - **Email:** SMTP/SendGrid Config, Email Templates
  - **Akzeptanzkriterien:**
    - Settings können gespeichert werden
    - Sensitive Daten sind maskiert

- [ ] **ADMIN-014**: Analytics Dashboard (Admin)
  - **Priorität:** Hoch
  - **Route:** `/admin/analytics`
  - **Widgets:**
    - Total Revenue (Credits sold)
    - Active Tenants / Total Tenants
    - API Calls Today / This Month
    - Top 10 Tenants by Usage
    - Provider Usage Split (Anthropic vs Scaleway)
    - Error Rate Chart
  - **Date Range Filter:** 7d, 30d, 90d, Custom
  - **Akzeptanzkriterien:**
    - Daten werden live geladen
    - Charts rendern korrekt

- [ ] **ADMIN-015**: Credit Top-Up & Billing Admin
  - **Priorität:** Hoch
  - **Route:** `/admin/billing`
  - **Features:**
    - Manual Credit Top-Up für jeden Tenant
    - Credit History (wer, wann, wieviel)
    - Pending Payments anzeigen
    - Invoice Generation (manuell auslösen)
    - Refund Processing
  - **Akzeptanzkriterien:**
    - Credits können manuell vergeben werden
    - Audit Trail für alle Credit-Änderungen

- [ ] **ADMIN-016**: Privacy Shield Test Console
  - **Priorität:** Hoch
  - **Route:** `/admin/privacy-test`
  - **Beschreibung:** Interaktive Test-Konsole für Admins, um die PII-Erkennung und Anonymisierung des Privacy Shields zu testen und zu demonstrieren
  - **Features:**
    - **LLM Provider/Model Auswahl:** Dropdown für Provider (Anthropic, Scaleway) und Model
    - **Test-Vorlagen Dropdown:**
      - Bankdaten (IBAN, BLZ, Kontonummer)
      - Kontaktdaten (Email, Telefon)
      - Personendaten (Name, Geburtsdatum)
      - Adressdaten (Straße, PLZ, Ort)
      - Gemischt (alle PII-Typen)
      - Custom (freie Eingabe)
    - **Zwei-Panel-Ansicht:**
      - Original Prompt (Eingabe)
      - Sanitized Prompt (was an LLM gesendet wird)
    - **PII-Erkennungsliste:** Detaillierte Auflistung aller erkannten PII mit Original → Ersetzung
    - **Zwei Modi:**
      - "Nur Analysieren" - Zeigt Sanitization ohne LLM-Call (0 Credits)
      - "Senden & Testen" - Tatsächlicher LLM-Call mit Response (verbraucht Credits)
    - **Metriken-Anzeige:** Tokens, Credits, Latenz, Provider
  - **Backend:**
    - Neuer Endpoint `POST /api/v1/admin/privacy-test`
    - Request: `{ prompt, provider, model, send_to_llm: boolean }`
    - Response: `{ original, sanitized, detected_pii[], llm_response?, metrics }`
  - **Use Cases:**
    - Compliance-Nachweis für DSGVO-Audits
    - Debugging von Edge Cases in der PII-Erkennung
    - Demo für Kunden zur Vertrauensbildung
    - QA-Tests mit vordefinierten Prompts
  - **Akzeptanzkriterien:**
    - Admin kann Prompt eingeben und Sanitization sehen
    - Alle erkannten PII werden aufgelistet
    - Optional: LLM-Response wird angezeigt
    - Test-Vorlagen funktionieren korrekt

- [ ] **ADMIN-017**: LLM Configuration Management
  - **Priorität:** Kritisch
  - **Route:** `/admin/settings/llm-config`
  - **Beschreibung:** Zentrale Verwaltung der LLM-Konfiguration auf Platform-, Tenant- und API-Key-Ebene (wie Scaleway Playground)
  - **Features:**
    - **Model Management:**
      - Aktivieren/Deaktivieren von Scaleway Models
      - Model-Verfügbarkeit pro Plan (Free, Pro, Enterprise)
      - Default Model setzen
    - **Default Parameter Panel (rechte Seitenleiste wie Scaleway):**
      - Response Format (Dropdown: Text, JSON Schema)
      - Maximum Output Tokens (Slider 1-8192, Input)
      - Temperature (Slider 0-2, Dezimalwerte)
      - Top P (Slider 0-1)
      - Presence Penalty (Slider 0-2)
      - System Prompt (Textarea, mehrzeilig)
      - Stop Sequences (Array-Input mit Add/Remove)
    - **Konfigurationsebenen:**
      - Platform Default (für alle neuen Tenants)
      - Tenant Override (pro Kunde)
      - API Key Override (pro App/Integration)
    - **Presets/Templates:**
      - "Creative Writing" (temp=1.0, top_p=0.95)
      - "Factual/Precise" (temp=0.15, top_p=1.0)
      - "Code Generation" (temp=0.7, top_p=0.8)
      - "Balanced" (temp=0.7, top_p=0.9)
      - Custom Presets speichern
  - **Backend:**
    - `GET /api/v1/admin/llm-config` - Aktuelle Config laden
    - `PUT /api/v1/admin/llm-config` - Config speichern
    - `GET /api/v1/admin/llm-config/models` - Verfügbare Models
    - `PUT /api/v1/admin/llm-config/models/{model_id}/status` - Model aktivieren/deaktivieren
  - **Akzeptanzkriterien:**
    - Parameter können live angepasst werden
    - Änderungen werden sofort wirksam
    - Presets können gespeichert und geladen werden
    - Model-Verfügbarkeit kann gesteuert werden

- [ ] **ADMIN-018**: AI Playground (Interactive Testing)
  - **Priorität:** Hoch
  - **Route:** `/admin/playground`
  - **Beschreibung:** Interaktiver Chat-Playground zum Testen von Models und Konfigurationen (wie Scaleway Screenshot)
  - **Features:**
    - **Linke Seite - Chat Interface:**
      - Model Dropdown (alle verfügbaren Scaleway Models)
      - "View code" Button (zeigt API-Aufruf als Code)
      - Chat-Verlauf mit User/Assistant Messages
      - Prompt Input mit Send Button
      - Streaming Response Anzeige
    - **Rechte Seite - Parameter Panel:**
      - Response Format (Text/JSON)
      - Maximum Output Tokens (Slider + Input)
      - Temperature (Slider + Input, 0-2)
      - Top P (Slider + Input, 0-1)
      - Presence Penalty (Slider + Input)
      - System Prompt (Textarea)
      - Stop Sequences (Add/Remove)
    - **Zusatzfeatures:**
      - Chat-History speichern/laden
      - "Copy as cURL" / "Copy as Python"
      - Token-Verbrauch Anzeige
      - Latenz-Metriken
      - Credit-Kosten pro Request
  - **Backend:**
    - Nutzt bestehenden `/api/v1/generate` Endpoint
    - Neue Parameter: alle LLM-Konfigurationen
  - **Akzeptanzkriterien:**
    - Chat funktioniert mit allen Scaleway Models
    - Parameter werden live angewendet
    - Code-Export funktioniert
    - Streaming Responses werden korrekt angezeigt

- [ ] **ADMIN-019**: Tenant LLM Config Override
  - **Priorität:** Mittel
  - **Route:** `/admin/tenants/{id}/llm-config`
  - **Beschreibung:** Pro-Tenant LLM-Konfiguration überschreiben
  - **Features:**
    - Eigene Default-Parameter pro Tenant
    - Model-Einschränkungen (nur bestimmte Models erlauben)
    - Max Token Limits (Kostenkontrolle)
    - Custom System Prompts
  - **Akzeptanzkriterien:**
    - Tenant-spezifische Config überschreibt Platform Defaults
    - Limits werden bei API-Calls enforced

### 6.10 Database Schema für LLM Config

- [ ] **DB-010**: LLM Configuration Schema Migration
  - **Priorität:** Kritisch
  - **Datei:** `migrations/012_add_llm_config.sql`
  - **Schema:**
    ```sql
    -- Platform-Level LLM Defaults
    CREATE TABLE IF NOT EXISTS platform_settings (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      key VARCHAR(255) UNIQUE NOT NULL,
      value JSONB NOT NULL,
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Insert default LLM config
    INSERT INTO platform_settings (key, value) VALUES
    ('llm_config', '{
      "default_model": "mistral-small-3.2-24b-instruct-2506",
      "max_output_tokens": 512,
      "temperature": 0.7,
      "top_p": 0.8,
      "presence_penalty": 0,
      "system_prompt": "You are a helpful assistant",
      "stop_sequences": [],
      "response_format": "text",
      "enabled_models": [
        "gpt-oss-120b",
        "llama-3.3-70b-instruct",
        "mistral-small-3.2-24b-instruct-2506",
        "qwen3-235b-a22b-instruct-2507"
      ]
    }'::jsonb);

    -- Tenant-Level LLM Config Override
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS llm_config JSONB DEFAULT NULL;

    -- API Key Level Override
    ALTER TABLE licenses ADD COLUMN IF NOT EXISTS llm_config_override JSONB DEFAULT NULL;

    -- LLM Config Presets
    CREATE TABLE IF NOT EXISTS llm_presets (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name VARCHAR(255) NOT NULL,
      description TEXT,
      config JSONB NOT NULL,
      is_system BOOLEAN DEFAULT FALSE,
      tenant_id UUID REFERENCES tenants(id),
      created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Insert system presets
    INSERT INTO llm_presets (name, description, config, is_system) VALUES
    ('Creative Writing', 'Higher randomness for creative tasks', '{"temperature": 1.0, "top_p": 0.95, "presence_penalty": 0.5}', true),
    ('Factual/Precise', 'Low randomness for factual accuracy', '{"temperature": 0.15, "top_p": 1.0, "presence_penalty": 0}', true),
    ('Code Generation', 'Balanced settings for code', '{"temperature": 0.7, "top_p": 0.8, "presence_penalty": 0}', true),
    ('Balanced', 'Default balanced settings', '{"temperature": 0.7, "top_p": 0.9, "presence_penalty": 0}', true);
    ```
  - **Akzeptanzkriterien:**
    - Migration läuft fehlerfrei
    - Defaults werden korrekt gesetzt
    - Presets sind verfügbar

- [ ] **DB-011**: Model Pricing Schema Migration
  - **Priorität:** Kritisch
  - **Datei:** `migrations/013_add_model_pricing.sql`
  - **Schema:**
    ```sql
    -- Model Pricing Table
    CREATE TABLE IF NOT EXISTS model_pricing (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      model_id VARCHAR(100) UNIQUE NOT NULL,
      provider VARCHAR(50) NOT NULL,
      tasks TEXT[] NOT NULL,  -- ['chat', 'vision', 'audio', 'embeddings']

      -- Einkaufspreise (Scaleway)
      input_price_ek DECIMAL(10, 6) NOT NULL,   -- €/Million Tokens
      output_price_ek DECIMAL(10, 6) NOT NULL,  -- €/Million Tokens

      -- Verkaufspreise (an Kunden)
      input_price_vk DECIMAL(10, 6) NOT NULL,   -- €/Million Tokens
      output_price_vk DECIMAL(10, 6) NOT NULL,  -- €/Million Tokens

      -- Audio-spezifisch (€/Minute)
      audio_price_ek DECIMAL(10, 6),
      audio_price_vk DECIMAL(10, 6),

      -- Marge-Info
      margin_percentage DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE WHEN input_price_ek > 0
          THEN ((input_price_vk - input_price_ek) / input_price_ek * 100)
          ELSE 0
        END
      ) STORED,

      -- Status
      status VARCHAR(20) DEFAULT 'active',  -- active, deprecated, preview
      is_enabled BOOLEAN DEFAULT TRUE,

      -- Metadaten
      context_window INTEGER,
      max_output_tokens INTEGER,

      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Insert all model pricing
    INSERT INTO model_pricing (model_id, provider, tasks, input_price_ek, output_price_ek, input_price_vk, output_price_vk, status, context_window, max_output_tokens) VALUES
    ('qwen3-235b-a22b-instruct-2507', 'Qwen', ARRAY['chat'], 0.75, 2.25, 1.00, 3.00, 'active', 250000, 8192),
    ('qwen3-coder-30b-a3b-instruct', 'Qwen', ARRAY['chat'], 0.20, 0.80, 0.30, 1.10, 'active', 128000, 8192),
    ('qwen2.5-coder-32b-instruct', 'Qwen', ARRAY['chat'], 0.90, 0.90, 1.20, 1.20, 'deprecated', 128000, 8192),
    ('gpt-oss-120b', 'OpenAI', ARRAY['chat'], 0.15, 0.60, 0.20, 0.80, 'preview', 128000, 8192),
    ('gemma-3-27b-it', 'Google', ARRAY['chat', 'vision'], 0.25, 0.50, 0.35, 0.70, 'preview', 128000, 8192),
    ('holo2-30b-a3b', 'HCompany', ARRAY['chat', 'vision'], 0.30, 0.70, 0.40, 1.00, 'preview', 128000, 8192),
    ('voxtral-small-24b-2507', 'Mistral', ARRAY['chat', 'audio'], 0.15, 0.35, 0.20, 0.50, 'active', 32000, 8192),
    ('mistral-small-3.2-24b-instruct-2506', 'Mistral', ARRAY['chat', 'vision'], 0.15, 0.35, 0.20, 0.50, 'active', 128000, 8192),
    ('mistral-small-3.1-24b-instruct-2503', 'Mistral', ARRAY['chat', 'vision'], 0.15, 0.35, 0.20, 0.50, 'deprecated', 128000, 8192),
    ('mistral-nemo-instruct-2407', 'Mistral', ARRAY['chat'], 0.20, 0.20, 0.30, 0.30, 'active', 128000, 8192),
    ('devstral-small-2505', 'Mistral', ARRAY['chat'], 0.15, 0.35, 0.20, 0.50, 'preview', 128000, 8192),
    ('pixtral-12b-2409', 'Mistral', ARRAY['chat', 'vision'], 0.20, 0.20, 0.30, 0.30, 'active', 128000, 4096),
    ('llama-3.3-70b-instruct', 'Meta', ARRAY['chat'], 0.90, 0.90, 1.20, 1.20, 'active', 100000, 4096),
    ('llama-3.1-8b-instruct', 'Meta', ARRAY['chat'], 0.20, 0.20, 0.30, 0.30, 'active', 128000, 16384),
    ('deepseek-r1-distill-llama-70b', 'DeepSeek', ARRAY['chat'], 0.90, 0.90, 1.20, 1.20, 'active', 32000, 4096),
    ('bge-multilingual-gemma2', 'BAAI', ARRAY['embeddings'], 0.10, 0, 0.15, 0, 'active', 8192, NULL),
    ('qwen3-embedding-8b', 'Qwen', ARRAY['embeddings'], 0.10, 0, 0.15, 0, 'active', 32000, NULL);

    -- Audio-only model
    INSERT INTO model_pricing (model_id, provider, tasks, input_price_ek, output_price_ek, input_price_vk, output_price_vk, audio_price_ek, audio_price_vk, status) VALUES
    ('whisper-large-v3', 'OpenAI', ARRAY['audio'], 0, 0, 0, 0, 0.003, 0.005, 'preview');

    -- Index for quick lookups
    CREATE INDEX IF NOT EXISTS idx_model_pricing_model_id ON model_pricing(model_id);
    CREATE INDEX IF NOT EXISTS idx_model_pricing_status ON model_pricing(status);
    CREATE INDEX IF NOT EXISTS idx_model_pricing_is_enabled ON model_pricing(is_enabled);
    ```
  - **Akzeptanzkriterien:**
    - Alle Models mit korrekten Preisen
    - EK und VK getrennt
    - Marge automatisch berechnet

- [ ] **ADMIN-020**: Model Pricing Management UI
  - **Priorität:** Kritisch
  - **Route:** `/admin/settings/pricing`
  - **Beschreibung:** Admin-Interface zur Verwaltung der Model-Preise
  - **Features:**
    - **Pricing Table:**
      - Model Name, Provider, Tasks
      - Input EK / VK (editable)
      - Output EK / VK (editable)
      - Berechnete Marge (%)
      - Status (Active/Deprecated/Preview)
      - Enable/Disable Toggle
    - **Bulk Actions:**
      - Marge für alle Models anpassen (z.B. +10%)
      - Alle Preview-Models aktivieren/deaktivieren
    - **Price Calculator:**
      - Simuliere Request (Input Tokens, Output Tokens)
      - Zeige: EK, VK, Profit
    - **Import/Export:**
      - CSV Export der Preise
      - CSV Import für Bulk-Updates
  - **Backend:**
    - `GET /api/v1/admin/pricing` - Alle Preise laden
    - `PUT /api/v1/admin/pricing/{model_id}` - Preis aktualisieren
    - `POST /api/v1/admin/pricing/bulk-update` - Bulk-Update
  - **Akzeptanzkriterien:**
    - Preise können im Admin angepasst werden
    - Änderungen werden sofort wirksam
    - Marge wird korrekt berechnet

### 6.9 Testing & Quality

- [ ] **TEST-004**: Component Unit Tests
  - **Priorität:** Hoch
  - **Tool:** Vitest + React Testing Library
  - **Coverage:**
    - Alle Landing Components
    - Auth Forms
    - Dashboard Widgets
  - **Akzeptanzkriterien:**
    - 80%+ Coverage
    - Alle Tests grün

- [ ] **TEST-005**: E2E Tests
  - **Priorität:** Hoch
  - **Tool:** Playwright
  - **Flows:**
    - Landing → Signup → Verify → Dashboard
    - Login → Create API Key → Copy
    - Dashboard → Billing → Checkout
  - **Akzeptanzkriterien:**
    - Happy Paths funktionieren
    - CI Integration

### 6.10 Implementierungsplan Phase 6

| Task | Beschreibung | Aufwand |
|------|--------------|---------|
| **Frontend Setup** | | |
| FRONTEND-001 | Next.js Setup | 2h |
| FRONTEND-002 | Supabase Client | 2h |
| **Landing Page** | | |
| FRONTEND-003 | Landing Layout | 4h |
| FRONTEND-004 | Hero Section | 2h |
| FRONTEND-005 | Features Section | 2h |
| FRONTEND-006 | Pricing Section | 3h |
| FRONTEND-007 | FAQ Section | 2h |
| FRONTEND-008 | Testimonials | 2h |
| FRONTEND-009 | Footer | 1h |
| **Authentication** | | |
| FRONTEND-010 | Login Page | 3h |
| FRONTEND-011 | Signup Page | 3h |
| FRONTEND-012 | Password Reset | 2h |
| FRONTEND-013 | Email Verification | 1h |
| **User Dashboard** | | |
| FRONTEND-014 | Dashboard Layout | 4h |
| FRONTEND-015 | Dashboard Overview | 4h |
| FRONTEND-016 | API Keys Page (User) | 4h |
| FRONTEND-017 | Usage Analytics | 5h |
| FRONTEND-018 | Billing Page | 5h |
| FRONTEND-019 | Settings Page | 3h |
| **Admin Dashboard** | | |
| ADMIN-009 | Tenant Management | 5h |
| ADMIN-010 | License/API Key Management | 6h |
| ADMIN-011 | User Management | 4h |
| ADMIN-012 | Audit Log Viewer | 4h |
| ADMIN-013 | System Settings | 3h |
| ADMIN-014 | Analytics Dashboard | 5h |
| ADMIN-015 | Credit Top-Up Admin | 4h |
| ADMIN-016 | Privacy Shield Test Console | 6h |
| **Design & UX** | | |
| DESIGN-001 | Design System | 3h |
| DESIGN-002 | Dark Mode | 2h |
| DESIGN-003 | Responsive | 3h |
| I18N-001 | Internationalization | 4h |
| A11Y-002 | Accessibility Panel | 2h |
| A11Y-003 | WCAG Compliance | 3h |
| **Testing** | | |
| TEST-004 | Component Tests | 5h |
| TEST-005 | E2E Tests | 5h |

**Gesamt Phase 6:** ~112h (~14 Arbeitstage)

---

## 🔴 Phase 7: Public Pages & Landing Page Overhaul (KRITISCH)

> **Problem:** Aktuell leitet die Middleware alle nicht-authentifizierten Benutzer zum Login weiter.
> **Ziel:** Öffentliche Seiten (Landing, AGB, Datenschutz, etc.) ohne Login zugänglich machen.
> **Referenz:** Struktur aus `/root/Projekte/e-rechnung`

### 7.1 Middleware & Routing Fix

- [ ] **ROUTING-001**: Middleware für öffentliche Routen anpassen
  - **Priorität:** KRITISCH
  - **Datei:** `src/lib/supabase/middleware.ts`
  - **Problem:** Alle Routen leiten zu `/login` weiter
  - **Lösung:**
    - Definiere `publicRoutes` Array (Landing, AGB, Datenschutz, etc.)
    - Definiere `protectedRoutes` Array (Dashboard, Admin, Settings)
    - Nur `protectedRoutes` erfordern Authentifizierung
  - **Öffentliche Routen:**
    - `/` (Landing Page)
    - `/[locale]` (Lokalisierte Landing)
    - `/[locale]/agb` (AGB)
    - `/[locale]/datenschutz` (Datenschutz)
    - `/[locale]/impressum` (Impressum)
    - `/[locale]/avv` (AVV)
    - `/[locale]/accessibility` (Barrierefreiheit)
    - `/[locale]/docs` (Dokumentation)
    - `/[locale]/blog` (Blog)
    - `/[locale]/contact` (Kontakt)
    - `/[locale]/help` (Hilfe)
    - `/[locale]/changelog` (Changelog)
    - `/[locale]/status` (Status)
    - `/[locale]/login`, `/[locale]/signup`, `/[locale]/forgot-password`
  - **Geschützte Routen:**
    - `/[locale]/dashboard/*`
    - `/[locale]/admin/*`
    - `/[locale]/settings/*`
  - **Akzeptanzkriterien:**
    - Landing Page ohne Login erreichbar
    - Dashboard leitet zu Login weiter
    - Auth-Seiten leiten zu Dashboard wenn eingeloggt

### 7.2 Öffentliche Seiten erstellen

- [ ] **PUBLIC-001**: Landing Page Layout mit öffentlichem Header/Footer
  - **Priorität:** KRITISCH
  - **Dateien:**
    - `src/components/landing/PublicNavbar.tsx`
    - `src/components/landing/PublicFooter.tsx`
  - **PublicNavbar Features:**
    - Logo + Navigation Links (Funktionen, Preise, Blog, Hilfe)
    - Auth-State Detection (zeigt "Dashboard" wenn eingeloggt, sonst "Login/Registrieren")
    - LanguageSwitcher (DE/EN)
    - AccessibilityPanel Trigger
    - ModeToggle (Dark/Light)
    - Mobile Menu (Sheet)
  - **PublicFooter Features:**
    - Logo + Tagline
    - Produkt-Links (Features, Pricing, Blog, Docs, Changelog)
    - Rechtliches (Datenschutz, AGB, Impressum, AVV, Barrierefreiheit)
    - Support (Kontakt, Hilfe, Status)
    - Cookie-Einstellungen Button (`data-cc="show-preferencesModal"`)
    - Social Links (GitHub, Twitter, LinkedIn)
    - Copyright
  - **Akzeptanzkriterien:**
    - Navbar zeigt korrekten Auth-State
    - Footer-Links funktionieren
    - Responsive auf Mobile

- [ ] **PUBLIC-002**: AGB-Seite (Allgemeine Geschäftsbedingungen)
  - **Priorität:** KRITISCH
  - **Route:** `/[locale]/agb`
  - **Datei:** `src/app/[locale]/agb/page.tsx`
  - **Inhalt:**
    - PublicNavbar + PublicFooter
    - Strukturierte AGB (Geltungsbereich, Vertragsschluss, Leistungen, Preise, Zahlung, Haftung, etc.)
  - **Akzeptanzkriterien:**
    - Seite ohne Login erreichbar
    - Alle AGB-Abschnitte vorhanden

- [ ] **PUBLIC-003**: Datenschutz-Seite (DSGVO)
  - **Priorität:** KRITISCH
  - **Route:** `/[locale]/datenschutz`
  - **Datei:** `src/app/[locale]/datenschutz/page.tsx`
  - **Inhalt:**
    - Verantwortlicher, Datenschutzbeauftragter
    - Erhobene Daten, Zwecke, Rechtsgrundlage
    - Cookies, Drittanbieter, Rechte der Betroffenen
  - **Akzeptanzkriterien:**
    - DSGVO-konforme Datenschutzerklärung
    - Alle Pflichtangaben vorhanden

- [ ] **PUBLIC-004**: Impressum-Seite
  - **Priorität:** KRITISCH
  - **Route:** `/[locale]/impressum`
  - **Datei:** `src/app/[locale]/impressum/page.tsx`
  - **Inhalt:**
    - Angaben gem. § 5 TMG
    - Kontaktdaten, Vertretungsberechtigte
    - Handelsregister, USt-IdNr.
    - Verantwortlicher für Inhalt
  - **Akzeptanzkriterien:**
    - Alle gesetzlichen Pflichtangaben

- [ ] **PUBLIC-005**: AVV-Seite (Auftragsverarbeitungsvertrag)
  - **Priorität:** HOCH
  - **Route:** `/[locale]/avv`
  - **Datei:** `src/app/[locale]/avv/page.tsx`
  - **Inhalt:**
    - AVV gem. Art. 28 DSGVO
    - Gegenstand, Dauer, Art der Verarbeitung
    - Pflichten des Auftragsverarbeiters
    - Technische und organisatorische Maßnahmen (TOMs)
  - **Akzeptanzkriterien:**
    - Vollständiger AVV-Text

- [ ] **PUBLIC-006**: Barrierefreiheit-Seite
  - **Priorität:** HOCH
  - **Route:** `/[locale]/accessibility`
  - **Datei:** `src/app/[locale]/accessibility/page.tsx`
  - **Inhalt:**
    - Erklärung zur Barrierefreiheit (WCAG 2.1 AA)
    - Bekannte Einschränkungen
    - Feedback-Mechanismus
    - Durchsetzungsverfahren
  - **Akzeptanzkriterien:**
    - Barrierefreiheitserklärung gem. EU-Richtlinie

### 7.3 Cookie Consent Integration

- [ ] **COOKIE-001**: Cookie Consent Banner implementieren
  - **Priorität:** KRITISCH
  - **Library:** `vanilla-cookieconsent` v3.x
  - **Dateien:**
    - `src/components/marketing/CookieConsent.tsx`
    - Styling in `globals.css`
  - **Features:**
    - Consent Modal (Bottom Right)
    - Preferences Modal (Categories: Notwendig, Analyse)
    - Bilingual (DE/EN mit Browser-Autodetection)
    - Footer-Button zum erneuten Öffnen
  - **Kategorien:**
    - `necessary`: Immer aktiv, nicht abwählbar
    - `analytics`: Optional, standardmäßig aus
  - **Integration:**
    - In Root Layout einbinden
    - Footer-Button: `data-cc="show-preferencesModal"`
  - **Akzeptanzkriterien:**
    - Banner erscheint bei erstem Besuch
    - Einstellungen werden gespeichert
    - Footer-Button öffnet Preferences

### 7.4 Accessibility Integration (öffentliche Seiten)

- [ ] **A11Y-004**: SkipLink implementieren
  - **Priorität:** HOCH
  - **Datei:** `src/components/accessibility/SkipLink.tsx`
  - **Features:**
    - Visuell versteckt bis fokussiert (`sr-only` + `focus:not-sr-only`)
    - Springt zu `#main-content`
    - Erscheint bei Tab-Taste
  - **Akzeptanzkriterien:**
    - SkipLink funktioniert mit Tastatur
    - WCAG 2.1 AA konform

- [ ] **A11Y-005**: AccessibilityPanel auf öffentlichen Seiten
  - **Priorität:** HOCH
  - **Problem:** AccessibilityPanel nur im Dashboard
  - **Lösung:** In PublicNavbar integrieren
  - **Akzeptanzkriterien:**
    - Panel auf Landing Page verfügbar
    - Einstellungen werden gespeichert

- [ ] **A11Y-006**: Accessibility CSS-Klassen in globals.css
  - **Priorität:** HOCH
  - **Datei:** `src/app/globals.css`
  - **CSS-Klassen:**
    - `.high-contrast` - Schwarz/Weiß Modus
    - `.reduce-motion` - Animationen deaktivieren
    - `.larger-cursor` - Größerer Mauszeiger
    - `.underline-links` - Links unterstrichen
    - `.focus-highlight` - Gelbe Fokus-Umrandung
  - **Akzeptanzkriterien:**
    - Alle Accessibility-Modi funktionieren
    - Styles werden korrekt angewendet

### 7.5 Landing Page Verbesserung

- [ ] **LANDING-001**: Landing Page ohne Auth-Redirect
  - **Priorität:** KRITISCH
  - **Route:** `/` und `/[locale]`
  - **Datei:** `src/app/[locale]/page.tsx`
  - **Struktur:**
    ```
    PublicNavbar
    <main id="main-content">
      Hero
      Features
      Pricing
      Testimonials
      FAQ
      CTA
    </main>
    PublicFooter
    ```
  - **Akzeptanzkriterien:**
    - Landing Page ohne Login erreichbar
    - Alle Sektionen sichtbar
    - CTAs führen zu /signup

- [ ] **LANDING-002**: Pricing Section mit korrekten Links
  - **Priorität:** HOCH
  - **Problem:** CTA-Buttons müssen zu Checkout führen
  - **Lösung:**
    - Starter → `/signup`
    - Professional → `/signup?plan=professional`
    - Enterprise → `/contact`
  - **Akzeptanzkriterien:**
    - Pricing-CTAs funktionieren

### 7.6 Implementierungsplan Phase 7

| Task | Beschreibung | Aufwand |
|------|--------------|---------|
| **Routing** | | |
| ROUTING-001 | Middleware für öffentliche Routen | 2h |
| **Public Pages** | | |
| PUBLIC-001 | PublicNavbar + PublicFooter | 4h |
| PUBLIC-002 | AGB-Seite | 2h |
| PUBLIC-003 | Datenschutz-Seite | 2h |
| PUBLIC-004 | Impressum-Seite | 1h |
| PUBLIC-005 | AVV-Seite | 2h |
| PUBLIC-006 | Barrierefreiheit-Seite | 1h |
| **Cookie Consent** | | |
| COOKIE-001 | Cookie Consent Banner | 3h |
| **Accessibility** | | |
| A11Y-004 | SkipLink | 1h |
| A11Y-005 | AccessibilityPanel auf öffentlichen Seiten | 1h |
| A11Y-006 | Accessibility CSS-Klassen | 2h |
| **Landing Page** | | |
| LANDING-001 | Landing Page ohne Auth-Redirect | 2h |
| LANDING-002 | Pricing Links | 1h |

**Gesamt Phase 7:** ~24h (~3 Arbeitstage)

---

## 🤖 Phase 8: Scaleway Multi-Model Integration (AI-006)

> **Ziel:** Alle Scaleway Generative API Modelle individuell integrieren mit korrekten Spezifikationen.
> **API Base URL:** `https://api.scaleway.ai/v1`

### 8.1 Modell-Katalog (Stand: Dezember 2025)

#### Multimodal Models (Chat + Vision)

| Provider | Model String | Context Window | Max Output | License |
|----------|--------------|----------------|------------|---------|
| Google (Preview) | `gemma-3-27b-it` | 40k | 8192 | Gemma |
| Mistral | `mistral-small-3.2-24b-instruct-2506` | 128k | 8192 | Apache-2.0 |
| H | `holo2-30b-a3b` | 22k | 8192 | CC-BY-NC-4.0 |

#### Chat + Audio Models

| Provider | Model String | Context Window | Max Output | License |
|----------|--------------|----------------|------------|---------|
| Mistral | `voxtral-small-24b-2507` | 32k | 8192 | Apache-2.0 |

#### Audio Transcription Models

| Provider | Model String | Max Duration | Chunk Size | Max File Size | Temp | Top_P | License |
|----------|--------------|--------------|------------|---------------|------|-------|---------|
| Mistral | `voxtral-small-24b-2507` | 30 min | 30s | 25 MB | 0.2 | 0.95 | Apache-2.0 |
| OpenAI | `whisper-large-v3` | - | 30s | 25 MB | - | - | Apache-2.0 |

#### Chat Models

| Provider | Model String | Context Window | Max Output | Temp | Top_P | License |
|----------|--------------|----------------|------------|------|-------|---------|
| OpenAI | `gpt-oss-120b` | 128k | 8192 | 1.0 | 1.0 | Apache-2.0 |
| Meta | `llama-3.3-70b-instruct` | 100k | 4096 | 0.6 | 0.9 | Llama 3.3 |
| Meta | `llama-3.1-8b-instruct` | 128k | 16384 | 0.6 | 0.9 | Llama 3.1 |
| Mistral | `mistral-nemo-instruct-2407` | 128k | 8192 | 0.3 | 1.0 | Apache-2.0 |
| Mistral | `mistral-small-3.1-24b-instruct-2503` | 128k | 8192 | 0.15 | 1.0 | Apache-2.0 |
| Mistral | `devstral-small-2505` | 128k | 8192 | 0.15 | 1.0 | Apache-2.0 |
| Qwen | `qwen3-235b-a22b-instruct-2507` | 250k | 8192 | 0.7 | 0.8 | Apache-2.0 |
| Qwen | `qwen3-coder-30b-a3b-instruct` | 128k | 8192 | 0.7 | 0.8 | Apache-2.0 |
| Qwen | `qwen2.5-coder-32b-instruct` | 128k | 8192 | 0.8 | 0.7 | Apache-2.0 |
| DeepSeek | `deepseek-r1-distill-llama-70b` | 32k | 4096 | 0.6 | 0.95 | MIT |

#### Vision/Multimodal Models

| Provider | Model String | Context Window | Max Output | Temp | Top_P | License |
|----------|--------------|----------------|------------|------|-------|---------|
| Mistral | `pixtral-12b-2409` | 128k | 4096 | 0.7 | 1.0 | Apache-2.0 |
| Mistral | `mistral-small-3.2-24b-instruct-2506` | 128k | 8192 | 0.15 | 1.0 | Apache-2.0 |
| Google | `gemma-3-27b-it` | 128k | 8192 | 1.0 | 0.95 | Gemma |
| HoloVision | `holo2-30b-a3b` | 128k | 8192 | 0.8 | 0.95 | Apache-2.0 |

> **Note:** Image sizes are limited to 32 million pixels (e.g., ~8096x4048). Images >1024x1024 are automatically downscaled.

#### Embedding Models

| Provider | Model String | Max Dimension | Min Dimension | Context Window | License |
|----------|--------------|---------------|---------------|----------------|---------|
| Qwen | `qwen3-embedding-8b` | 4096 | 32 | 32000 | Apache-2.0 |
| BAAI | `bge-multilingual-gemma2` | 3584 | 3584 | 8192 | Gemma |

### 8.1b Preismodell (Einkauf & Verkauf)

> **Wichtig:** Preise sind pro Million Tokens (außer Audio = pro Minute)

#### Scaleway Einkaufspreise (Stand: Dezember 2025)

| Model | Provider | Tasks | Input (EK) | Output (EK) | Status |
|-------|----------|-------|------------|-------------|--------|
| `qwen3-235b-a22b-instruct-2507` | Qwen | Chat | €0.75/M | €2.25/M | Active |
| `qwen3-coder-30b-a3b-instruct` | Qwen | Chat | €0.20/M | €0.80/M | Active |
| `qwen2.5-coder-32b-instruct` | Qwen | Chat | €0.90/M | €0.90/M | Deprecated |
| `gpt-oss-120b` | OpenAI | Chat | €0.15/M | €0.60/M | Preview |
| `gemma-3-27b-it` | Google | Chat, Vision | €0.25/M | €0.50/M | Preview |
| `holo2-30b-a3b` | HCompany | Chat, Vision | €0.30/M | €0.70/M | Preview |
| `voxtral-small-24b-2507` | Mistral | Chat, Audio | €0.15/M | €0.35/M | Active |
| `mistral-small-3.2-24b-instruct-2506` | Mistral | Chat, Vision | €0.15/M | €0.35/M | Active |
| `mistral-small-3.1-24b-instruct-2503` | Mistral | Chat, Vision | €0.15/M | €0.35/M | Deprecated |
| `mistral-nemo-instruct-2407` | Mistral | Chat | €0.20/M | €0.20/M | Active |
| `devstral-small-2505` | Mistral | Chat | €0.15/M | €0.35/M | Preview |
| `pixtral-12b-2409` | Mistral | Chat, Vision | €0.20/M | €0.20/M | Active |
| `llama-3.3-70b-instruct` | Meta | Chat | €0.90/M | €0.90/M | Active |
| `llama-3.1-8b-instruct` | Meta | Chat | €0.20/M | €0.20/M | Active |
| `deepseek-r1-distill-llama-70b` | DeepSeek | Chat | €0.90/M | €0.90/M | Active |
| `whisper-large-v3` | OpenAI | Audio | €0.003/min | Free | Preview |
| `bge-multilingual-gemma2` | BAAI | Embeddings | €0.10/M | Free | Active |
| `qwen3-embedding-8b` | Qwen | Embeddings | €0.10/M | Free | Active |

#### Verkaufspreise (Empfohlene Marge: 30-50%)

| Model | Input (VK) | Output (VK) | Marge | Credits/1K Tokens |
|-------|------------|-------------|-------|-------------------|
| `qwen3-235b-a22b-instruct-2507` | €1.00/M | €3.00/M | 33% | 0.001 / 0.003 |
| `qwen3-coder-30b-a3b-instruct` | €0.30/M | €1.10/M | 37% | 0.0003 / 0.0011 |
| `gpt-oss-120b` | €0.20/M | €0.80/M | 33% | 0.0002 / 0.0008 |
| `gemma-3-27b-it` | €0.35/M | €0.70/M | 40% | 0.00035 / 0.0007 |
| `holo2-30b-a3b` | €0.40/M | €1.00/M | 40% | 0.0004 / 0.001 |
| `voxtral-small-24b-2507` | €0.20/M | €0.50/M | 40% | 0.0002 / 0.0005 |
| `mistral-small-3.2-24b-instruct-2506` | €0.20/M | €0.50/M | 40% | 0.0002 / 0.0005 |
| `mistral-nemo-instruct-2407` | €0.30/M | €0.30/M | 50% | 0.0003 / 0.0003 |
| `devstral-small-2505` | €0.20/M | €0.50/M | 40% | 0.0002 / 0.0005 |
| `pixtral-12b-2409` | €0.30/M | €0.30/M | 50% | 0.0003 / 0.0003 |
| `llama-3.3-70b-instruct` | €1.20/M | €1.20/M | 33% | 0.0012 / 0.0012 |
| `llama-3.1-8b-instruct` | €0.30/M | €0.30/M | 50% | 0.0003 / 0.0003 |
| `deepseek-r1-distill-llama-70b` | €1.20/M | €1.20/M | 33% | 0.0012 / 0.0012 |
| `whisper-large-v3` | €0.005/min | Free | 67% | 0.005/min |
| `bge-multilingual-gemma2` | €0.15/M | Free | 50% | 0.00015 |
| `qwen3-embedding-8b` | €0.15/M | Free | 50% | 0.00015 |

#### Preisberechnungslogik

```python
# Credit-Berechnung pro Request
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input_vk"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_vk"]
    return input_cost + output_cost

# Beispiel: qwen3-235b mit 1000 Input + 500 Output Tokens
# Input:  (1000 / 1M) * €1.00 = €0.001
# Output: (500 / 1M) * €3.00 = €0.0015
# Total:  €0.0025 = 0.0025 Credits
```

### 8.2 API Code Examples (Pro Modell)

> **Base URL:** `https://api.scaleway.ai/{PROJECT_ID}/v1`
> **Auth:** Bearer Token mit Scaleway IAM API Key (SCW_SECRET_KEY)
> **Note:** Ersetze `{PROJECT_ID}` mit deiner Scaleway Project ID

---

#### Chat Models

##### GPT-OSS 120B
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=1,
    top_p=1,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Llama 3.3 70B Instruct
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="llama-3.3-70b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.6,
    top_p=0.9,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Llama 3.1 8B Instruct
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.6,
    top_p=0.9,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Mistral Nemo Instruct 2407
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="mistral-nemo-instruct-2407",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.3,
    top_p=1,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Qwen3 235B A22B Instruct (250k Context)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="qwen3-235b-a22b-instruct-2507",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.7,
    top_p=0.8,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Qwen3 Coder 30B A3B Instruct
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="qwen3-coder-30b-a3b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.7,
    top_p=0.8,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### DeepSeek R1 Distill Llama 70B
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="deepseek-r1-distill-llama-70b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.6,
    top_p=0.95,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

#### Multimodal Models (Chat + Vision)

##### Gemma 3 27B IT (Preview)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

# Text-only
response = client.chat.completions.create(
    model="gemma-3-27b-it",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=1,
    top_p=0.95,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# With Vision
response = client.chat.completions.create(
    model="gemma-3-27b-it",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
            ]
        }
    ],
    max_tokens=1024
)
print(response.choices[0].message.content)
```

##### Mistral Small 3.2 24B Instruct (Recommended)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

# Text-only
response = client.chat.completions.create(
    model="mistral-small-3.2-24b-instruct-2506",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.15,
    top_p=1,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# With Vision
response = client.chat.completions.create(
    model="mistral-small-3.2-24b-instruct-2506",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail"},
                {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
            ]
        }
    ],
    max_tokens=1024
)
print(response.choices[0].message.content)
```

##### Holo2 30B A3B
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

# Text-only
response = client.chat.completions.create(
    model="holo2-30b-a3b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.8,
    top_p=0.95,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# With Vision
response = client.chat.completions.create(
    model="holo2-30b-a3b",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
            ]
        }
    ],
    max_tokens=1024
)
print(response.choices[0].message.content)
```

---

#### Vision-Only Models

##### Pixtral 12B 2409
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

# Chat (Text-only)
response = client.chat.completions.create(
    model="pixtral-12b-2409",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.7,
    top_p=1,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# With Vision
response = client.chat.completions.create(
    model="pixtral-12b-2409",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image and describe what you see"},
                {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
            ]
        }
    ],
    max_tokens=1024
)
print(response.choices[0].message.content)
```

---

#### Audio Models

##### Voxtral Small 24B (Chat + Audio + Transcription)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

# Chat
response = client.chat.completions.create(
    model="voxtral-small-24b-2507",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.2,
    top_p=0.95,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# Audio Transcription
audio_path = "path/to/file/audio.mp3"  # Replace with path to your local file

with open(audio_path, "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="voxtral-small-24b-2507",
        file=f.read(),
        prompt="You are a helpful assistant",
        language="en"
    )
print(transcript.text)
```

##### Whisper Large V3 (Transcription Only)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

audio_path = "path/to/file/audio.mp3"  # Replace with path to your local file

with open(audio_path, "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=f.read(),
        prompt="You are a helpful assistant",
        language="en"
    )

print(transcript.text)
```

---

#### Embedding Models

##### Qwen3 Embedding 8B (Dimension: 32-4096)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.embeddings.create(
    input="Example text to embed",
    model="qwen3-embedding-8b",
)

print(response.data[0].embedding)
print("Printed embedding vector with", len(response.data[0].embedding), "dimensions")
```

##### BGE Multilingual Gemma2 (Dimension: 3584 fixed)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.embeddings.create(
    input="Example text to embed",
    model="bge-multilingual-gemma2",
)

print(response.data[0].embedding)
print("Printed embedding vector with", len(response.data[0].embedding), "dimensions")
```

---

#### Additional Chat Models

##### Mistral Small 3.1 24B Instruct
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="mistral-small-3.1-24b-instruct-2503",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.15,
    top_p=1,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Qwen2.5 Coder 32B Instruct
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="qwen2.5-coder-32b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.8,
    top_p=0.7,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Devstral Small 2505
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.scaleway.ai/{PROJECT_ID}/v1",  # Replace {PROJECT_ID}
    api_key="SCW_SECRET_KEY"  # Replace with your IAM API key
)

response = client.chat.completions.create(
    model="devstral-small-2505",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": ""},
    ],
    max_tokens=512,
    temperature=0.15,
    top_p=1,
    presence_penalty=0,
    stream=True,
    response_format={"type": "text"}
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 8.3 Implementation Tasks

- [ ] **AI-006a**: Update ScalewayProvider with correct model specifications
  - **Datei:** `app/services/scaleway_provider.py`
  - **Aufgaben:**
    - Korrigiere Context Window und Max Output Werte
    - Füge Lizenz-Informationen hinzu
    - Aktualisiere SCALEWAY_MODELS Dictionary
  - **Aufwand:** 2h

- [ ] **AI-006b**: Implement Vision API Support
  - **Datei:** `app/services/scaleway_provider.py`
  - **Aufgaben:**
    - `generate_with_image()` Methode
    - Image URL und Base64 Support
    - Automatic downscaling info
  - **Aufwand:** 3h

- [ ] **AI-006c**: Implement Audio Transcription API
  - **Datei:** `app/services/scaleway_provider.py`
  - **Aufgaben:**
    - `transcribe_audio()` Methode
    - File upload handling (max 25MB)
    - Chunk handling (30s)
  - **Aufwand:** 3h

- [ ] **AI-006d**: Implement Embeddings API
  - **Datei:** `app/services/scaleway_provider.py`
  - **Aufgaben:**
    - `create_embeddings()` Methode
    - Batch processing support
    - Dimension validation
  - **Aufwand:** 2h

- [ ] **AI-006e**: Add Model Selection to API
  - **Datei:** `app/api/v1/generate.py`
  - **Aufgaben:**
    - `model` Parameter im Request
    - Modell-Validierung
    - `/v1/models` Endpoint für verfügbare Modelle
  - **Aufwand:** 2h

- [ ] **AI-006f**: Write Unit Tests for Scaleway Models
  - **Datei:** `app/tests/test_scaleway_provider.py`
  - **Aufgaben:**
    - Test alle Modell-Typen
    - Mock API responses
    - Test error handling
  - **Aufwand:** 3h

### 8.4 Implementierungsplan Phase 8

| Task | Beschreibung | Aufwand |
|------|--------------|---------|
| AI-006a | Model Specifications Update | 2h |
| AI-006b | Vision API Support | 3h |
| AI-006c | Audio Transcription API | 3h |
| AI-006d | Embeddings API | 2h |
| AI-006e | Model Selection API | 2h |
| AI-006f | Unit Tests | 3h |

**Gesamt Phase 8:** ~15h (~2 Arbeitstage)

---

## 🌐 Phase 9: Google Vertex AI Integration (AI-007)

> **Ziel:** Claude und Gemini über Google Vertex AI EU integrieren für 100% DSGVO-Konformität.
> **Region:** `europe-west3` (Frankfurt) - Keine US-Datenübertragung
> **DSGVO:** ✅ EU Data Residency mit Google's EU-Datenschutzgarantien

### 9.1 Provider-Strategie (Aktualisiert)

| Priorität | Provider | Region | Modelle | DSGVO | Use Case |
|-----------|----------|--------|---------|-------|----------|
| **1** | Scaleway | FR/EU | Llama, Mistral, Qwen, Whisper | ✅ 100% EU | Kostengünstig, Open-Source |
| **2** | Vertex AI EU | DE (Frankfurt) | Claude 3.5, Gemini Pro | ✅ EU | Premium Quality, DSGVO-konform |
| **3** | Anthropic Direct | US | Claude (Fallback) | ⚠️ SCCs | Nur wenn Vertex nicht verfügbar |

### 9.2 Verfügbare Modelle auf Vertex AI EU

#### Claude Modelle (via Anthropic on Vertex)

| Model | Model String | Context | Max Output | Temp | Pricing (Input/Output) |
|-------|--------------|---------|------------|------|------------------------|
| Claude 3.5 Sonnet v2 | `claude-3-5-sonnet-v2@20241022` | 200k | 8192 | 0.0-1.0 | $3.00/$15.00 per M |
| Claude 3.5 Sonnet | `claude-3-5-sonnet@20240620` | 200k | 8192 | 0.0-1.0 | $3.00/$15.00 per M |
| Claude 3 Opus | `claude-3-opus@20240229` | 200k | 4096 | 0.0-1.0 | $15.00/$75.00 per M |
| Claude 3 Sonnet | `claude-3-sonnet@20240229` | 200k | 4096 | 0.0-1.0 | $3.00/$15.00 per M |
| Claude 3 Haiku | `claude-3-haiku@20240307` | 200k | 4096 | 0.0-1.0 | $0.25/$1.25 per M |

#### Gemini Modelle

| Model | Model String | Context | Max Output | Temp | Pricing (Input/Output) |
|-------|--------------|---------|------------|------|------------------------|
| Gemini 2.0 Flash | `gemini-2.0-flash-001` | 1M | 8192 | 0.0-2.0 | $0.075/$0.30 per M |
| Gemini 1.5 Pro | `gemini-1.5-pro-002` | 2M | 8192 | 0.0-2.0 | $1.25/$5.00 per M |
| Gemini 1.5 Flash | `gemini-1.5-flash-002` | 1M | 8192 | 0.0-2.0 | $0.075/$0.30 per M |

### 9.3 API Code Examples

#### Claude via Vertex AI (Frankfurt)

```python
import anthropic

# Claude via Vertex AI EU (Frankfurt)
client = anthropic.AnthropicVertex(
    region="europe-west3",  # Frankfurt - EU Data Residency
    project_id="your-gcp-project-id"
)

response = client.messages.create(
    model="claude-3-5-sonnet-v2@20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)
print(response.content[0].text)
```

#### Gemini via Vertex AI (Frankfurt)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI with EU region
vertexai.init(
    project="your-gcp-project-id",
    location="europe-west3"  # Frankfurt - EU Data Residency
)

model = GenerativeModel("gemini-1.5-pro-002")

response = model.generate_content(
    "Hello, Gemini!",
    generation_config={
        "max_output_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.95,
    }
)
print(response.text)
```

#### Claude Streaming via Vertex AI

```python
import anthropic

client = anthropic.AnthropicVertex(
    region="europe-west3",
    project_id="your-gcp-project-id"
)

with client.messages.stream(
    model="claude-3-5-sonnet-v2@20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a poem about GDPR"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### 9.4 Preismodell Vertex AI (Einkauf & Verkauf)

#### Einkaufspreise (Google Cloud Pricing, Stand: Dezember 2025)

| Model | Provider | Input (EK) | Output (EK) | Status |
|-------|----------|------------|-------------|--------|
| `claude-3-5-sonnet-v2@20241022` | Anthropic | $3.00/M | $15.00/M | Active |
| `claude-3-5-sonnet@20240620` | Anthropic | $3.00/M | $15.00/M | Active |
| `claude-3-opus@20240229` | Anthropic | $15.00/M | $75.00/M | Active |
| `claude-3-haiku@20240307` | Anthropic | $0.25/M | $1.25/M | Active |
| `gemini-2.0-flash-001` | Google | $0.075/M | $0.30/M | Active |
| `gemini-1.5-pro-002` | Google | $1.25/M | $5.00/M | Active |
| `gemini-1.5-flash-002` | Google | $0.075/M | $0.30/M | Active |

#### Verkaufspreise (Empfohlene Marge: 25-40%)

| Model | Input (VK) | Output (VK) | Marge | EUR equivalent |
|-------|------------|-------------|-------|----------------|
| `claude-3-5-sonnet-v2` | $4.00/M | $20.00/M | 33% | ~€3.70/€18.50 |
| `claude-3-opus` | $20.00/M | $100.00/M | 33% | ~€18.50/€92.50 |
| `claude-3-haiku` | $0.35/M | $1.75/M | 40% | ~€0.32/€1.62 |
| `gemini-2.0-flash` | $0.10/M | $0.40/M | 33% | ~€0.09/€0.37 |
| `gemini-1.5-pro` | $1.75/M | $7.00/M | 40% | ~€1.62/€6.48 |
| `gemini-1.5-flash` | $0.10/M | $0.40/M | 33% | ~€0.09/€0.37 |

> **Note:** Preise in USD, da Google Cloud Billing. EUR-Konvertierung bei ~0.925 EUR/USD.

### 9.5 Implementation Tasks

- [x] **AI-007a**: Create VertexAI Provider Base Class ✅
  - **Datei:** `app/services/vertex_provider.py`
  - **Aufgaben:**
    - GCP Authentication (Service Account JSON)
    - Region-Konfiguration (europe-west3)
    - Base client initialization
    - Data residency enum (EU, US, GLOBAL)
    - DSGVO compliance property
  - **Abgeschlossen:** 2025-12-08

- [x] **AI-007b**: Implement Claude via Vertex AI Adapter ✅
  - **Datei:** `app/services/vertex_claude_provider.py`
  - **Aufgaben:**
    - `AnthropicVertex` Client Integration
    - Streaming Support
    - Token counting
    - 5 Claude models supported
  - **Abgeschlossen:** 2025-12-08

- [x] **AI-007c**: Implement Gemini via Vertex AI Adapter ✅
  - **Datei:** `app/services/vertex_gemini_provider.py`
  - **Aufgaben:**
    - `GenerativeModel` Integration
    - Streaming Support
    - Multi-modal (Vision) Support
    - 3 Gemini models supported
  - **Abgeschlossen:** 2025-12-08

- [x] **AI-007d**: Add Vertex AI Models to Provider Registry ✅
  - **Datei:** `app/api/v1/generate.py`
  - **Aufgaben:**
    - Provider factory function `get_provider_instance()`
    - 4 providers: anthropic, scaleway, vertex_claude, vertex_gemini
    - EU-only constraint for DSGVO compliance
    - `/v1/providers` endpoint added
  - **Abgeschlossen:** 2025-12-08

- [x] **AI-007e**: Update Environment Configuration ✅
  - **Datei:** `app/core/config.py`, `.env.example`
  - **Aufgaben:**
    - `GCP_PROJECT_ID` Variable
    - `GCP_REGION` Variable (default: europe-west3)
    - `GOOGLE_APPLICATION_CREDENTIALS` Path
  - **Abgeschlossen:** 2025-12-08

- [x] **AI-007f**: Add Vertex AI Pricing to Model Pricing Table ✅
  - **Datei:** `migrations/012_add_vertex_ai_models.sql`
  - **Aufgaben:**
    - Insert Claude models with pricing (5 models)
    - Insert Gemini models with pricing (3 models)
    - region and data_residency columns added
    - Performance indexes included
  - **Abgeschlossen:** 2025-12-08

- [x] **AI-007g**: Write Unit Tests for Vertex AI Providers ✅
  - **Datei:** `app/tests/test_vertex_provider.py`
  - **Aufgaben:**
    - Mock GCP credentials
    - Test Claude via Vertex (20+ tests)
    - Test Gemini via Vertex (20+ tests)
    - Test error handling
    - **60 tests, 96% coverage**
  - **Abgeschlossen:** 2025-12-08

- [x] **DB-012**: Add provider_region Column for EU Compliance ✅
  - **Migration:** `migrations/012_add_vertex_ai_models.sql`
  - **Aufgaben:**
    - Add `region` column to `model_pricing`
    - Add `data_residency` enum (EU, US, GLOBAL)
    - Update existing models
  - **Abgeschlossen:** 2025-12-08

### 9.6 DSGVO Compliance Checklist

- [ ] **GDPR-001**: EU Data Residency Configuration
  - Region: `europe-west3` (Frankfurt)
  - No data transfer to US
  - Google's Standard Contractual Clauses (SCCs)

- [ ] **GDPR-002**: Data Processing Agreement
  - GCP Data Processing Addendum signed
  - Anthropic via Vertex DPA included
  - Document in `/docs/legal/`

- [ ] **GDPR-003**: Model Selection Logic
  - EU tenants → Vertex AI EU only
  - US tenants → Any provider allowed
  - Admin can override per tenant

### 9.7 Provider Failover Logic (Updated)

```python
# Updated failover chain for EU compliance
EU_PROVIDER_CHAIN = [
    "scaleway",           # 1. FR/EU - Cheapest
    "vertex_claude",      # 2. DE - Premium Quality
    "vertex_gemini",      # 3. DE - Fast & Multimodal
    "anthropic_direct",   # 4. US - Only with explicit consent
]

# Model mapping for failover
MODEL_EQUIVALENTS = {
    "claude-3-5-sonnet": {
        "vertex": "claude-3-5-sonnet-v2@20241022",
        "anthropic": "claude-3-5-sonnet-20241022"
    },
    "fast": {
        "scaleway": "mistral-small-3.2-24b-instruct-2506",
        "vertex": "gemini-2.0-flash-001"
    },
    "cheap": {
        "scaleway": "llama-3.1-8b-instruct",
        "vertex": "claude-3-haiku@20240307"
    }
}
```

### 9.8 Implementierungsplan Phase 9

| Task | Beschreibung | Aufwand |
|------|--------------|---------|
| AI-007a | Vertex Provider Base Class | 3h |
| AI-007b | Claude via Vertex Adapter | 4h |
| AI-007c | Gemini via Vertex Adapter | 4h |
| AI-007d | Provider Registry Update | 2h |
| AI-007e | Environment Config | 1h |
| AI-007f | Pricing Migration | 1h |
| AI-007g | Unit Tests | 3h |
| DB-012 | Region Column | 1h |
| GDPR-001 | EU Config | 1h |
| GDPR-002 | DPA Documentation | 2h |
| GDPR-003 | Model Selection Logic | 2h |

**Gesamt Phase 9:** ~24h (~3 Arbeitstage)

---

**Document Version:** 7.0
**Owner:** Technical Lead
**Last Review:** 2025-12-08
