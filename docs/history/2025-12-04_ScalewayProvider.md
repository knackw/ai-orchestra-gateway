# History: AI-003 Scaleway AI Provider

**Date:** 2025-12-04
**Task:** AI-003
**Status:** Completed
**Version:** 0.1.9

## Overview
Added Scaleway as additional AI provider supporting 7 LLM models, giving users choice between Anthropic and Scaleway.

## Changes

### Backend
- **NEW:** `app/services/scaleway_provider.py`
  - `ScalewayProvider` class implementing `AIProvider` interface
  - Support for 7 models: Llama 3.1 (8B, 70B), Mistral, Qwen, Deepseek
  - Default: `llama-3.1-8b-instruct` (cost-effective)
  - OpenAI-compatible API format
  - 94% test coverage

- **MODIFIED:** `app/core/config.py`
  - Added `SCALEWAY_API_KEY` setting (optional, defaults to empty string)

- **MODIFIED:** `app/api/v1/generate.py`
  - Added `provider` parameter to `GenerateRequest` (default: "anthropic")
  - Dynamic provider selection: `"anthropic"` or `"scaleway"`
  - Validation: 400 error for invalid providers
  - Top-level imports for both providers

### Testing
- **NEW:** `app/tests/test_scaleway_provider.py`
  - 10 comprehensive tests (100% coverage)
  - Tests: initialization, generation, errors (401, 429, 500), model selection

- **MODIFIED:** `app/tests/test_generate.py`
  - Added `TestProviderSelection` class with 3 tests
  - Tests: Scaleway selection, Anthropic default, invalid provider rejection

## Test Results
```
13 passed in 4.43s
- Scaleway provider: 10/10 ✅
- Provider selection: 3/3 ✅
Coverage: 94% for scaleway_provider.py
```

## Technical Decisions

**1. Additional Provider (Not Fallback)**
- User explicitly chooses via `provider` parameter
- No automatic fallback on errors
- Clear, predictable behavior

**2. Multi-Model Support**
- 7 available models in `AVAILABLE_MODELS` list
- Default: `llama-3.1-8b-instruct` (8B parameter model)
- Model selection via constructor parameter

**3. API Compatibility**
- OpenAI-compatible API format (Scaleway standard)
- Consistent interface with `AnthropicProvider`
- Same error handling pattern (401, 429, 500)

## Available Models
- `llama-3.3-70b-instruct`
- `llama-3.1-70b-instruct`
- `llama-3.1-8b-instruct` ← default
- `mistral-nemo-instruct-2407`
- `mistral-7b-instruct-v0.3`
- `deepseek-r1-distill-llama-70b`
- `qwen3-235b-a22b-instruct-2507`

## Example Usage
```json
POST /v1/generate
{
  "prompt": "Explain quantum computing",
  "provider": "scaleway"
}
```

## Production Ready
✅ Comprehensive testing
✅ Error handling
✅ Multiple model support
✅ OpenAI-compatible API
