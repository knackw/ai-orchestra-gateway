# TECHNISCHES KONZEPT & PROJEKTPLAN: AI Legal Ops (SaaS Proxy & Gateway)

**Version:** 2.0 (Enterprise / White-Label Ready)  
**Typ:** API Gateway / Middleware  
**Stack:** Python 3.11, FastAPI, Supabase, Docker, Redis  
**Ziel:** Hochsichere Middleware für AI-Orchestrierung, Billing und Privacy-Enforcement.

## 1. Architektur & White-Label Design

Wir erweitern die Architektur um Multi-Tenancy. Das System bedient nicht mehr nur dein Plugin, sondern kann Mandanten (andere SaaS-Anbieter) verwalten.

### Erweiterte Ordnerstruktur

```
ai-legal-proxy/
├── app/
│   ├── __init__.py
│   ├── main.py             # Entry Point
│   ├── core/
│   │   ├── config.py       # Pydantic Settings
│   │   └── security.py     # API Key & Tenant Validation
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints.py # Routen
│   │       └── deps.py      # Dependencies
│   ├── services/
│   │   ├── ai_gateway.py   # Router (Scaleway/Anthropic)
│   │   ├── privacy.py      # PII Shield
│   │   └── billing.py      # Credit Deductor
│   └── tests/              # Pytest Suite
│       ├── conftest.py
│       └── test_api.py
├── .github/
│   └── workflows/
│       └── ci-cd.yaml      # GitHub Actions
├── pyproject.toml          # Config für Ruff/Pytest
├── Dockerfile              # Prod Container
└── docker-compose.yml      # Local Dev Environment
```

## 2. Datenbank Schema (Multi-Tenant Ready)

Um das System an andere Anbieter zu vermarkten, führen wir tenants (die Anbieter) und apps ein.

### SQL Snippet (Supabase):

```sql
-- 1. Tenants (z.B. Du, oder eine Partner-Agentur)
create table public.tenants (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  api_secret text not null unique, -- Master Key für den Tenant
  is_active boolean default true
);

-- 2. Apps (Das konkrete Projekt des Tenants, z.B. "AGB Generator Plugin")
create table public.apps (
  id uuid default gen_random_uuid() primary key,
  tenant_id uuid references public.tenants(id),
  app_name text,
  allowed_origins text[] -- CORS Whitelist
);

-- 3. End-User Lizenzen (gebunden an eine App)
create table public.licenses (
  id uuid default gen_random_uuid() primary key,
  app_id uuid references public.apps(id), -- WICHTIG: Lizenz gehört zu einer App
  license_key text not null unique,
  plan_type text default 'pro',
  credits_remaining int default 0
);
```

## 3. Quality Assurance & Linting (Die "Kirsche")

Wir nutzen Ruff (ersetzt Flake8/Black/Isort und ist 100x schneller) für statische Code-Analyse. Das garantiert, dass dein Code auch für Dritte auditierbar ist.

### 3.1. pyproject.toml Konfiguration

Diese Datei steuert alle QA-Tools zentral.

```toml
[tool.ruff]
line-length = 120
select = ["E", "F", "I", "UP", "B"] # Error, Pyflakes, Import Sort, PyUpgrade, Bugbear
target-version = "py311"

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "--cov=app --cov-report=term-missing"
testpaths = ["app/tests"]
```

### 3.2. Automatisierte Tests (tests/test_api.py)

Wir testen nicht gegen die echte KI (teuer), sondern mocken die Factory.

```python
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_generate_agb_no_auth():
    response = client.post("/v1/generate/agb", json={"context_data": "test"})
    assert response.status_code == 403

@patch("app.services.ai_gateway.call_provider") # Mocken der KI
def test_generate_agb_success(mock_ai):
    # Simuliere KI Antwort
    mock_ai.return_value = ("Generierte AGB...", 100)
    
    # Simuliere validen Key (Mock DB Dependency muss injected werden)
    headers = {"X-License-Key": "test_valid_key"}
    payload = {
        "shop_url": "https://test.shop",
        "context_data": "Wir verkaufen Socken.",
        "request_type": "standard"
    }
    
    response = client.post("/v1/generate/agb", headers=headers, json=payload)
    assert response.status_code == 200
    assert "content" in response.json()
```

