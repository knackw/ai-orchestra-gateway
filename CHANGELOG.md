# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2025-12-03

### Added
- Implemented `/v1/generate` POST endpoint for AI text generation
- Created Pydantic request model (`GenerateRequest`) with validation
- Created Pydantic response model (`GenerateResponse`) with structured output
- Integrated DataPrivacyShield for automatic prompt sanitization
- Integrated AnthropicProvider for AI response generation
- Credit calculation system (1:1 with tokens for MVP)
- Comprehensive error handling (validation errors, AI provider errors)
- Added `pii_detected` field in response for transparency
- Created 12 comprehensive endpoint tests (100% coverage on generate.py)

### Changed
- Updated FastAPI app version to 0.1.5 in main.py
- Included `/v1/generate` router with `/v1` prefix

### Technical
- Request validation: prompt (1-10000 chars), license_key (non-empty)
- Response format: `{content, tokens_used, credits_deducted, pii_detected}`
- Processing flow: Validate → Sanitize → Generate → Calculate → Return
- Error responses: 422 (validation), 500 (AI errors)
- Logging: Sanitized logging (no PII in logs)

### Notes
- License key accepted but not yet validated (will be in API-002)
- Credit deduction calculation only (DB update will be in BILLING-001)

## [0.1.4] - 2025-12-03

### Added
- Implemented DataPrivacyShield for PII detection and sanitization
- Created regex patterns for email, phone (German), and IBAN detection
- Auto-sanitization with placeholders (`<EMAIL_REMOVED>`, `<PHONE_REMOVED>`, `<IBAN_REMOVED>`)
- Return tuple `(sanitized_text, pii_found: bool)` for easy integration
- Logging of PII detections (without logging actual PII)
- `has_pii()` convenience method for checking without sanitizing
- Created 35 comprehensive tests with 93% coverage

### Technical
- Email pattern: Comprehensive regex matching 99% of valid emails
- Phone pattern: German formats (+49, 0049, 0xxx with flexible separators)
- IBAN pattern: German IBAN (DE + 20 digits)
- Processing order: Email → IBAN → Phone (avoids pattern conflicts)
- Fail-open error handling (returns original text on exception)

## [0.1.3] - 2025-12-02

### Added
- Implemented Anthropic provider for Claude API integration
- Created `AnthropicProvider` class implementing `AIProvider` interface
- Integrated with Claude 3.5 Sonnet via httpx async client
- Added x-api-key authentication for Anthropic API
- Comprehensive request/response handling
- Token counting from API usage data (input + output tokens)
- Robust error handling (401, 429, 500, network errors)
- Created 18 comprehensive tests with 97% coverage

### Technical
- Using httpx.AsyncClient for async HTTP requests
- Model: claude-3-5-sonnet-20241022
- Default max_tokens: 1024
- Proper error wrapping in ProviderAPIError

## [0.1.2] - 2025-12-02

### Added
- Implemented abstract AI provider interface (`AIProvider` base class)
- Created provider registry pattern for managing multiple AI providers
- Added custom exceptions hierarchy (`ProviderError`, `ProviderNotFoundError`, `ProviderAPIError`, `ProviderConfigError`)
- Implemented `AIGateway` facade for provider access
- Created comprehensive test suite with 25 tests for gateway functionality
- Added global registry singleton pattern

### Technical
- Using Python ABC module for abstract base class
- Type hints compatible with Python 3.8+ (using `Tuple`, `List` from typing)
- 97% test coverage on new gateway module

## [0.1.1] - 2025-12-02

### Added
- Implemented comprehensive `/health` endpoint with database connectivity check
- Added uptime metrics tracking (app start time based)
- Created `app/core/health.py` with structured health check service
- Added Pydantic models for health response validation
- Created comprehensive test suite for health check (11 tests, 100% coverage)

### Changed
- Enhanced `/health` endpoint from simple status to comprehensive system check
- Updated application version from 0.1.0 to 0.1.1

## [2.0.4] - 2025-11-30

### Added
- Created production `Dockerfile` with multi-stage build and non-root user.
- Added `docker-compose.yml` for local development and deployment.
- Configured GitHub Actions CI/CD workflow (`.github/workflows/ci-cd.yaml`) for automated linting, testing, and building.
- Added `.dockerignore` to optimize build context.

## [2.0.3] - 2025-11-30

### Added
- Implemented Supabase client in `app/core/database.py`.
- Added `scripts/test_db_connection.py` for connection verification.
- Configured `.env` with production Supabase credentials.
- Updated `requirements.txt` to include `httpx[http2]` for Supabase client compatibility.

## [2.0.2] - 2025-11-30

### Added
- Initialized Python/FastAPI project structure (`app/`, `services/`, `api/`, `core/`, `tests/`).
- Configured `pyproject.toml` with Ruff linting and Pytest settings.
- Added `requirements.txt` with core dependencies (FastAPI, Pydantic, Supabase).
- Created `.pre-commit-config.yaml` for automated code quality checks.
- Implemented basic `main.py` and health check endpoint.

## [2.0.1] - 2025-11-30

### Added
- Created `.env.example` with configuration templates for Supabase, AI Providers, and Billing.
- Updated task tracking in `docs/TASKS.md`.

## [2.0.0] - 2025-11-29

### Initial Release
- Initial project structure and documentation.
- Defined project plan and implementation tasks.
