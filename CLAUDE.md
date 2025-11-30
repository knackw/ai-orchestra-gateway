# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📋 Project Overview

**AI Legal Ops (SaaS Proxy & Gateway)** - A high-security middleware for AI orchestration, billing, and privacy enforcement.

**Version:** 2.0 (Enterprise / White-Label Ready)
**Vision:** Enable SaaS providers to integrate AI capabilities with strict privacy controls (PII Shield) and multi-tenant management.

---

## 📁 File Organization

```
ai-legal-proxy/
├── app/
│   ├── __init__.py
│   ├── main.py             # Entry Point
│   ├── core/               # Config & Security
│   ├── api/                # API Routes (v1)
│   ├── services/           # Business Logic (AI, Privacy, Billing)
│   └── tests/              # Pytest Suite
├── .github/
│   └── workflows/          # CI/CD
├── pyproject.toml          # QA Config (Ruff, Pytest)
├── Dockerfile              # Production Container
└── docker-compose.yml      # Local Dev Environment
```

**Rules:**
- ✅ Backend code → `app/` (Python/FastAPI)
- ✅ Documentation → `docs/`
- ❌ NO frontend code in this repo (unless specified)
- 🚨 **STRICT:** For every task, you MUST follow `docs/prompts/PROMPT_IMPLEMENT.md` (Tests, Versioning, Changelog, History).

---

## ⚠️ Architecture

### Multi-Tenant Middleware
**Gateway:** Python/FastAPI → **Database:** Supabase (PostgreSQL) → **AI Providers:** Anthropic/Scaleway

**Tech Stack:**
- **Python 3.11:** FastAPI, Pydantic, httpx
- **Supabase:** Multi-tenant DB, Auth, RPC for billing
- **Redis:** Rate limiting (optional/future)
- **Docker:** Containerization for production

**Core Services:**
1. **AI Gateway:** Routes requests to providers (Anthropic, etc.)
2. **Privacy Shield:** Detects and redacts PII (Email, Phone, IBAN) before sending to AI
3. **Billing:** Deducts credits per request using atomic DB transactions

---

## Compliance & Privacy (CRITICAL)

**Privacy First:**
- **PII Shield:** MANDATORY. No personal data sent to AI providers without sanitization.
- **Logging:** NEVER log PII. Use `DataPrivacyShield` to sanitize logs.

---

## Coding Guidelines

### Python (Backend)

**Style:** PEP 8, Ruff (Linting/Formatting), Black compatible
**Type Hints:** Mandatory
**Testing:** pytest, mock external API calls

```python
# Example: Privacy Shield
class DataPrivacyShield:
    @classmethod
    def sanitize(cls, text: str) -> tuple[str, bool]:
        # Implementation to remove PII
        ...
```

---

## Testing

**Command:**
```bash
pytest
```

**Strategy:**
- **Mocking:** Do NOT call real AI APIs in tests. Mock `app.services.ai_gateway.call_provider`.
- **Coverage:** Aim for high coverage on core logic (Billing, Privacy).

---

## Deployment

**Production:** Docker Compose
**CI/CD:** GitHub Actions (Linting + Tests required before deploy)

---

## Reference Docs

- `docs/PROJEKTPLAN.md` - Master Technical Concept
- `docs/TASKS.md` - Implementation Tasks
- `GEMINI.md` - Gemini Instructions

**Version:** 2.0 - AI Legal Ops Adaptation
