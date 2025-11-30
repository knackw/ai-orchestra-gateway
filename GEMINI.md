# GEMINI.md

This document provides guidance to **Gemini CLI / Gemini Code Assist** (ai.google.dev/gemini-api) when working with this repository.

You are Gemini, Google's AI assistant. You work alongside Claude Code to maintain and develop the **AI Legal Ops (SaaS Proxy & Gateway)**. Use the instructions below and reference CLAUDE.md for shared project-wide rules.

**IMPORTANT:** If CLAUDE.md and GEMINI.md ever conflict, **project-wide rules in CLAUDE.md take precedence**.

---

## 📋 Project Overview

**AI Legal Ops** is a high-security middleware for AI orchestration, billing, and privacy enforcement.

### Project Vision

Enable SaaS providers to integrate AI capabilities (Anthropic, Scaleway, etc.) with strict privacy controls (PII Shield) and multi-tenant management.

### Core Mission

Route AI requests, enforce privacy (remove PII before sending to AI), manage tenant billing (credits), and ensure auditability.

---

## 📁 File Organization Rules (MANDATORY)

**CRITICAL:** All files in this project MUST follow this organization structure.

### Project Structure Overview

```
ai-legal-proxy/
├── app/                              # Python/FastAPI Application
│   ├── __init__.py
│   ├── main.py                       # Entry Point
│   ├── core/                         # Config & Security
│   │   ├── config.py
│   │   └── security.py
│   ├── api/                          # API Routes
│   │   └── v1/
│   │       ├── endpoints.py
│   │       └── deps.py
│   ├── services/                     # Business Logic
│   │   ├── ai_gateway.py             # AI Provider Routing
│   │   ├── privacy.py                # PII Shield (Redaction)
│   │   └── billing.py                # Credit Deduction
│   └── tests/                        # Pytest Suite
│       ├── conftest.py
│       └── test_api.py
│
├── .github/                          # GitHub Actions
│   └── workflows/
│       └── ci-cd.yaml
│
├── docs/                             # Documentation
│   ├── PROJEKTPLAN.md                # Master project plan
│   ├── TASKS.md                      # Implementation tasks
│
├── pyproject.toml                    # QA Config (Ruff, Pytest)
├── Dockerfile                        # Production Container
├── docker-compose.yml                # Local Dev Environment
├── GEMINI.md                         # This file
├── CLAUDE.md                         # Claude instructions
└── README.md                         # Project README
```

### Placement Rules

**✅ DO - Backend (Python/FastAPI):**
- Place all application code in `app/`
- Place business logic in `app/services/`
- Place API routes in `app/api/`
- Place tests in `app/tests/`

**✅ DO - Documentation:**
- Place ALL documentation in `docs/`

**❌ DON'T:**
- ❌ Create frontend code (unless explicitly requested for a demo)
- ❌ Hardcode credentials (use `.env` files)

---

## ⚠️ CRITICAL: Architecture Overview

### Multi-Tenant Middleware

**Gateway:** Python/FastAPI → **Database:** Supabase (PostgreSQL) → **AI Providers:** Anthropic/Scaleway

### Tech Stack

**Backend (Python 3.11+)**
- **Framework:** FastAPI (async REST API)
- **Validation:** Pydantic
- **HTTP Client:** httpx
- **Linting:** Ruff

**Database & Storage (Supabase)**
- **Database:** PostgreSQL 15+ (Frankfurt region, EU)
- **Auth:** Supabase Auth (Multi-tenancy)
- **Billing:** RPC functions for atomic credit deduction

### Core Services

1. **AI Gateway:** Central router for AI requests. Handles provider switching and API key management.
2. **Privacy Shield:** Analyzes input text for PII (Email, Phone, IBAN, Names) and replaces it with placeholders (e.g., `<EMAIL_REMOVED>`) *before* the data leaves the server.
3. **Billing:** Checks and deducts credits from the tenant's license *before* processing the request.

---

## Compliance & Privacy (CRITICAL)

**Privacy First:**
- **PII Shield:** MANDATORY. No personal data sent to AI providers without sanitization.
- **Logging:** NEVER log PII. Use `DataPrivacyShield` to sanitize logs.

### Implementation Rules

**DO:**
- ✅ Implement `DataPrivacyShield` class with regex patterns for PII.
- ✅ Use atomic DB transactions for billing (prevent race conditions).
- ✅ Validate Tenant API Keys on every request.

**DON'T:**
- ❌ Log raw user input.
- ❌ Send PII to external AI providers.
- ❌ Hardcode API keys.

---

## Coding Guidelines

### Python (Backend)

**Style:** PEP 8, Ruff (Linting/Formatting), Black compatible
**Type Hints:** Mandatory
**Testing:** pytest, mock external API calls

```python
# Example: Privacy Shield
import re
import logging

logger = logging.getLogger("privacy_shield")

class DataPrivacyShield:
    PATTERNS = {
        "email": r'[\w\.-]+@[\w\.-]+\.\w+',
        "phone": r'(\+49|0)[1-9][0-9 \-\.]+'
    }

    @classmethod
    def sanitize(cls, text: str) -> tuple[str, bool]:
        # Implementation to remove PII
        ...
```

---

## Testing Strategy

**Command:**
```bash
pytest
```

**Strategy:**
- **Mocking:** Do NOT call real AI APIs in tests. Mock `app.services.ai_gateway.call_provider`.
- **Coverage:** Aim for high coverage on core logic (Billing, Privacy).
- **Security:** Test that PII is correctly redacted.

---

## Deployment

**Production:** Docker Compose
**CI/CD:** GitHub Actions (Linting + Tests required before deploy)

**Environment Variables:**
```bash
SUPABASE_URL=...
SUPABASE_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

---

## Reference Docs

- `docs/PROJEKTPLAN.md` - Master Technical Concept
- `docs/TASKS.md` - Implementation Tasks
- `CLAUDE.md` - Project Rules

**Version:** 2.0 - AI Legal Ops Adaptation
