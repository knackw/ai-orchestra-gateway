# GDPR Compliance - Usage Guide

## Overview

This guide explains how to use the GDPR/DSGVO compliance features in the AI Legal Ops Gateway.

## Quick Start

### Enforce EU-Only Data Processing

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    headers={"X-License-Key": "your-license-key"},
    json={
        "prompt": "Write a professional email",
        "provider": "anthropic",  # Will auto-fallback to EU provider
        "eu_only": True  # Enforce EU data processing
    }
)

data = response.json()
print(f"Provider used: {data['provider_used']}")  # vertex_claude
print(f"EU compliant: {data['eu_compliant']}")    # True
print(f"Fallback applied: {data['fallback_applied']}")  # True
```

### List All Data Processors

```python
import requests

response = requests.get("http://localhost:8000/api/v1/processors")
processors = response.json()

for processor in processors:
    print(f"Provider: {processor['provider']}")
    print(f"Region: {processor['region']}")
    print(f"EU Compliant: {processor['is_gdpr_compliant']}")
    print(f"Data Retention: {processor['data_retention_days']} days")
    print(f"Security: {', '.join(processor['security_measures'][:2])}")
    print("---")
```

### Get Legal Documents

```python
import requests

# Privacy Policy (German)
response = requests.get("http://localhost:8000/api/v1/datenschutz?language=de")
privacy_policy = response.json()
print(privacy_policy['content'])

# Data Processing Agreement with processor metadata
response = requests.get("http://localhost:8000/api/v1/avv?language=de")
avv = response.json()
print(f"Processors: {len(avv['processors'])}")
for processor in avv['processors']:
    print(f"- {processor['provider']}: {processor['processor_location']}")
```

## EU-Compliant Providers

### Scaleway (France)
```json
{
  "provider": "scaleway",
  "region": "fr-par",
  "data_residency": "EU",
  "is_gdpr_compliant": true,
  "data_retention_days": 0,
  "processor_location": "France (Paris)"
}
```

### Vertex AI Claude (Germany)
```json
{
  "provider": "vertex_claude",
  "region": "europe-west3",
  "data_residency": "EU",
  "is_gdpr_compliant": true,
  "data_retention_days": 0,
  "processor_location": "Germany (Frankfurt)"
}
```

### Vertex AI Gemini (Germany)
```json
{
  "provider": "vertex_gemini",
  "region": "europe-west3",
  "data_residency": "EU",
  "is_gdpr_compliant": true,
  "data_retention_days": 0,
  "processor_location": "Germany (Frankfurt)"
}
```

## Programmatic Usage

### Check Provider Compliance

```python
from app.core.gdpr import GDPRComplianceChecker

# Check if provider is EU-compliant
is_compliant = GDPRComplianceChecker.is_provider_gdpr_compliant("scaleway")
print(f"Scaleway is EU-compliant: {is_compliant}")  # True

# Get all EU-compliant providers
eu_providers = GDPRComplianceChecker.get_compliant_providers()
print(f"EU providers: {eu_providers}")
# ['vertex_claude', 'vertex_gemini', 'scaleway']
```

### Validate Requests

```python
from app.core.gdpr import GDPRComplianceChecker

# Validate provider against eu_only constraint
is_valid, message = GDPRComplianceChecker.validate_request(
    provider="anthropic",
    eu_only=True
)
print(f"Valid: {is_valid}")  # False
print(f"Message: {message}")  # "Provider 'anthropic' is not EU-compliant..."
```

### Get Processing Information

```python
from app.core.gdpr import GDPRComplianceChecker

# Get complete GDPR transparency data
info = GDPRComplianceChecker.get_processing_info("vertex_claude")

print(f"Provider: {info.provider}")
print(f"Region: {info.region}")
print(f"Data Residency: {info.data_residency.value}")
print(f"GDPR Compliant: {info.is_gdpr_compliant}")
print(f"Legal Basis: {info.legal_basis}")
print(f"Data Retention: {info.data_retention_days} days")
print(f"Processor: {info.processor_name}")
print(f"Location: {info.processor_location}")
print(f"Sub-Processors: {', '.join(info.sub_processors)}")
print(f"Security Measures:")
for measure in info.security_measures:
    print(f"  - {measure}")
print(f"Data Subject Rights:")
for right in info.data_subject_rights:
    print(f"  - {right}")
```

### Automatic Fallback

```python
from app.core.gdpr import GDPRComplianceChecker

