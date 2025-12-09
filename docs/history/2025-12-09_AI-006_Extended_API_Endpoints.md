# AI-006: Extended API Endpoints (Vision, Audio, Embeddings, GDPR)

**Date:** 2025-12-09
**Version:** 0.8.7
**Status:** Complete

---

## Overview

This update adds four new API endpoint categories to the AI Orchestra Gateway, extending the platform's capabilities beyond text generation to include multi-modal AI features and GDPR compliance endpoints.

---

## New API Endpoints

### 1. Vision API (`app/api/v1/vision.py`)

**Endpoint:** `POST /api/v1/vision`

**Features:**
- Image analysis with AI vision models
- EU-only provider enforcement with automatic fallback
- PII detection in prompts before sending to AI
- Credit-based billing per request

**Supported Providers:**
- Scaleway (EU-compliant): `pixtral-12b-2409`, `mistral-small-3.2-24b-instruct-2506`

**Request Model:**
```python
class VisionRequest(BaseModel):
    prompt: str
    image_url: str
    provider: str = "scaleway"
    model: Optional[str] = None
    eu_only: bool = False
```

**Response Model:**
```python
class VisionResponse(BaseModel):
    content: str
    tokens_used: int
    credits_deducted: int
    pii_detected: bool
    provider_used: str
    model_used: str
    eu_compliant: bool
    fallback_applied: bool
```

---

### 2. Audio Transcription API (`app/api/v1/audio.py`)

**Endpoint:** `POST /api/v1/audio/transcribe`

**Features:**
- Audio-to-text transcription
- Multiple audio format support (wav, mp3, m4a, etc.)
- Maximum file size: 25MB
- EU-compliant provider selection

**Supported Providers:**
- Scaleway: `whisper-large-v3`, `voxtral-small-24b-2507`

**Response Model:**
```python
class TranscriptionResponse(BaseModel):
    text: str
    tokens_used: int
    credits_deducted: int
    provider_used: str
    model_used: str
    eu_compliant: bool
```

---

### 3. Embeddings API (`app/api/v1/embeddings.py`)

**Endpoint:** `POST /api/v1/embeddings`

**Features:**
- Text embedding generation for semantic search
- Batch processing (multiple texts per request)
- EU-compliant provider enforcement

**Supported Providers:**
- Scaleway: `qwen3-embedding-8b`, `bge-multilingual-gemma2`

**Request Model:**
```python
class EmbeddingsRequest(BaseModel):
    input: List[str]
    model: str = "qwen3-embedding-8b"
    provider: str = "scaleway"
    eu_only: bool = False
```

**Response Model:**
```python
class EmbeddingsResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingObject]
    model: str
    credits_deducted: int
    provider_used: str
    eu_compliant: bool
```

---

### 4. GDPR Compliance API (`app/api/v1/gdpr.py`)

**Endpoints:**
- `GET /api/v1/gdpr/dpa` - Get DPA information
- `POST /api/v1/gdpr/dpa/accept` - Accept DPA
- `GET /api/v1/gdpr/processing-info/{provider}` - Get processing info per provider
- `GET /api/v1/gdpr/compliance-status` - Get compliance status for all providers

**Features:**
- Data Processing Agreement (DPA) management
- Provider transparency (data residency, sub-processors, security measures)
- EU-compliant provider identification
- GDPR Article 13/14 compliance

**Core Module:** `app/core/gdpr.py`
- `GDPRComplianceChecker` class
- `DataProcessingInfo` dataclass
- `DataResidency` enum (EU, US, GLOBAL)
- Provider validation and fallback logic

---

## Test Coverage

### New Test Files:
- `app/tests/test_vision_api.py` - 9 tests
- `app/tests/test_audio_api.py` - 7 tests
- `app/tests/test_embeddings_api.py` - 7 tests
- `app/tests/test_gdpr_endpoints.py` - 15 tests

**Test Fixes Applied:**
- Updated `LicenseInfo` parameters (`credits` -> `credits_remaining`)
- Removed deprecated `has_expired` parameter
- Fixed rate limiter tests to work without real Request objects
- Tests now directly test endpoint logic with mocked dependencies

**Total Tests:** 919 passed, 14 skipped, 0 failed

---

## Files Modified/Created

### New Files:
- `app/api/v1/vision.py`
- `app/api/v1/audio.py`
- `app/api/v1/embeddings.py`
- `app/api/v1/gdpr.py`
- `app/core/gdpr.py`
- `app/tests/test_vision_api.py`
- `app/tests/test_audio_api.py`
- `app/tests/test_embeddings_api.py`
- `app/tests/test_gdpr_endpoints.py`

### Modified Files:
- `app/main.py` - Added new routers
- `app/services/scaleway_provider.py` - Added vision, audio, embeddings methods

---

## Security Considerations

1. **PII Protection:** All vision prompts are sanitized via DataPrivacyShield before AI processing
2. **EU Data Residency:** `eu_only` parameter enforces EU-compliant providers
3. **Rate Limiting:** All endpoints protected with rate limits (configurable per endpoint)
4. **License Validation:** All endpoints require valid X-License-Key header
5. **Credit Deduction:** Atomic credit deduction prevents billing issues

---

## Next Steps

- Phase 6: Frontend Implementation (Next.js)
- 20 Frontend tasks pending implementation
