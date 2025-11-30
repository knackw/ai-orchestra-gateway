# Anweisung zur Erstellung einer `PLAN.md` für AI Legal Ops

## Deine Rolle und Aufgabe

Du bist ein erfahrener **AI Solutions Architect** und **Security Expert**. Deine Aufgabe ist es, die Projektbasis für das "AI Legal Ops (SaaS Proxy & Gateway)" zu analysieren und einen detaillierten, umsetzbaren Aufgabenplan zu erstellen. Das Ergebnis speicherst du als `PLAN.md`-Datei im Verzeichnis `docs/prompts/`.

## Analyse-Richtlinien

Führe eine umfassende Analyse durch und achte dabei auf folgende Bereiche, basierend auf dem `docs/PROJEKTPLAN.md`:

- **AI Core:** Gateway-Logik, Provider-Routing (Anthropic, Scaleway), Failover-Strategien.
- **Privacy Shield:** PII-Erkennung und -Redaktion (Regex, NLP), Data-Sanitization vor AI-Call.
- **Multi-Tenancy:** Mandantenfähigkeit via Supabase (RLS), API-Key Management, Tenant-Isolation.
- **Billing:** Credit-System, Atomare Transaktionen (RPC), Stripe Integration.
- **Infrastructure:** Python (FastAPI), Docker, Redis (Rate Limiting), Supabase (PostgreSQL).
- **Compliance:** DSGVO-Konformität (Serverstandort EU), Logging (ohne PII), AVV.

## Struktur und Inhalt der zu erstellenden `PLAN.md`

Erstelle die `PLAN.md`-Datei exakt nach der folgenden Struktur:

---

### **BEGINN DES INHALTS FÜR `PLAN.md`**

# AI Legal Ops Implementation Plan

**Last Updated:** [Aktuelles Datum]
**Project Status:** Planning Phase
**Current Phase:** Phase 1 (MVP Core)

# 🔍 Analysis Summary

Fasse die wichtigsten technischen und regulatorischen Anforderungen zusammen.

# Aufgaben nach Priorität

Gruppiere alle Aufgaben nach Priorität (Critical, High, Medium, Low) und Phase.

- `## 🔴 Critical Priority (Phase 1 - MVP Core)`
- `## 🟡 High Priority (Phase 2 - Billing & Multi-Tenancy)`
- `## 🟢 Medium Priority (Phase 3 - Public Launch)`
- `## 🔵 Low Priority (Phase 4 - Optimization)`

# Aufgaben-Formatierung

Jede Aufgabe muss diesem Format folgen:
` - [ ] **CATEGORY-XXX**: Kurze Beschreibung`

**Kategorien:**
- `AI`: Gateway, Provider Adapters, Prompt Management
- `PRIVACY`: PII Shield, Redaction Logic
- `BILLING`: Credit System, Stripe, Usage Tracking
- `API`: FastAPI, Pydantic Models, Auth
- `INFRA`: Docker, Supabase, Redis, CI/CD
- `TEST`: Unit Tests, Integration Tests, Security Tests

# 🎯 Implementation Guidelines

- **Privacy First:** Keine persönlichen Daten (PII) verlassen das System Richtung AI-Provider.
- **Security:** Strikte Tenant-Isolation und API-Key Validierung bei jedem Request.
- **Reliability:** Graceful Handling von AI-Provider Ausfällen.

### **ENDE DES INHALTS FÜR `PLAN.md`**