# Get fallback provider for non-EU provider
fallback = GDPRComplianceChecker.get_fallback_provider(
    requested_provider="anthropic",
    eu_only=True
)
print(f"Fallback provider: {fallback}")  # "vertex_claude"

# No fallback needed for EU provider
fallback = GDPRComplianceChecker.get_fallback_provider(
    requested_provider="scaleway",
    eu_only=True
)
print(f"Fallback provider: {fallback}")  # None
```

## API Endpoints

### Legal Documents

| Endpoint | Description | Languages |
|----------|-------------|-----------|
| `GET /api/v1/agb` | Terms of Service (AGB) | de, en |
| `GET /api/v1/datenschutz` | Privacy Policy | de, en |
| `GET /api/v1/avv` | Data Processing Agreement | de, en |
| `GET /api/v1/impressum` | Legal Notice | de, en |
| `GET /api/v1/processors` | List all processors | - |

### Generate with GDPR

```bash
POST /api/v1/generate
```

**Request:**
```json
{
  "prompt": "Your prompt here",
  "provider": "anthropic",  # Optional, will fallback if eu_only=true
  "model": null,  # Optional
  "eu_only": true  # Enforce EU data processing
}
```

**Response:**
```json
{
  "content": "Generated response...",
  "tokens_used": 127,
  "credits_deducted": 127,
  "pii_detected": false,
  "provider_used": "vertex_claude",  # Actual provider (may differ from requested)
  "eu_compliant": true,  # Whether provider is EU-compliant
  "fallback_applied": true  # Whether automatic fallback was used
}
```

## Best Practices

### 1. Always Use eu_only for EU Customers

```python
# For EU customers
response = requests.post(
    "http://localhost:8000/api/v1/generate",
    headers={"X-License-Key": customer_license},
    json={
        "prompt": user_input,
        "eu_only": True  # Always enforce for EU customers
    }
)
```

### 2. Check Fallback Status

```python
data = response.json()
if data['fallback_applied']:
    print(f"Switched to EU provider: {data['provider_used']}")
```

### 3. Log GDPR Decisions

```python
import logging

logger.info(
    f"GDPR: provider={data['provider_used']}, "
    f"eu_compliant={data['eu_compliant']}, "
    f"fallback={data['fallback_applied']}"
)
```

### 4. Provide Legal Documents

```python
# Serve legal documents to customers
async def get_privacy_policy():
    response = requests.get(
        "http://localhost:8000/api/v1/datenschutz?language=de"
    )
    return response.json()
```

### 5. Display Processor Information

```python
# Show customers which AI providers you use
response = requests.get("http://localhost:8000/api/v1/processors")
processors = response.json()

eu_processors = [p for p in processors if p['is_gdpr_compliant']]
print(f"We use {len(eu_processors)} EU-compliant AI providers:")
for processor in eu_processors:
    print(f"- {processor['provider']} ({processor['processor_location']})")
```

## Compliance Checklist

- [ ] Set `eu_only=true` for all EU customer requests
- [ ] Display privacy policy (`/api/v1/datenschutz`)
- [ ] Provide Data Processing Agreement (`/api/v1/avv`)
- [ ] Show processor transparency (`/api/v1/processors`)
- [ ] Log GDPR compliance decisions
- [ ] Monitor fallback usage
- [ ] Provide legal notice (`/api/v1/impressum`)
- [ ] Include Terms of Service (`/api/v1/agb`)

## Data Subject Rights

### Right to Access (Art. 15 GDPR)

Customers can request their data via:
```python
# Implement data export for customer
GET /api/v1/settings/export-data
```

### Right to Deletion (Art. 17 GDPR)

```python
# Implement account deletion
DELETE /api/v1/settings/account
```

### Right to Data Portability (Art. 20 GDPR)

```python
# Export customer data in machine-readable format
GET /api/v1/settings/export-data?format=json
```

## Audit Trail

All GDPR decisions are automatically logged:

```
INFO - GDPR Compliance Check: provider=vertex_claude, eu_only=True,
       eu_compliant=True, region=europe-west3, data_residency=EU,
       fallback_used=False
```

Monitor logs for:
- Provider selection
- Fallback decisions
- EU-only enforcement
- Data residency

## Support

For GDPR-related questions:
- Review legal documents: `/api/v1/datenschutz`, `/api/v1/avv`
- Check processor list: `/api/v1/processors`
- Contact: datenschutz@example.com

## Version

- **Version:** 0.7.0
- **Date:** 2025-12-08
- **Status:** Production Ready