## 4. CI/CD Pipeline (GitHub Actions)

Jeder Push löst diese Pipeline aus. Nur wenn Tests + Linting grün sind, wird deployt.

**Datei:** `.github/workflows/ci-cd.yaml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ "main" ]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install Dependencies
        run: |
          pip install ruff pytest pytest-cov httpx
          pip install -r requirements.txt
          
      - name: Linting (Ruff)
        run: ruff check .
        
      - name: Run Tests
        run: pytest

  deploy:
    needs: quality-check # Nur deployen wenn Tests ok
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build & Push Docker
        # Hier würdest du z.B. die Scaleway/DockerHub Action nutzen
        run: echo "Building Docker Image and Pushing to Registry..."
      - name: Deploy to Server
        # Via SSH Key den 'docker pull' auf dem IONOS Server triggern
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/ai-proxy
            docker pull myrepo/ai-proxy:latest
            docker-compose up -d --force-recreate
```

## 5. Deployment (Production mit Docker Compose)

Für die Produktion nutzen wir docker-compose, da es einfacher zu warten ist als nackte docker run Befehle, besonders wenn wir später Redis für Caching hinzufügen.

**Datei:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: ai_legal_proxy
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    # Optional: Redis für Rate Limiting
    # depends_on:
    #   - redis
    
  # Optional: Redis Service
  # redis:
  #   image: redis:alpine
```

## 6. Code-Beispiele für Core Services

### 6.1. Privacy Shield mit Logging-Filter

Wir stellen sicher, dass PII (Personally Identifiable Information) niemals im Log landet.

```python
# app/services/privacy.py
import re
import logging

logger = logging.getLogger("privacy_shield")

class DataPrivacyShield:
    PATTERNS = {
        "email": r'[\w\.-]+@[\w\.-]+\.\w+',
        "phone": r'(\+49|0)[1-9][0-9 \-\.]+',
        "iban": r'[A-Z]{2}\d{2}[ ]\d{4}[ ]\d{4}[ ]\d{4}[ ]\d{4}[ ]\d{0,2}'
    }

    @classmethod
    def sanitize(cls, text: str) -> tuple[str, bool]:
        """
        Returns: (sanitized_text, was_modified)
        """
        if not text: return "", False
        
        modified = False
        clean_text = text
        
        for name, pattern in cls.PATTERNS.items():
            if re.search(pattern, clean_text):
                clean_text = re.sub(pattern, f'<{name.upper()}_REMOVED>', clean_text)
                modified = True
                
        if modified:
            logger.info("PII detected and removed from request.")
            
        return clean_text, modified
```

### 6.2. Billing Service (Atomare Transaktionen)

Um Race Conditions zu vermeiden (User sendet 10 Requests gleichzeitig), nutzen wir DB-Level Dekremente.

```python
# app/services/billing.py
async def deduct_credits(supabase: Client, license_id: str, cost: int):
    # RPC (Remote Procedure Call) in Supabase ist sicherer für atomare Updates
    # Alternativ direkter SQL call, aber RPC ist best practice
    try:
        response = supabase.rpc(
            "deduct_credits", 
            {"p_license_id": license_id, "p_amount": cost}
        ).execute()
        
        if response.data == False:
            raise ValueError("Insufficient balance")
            
    except Exception as e:
        # Fallback Logging
        raise e
```

(Hinweis: Dazu gehört eine SQL Function in Supabase:)

```sql
create or replace function deduct_credits(p_license_id uuid, p_amount int)
returns boolean as $$
begin
  update public.licenses
  set credits_remaining = credits_remaining - p_amount
  where id = p_license_id and credits_remaining >= p_amount;
  
  return found; -- Returns true if update was successful
end;
$$ language plpgsql;
```
