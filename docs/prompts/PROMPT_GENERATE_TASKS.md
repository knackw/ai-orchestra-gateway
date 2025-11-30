# Anweisung zur Erstellung der `TASKS.md` für AI Legal Ops

## Deine Rolle und Aufgabe

Du bist ein technischer Projektleiter für AI-Infrastruktur. Deine Aufgabe ist es, basierend auf dem `PROJEKTPLAN.md` und der `PLAN.md` einen detaillierten Umsetzungsplan (`TASKS.md`) zu erstellen.

## Input-Dokumente

- `docs/PROJEKTPLAN.md`: Master-Projektplan
- `docs/PLAN.md`: Strategische Planung (falls vorhanden)

## Struktur der `TASKS.md`

Erstelle die Datei `docs/TASKS.md` mit folgender Struktur:

---

### **BEGINN DES INHALTS FÜR `TASKS.md`**

# Implementation Tasks: AI Legal Ops

## Executive Summary
Kurzer Überblick über den aktuellen Status und das nächste große Ziel (z.B. MVP Gateway Launch).

## Thematische Aufgabenlisten

Erstelle für jeden Hauptbereich einen Abschnitt mit Checkbox-Aufgaben.

### 1. Infrastructure & Setup (Phase 1)
- [ ] **INFRA-001**: Init Python/FastAPI Project Structure
- [ ] **INFRA-002**: Setup Supabase Project (Frankfurt) & RLS
- [ ] **INFRA-003**: Configure Docker & CI/CD

### 2. Core: AI Gateway & Privacy (Phase 1)
- [ ] **AI-001**: Implement Provider Interface (Anthropic/Scaleway)
- [ ] **PRIVACY-001**: Implement DataPrivacyShield (Regex Patterns)
- [ ] **API-001**: Create /generate Endpoint with Auth

### 3. Billing & Multi-Tenancy (Phase 2)
- [ ] **BILLING-001**: Implement Credit Deduction RPC
- [ ] **BILLING-002**: Setup Tenant API Key Management
- [ ] **BILLING-003**: Integrate Stripe Webhooks

### 4. Compliance & Security (Phase 3)
- [ ] **SEC-001**: Audit Logging for Privacy Events
- [ ] **SEC-002**: Rate Limiting (Redis)
- [ ] **LEGAL-001**: AVV Workflow

## Timeline & Milestones

- **Phase 1 (Woche 1-2):** Core Gateway & Privacy Shield
- **Phase 2 (Woche 3-4):** Multi-Tenancy & Billing
- **Phase 3 (Woche 5):** Hardening & Launch

## Success Metrics

- 100% PII-Redaktion in Test-Suite
- < 200ms Overhead durch Gateway-Logik
- 100% Testabdeckung für Billing-Logik

### **ENDE DES INHALTS FÜR `TASKS.md`**
