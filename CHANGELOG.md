## [0.3.0] - 2025-12-05

### Added
- **Database:** `apps` table for multi-app support per tenant (3-tier architecture: tenant → app → license)
- **Database:** `usage_logs` table for immutable audit trail of AI API calls
- **Schema:** Modified `licenses` table to include `app_id` foreign key
- **Migration:** `003_create_apps_and_usage_logs.sql` with demo data
- **Testing:** Comprehensive schema tests in `test_db_schema.py` (apps, usage_logs, cascades, immutability)
- **Security:** RLS policies on `usage_logs` prevent UPDATE/DELETE operations

### Changed
- **Architecture:** Migrated from 2-tier (tenant → license) to 3-tier (tenant → app → license)
- **Demo Data:** Existing licenses migrated to new demo app structure
- **Indexes:** Added performance indexes for apps, licenses (by app), and usage_logs analytics

### Technical
- CORS whitelist support via `apps.allowed_origins` array
- Denormalized foreign keys in `usage_logs` for fast analytics
- CASCADE DELETE through entire hierarchy (tenant → app → license → usage_logs)
- 10 demo usage log entries for testing analytics queries

## [0.2.1] - 2025-12-05

### Fixed
- **Database:** Added `is_active` column to `tenants` table in migration `001_create_licenses_table.sql`
- **Code Quality:** Migrated Pydantic models to V2 API (`ConfigDict` instead of `Config`, `model_dump()` instead of `dict()`)
- **Admin API:** Fixed schema inconsistency between database and API models

### Changed
- **Pydantic:** Updated `app/api/admin/tenants.py` and `app/api/admin/licenses.py` to use Pydantic V2 API

### Technical
- Resolved all Pydantic deprecation warnings
- Ensured all 17 admin tests pass cleanly
- Database schema now matches API expectations

## [0.2.0] - 2025-12-05

### Added
- **Admin API:** New endpoints for tenant and license management (`/admin/tenants`, `/admin/licenses`)
- **Security:** Admin authentication via `X-Admin-Key` header
- **Billing:** Secure license key generation (`lic_` + 32 chars)
- **Config:** `ADMIN_API_KEY` setting
- **Testing:** 18 new tests for admin endpoints (CRUD, auth, validation)

### Changed
- **Architecture:** Added admin module structure

## [0.1.9] - 2025-12-04

### Added
- **AI Provider:** Scaleway AI support with 7 LLM models (Llama 3.1, Mistral, Qwen, Deepseek)
- **API:** `provider` parameter to `/v1/generate` endpoint ("anthropic" default, "scaleway" optional)
- **Config:** `SCALEWAY_API_KEY` setting (optional)
- **Testing:** 10 Scaleway provider tests + 3 provider selection tests (100% coverage)

### Changed
- **Endpoint:** `/v1/generate` now supports dynamic provider selection
- **Architecture:** Multi-provider support via runtime selection

## [0.1.8] - 2025-12-04

### Added
- **Billing:** Atomic credit deduction using Supabase RPC function
- **Database:** Migration `002_create_billing_functions.sql` with `deduct_credits` RPC
- **Backend:** `BillingService` class for credit management (100% test coverage)
- **Testing:** 6 billing unit tests + updated 12 generate endpoint tests

### Changed
- **API:** `/v1/generate` endpoint now deducts credits atomically after successful generation
- **Flow:** Credits deducted AFTER AI generation (user-friendly: pay on success only)

### Security
- Atomic transactions prevent race conditions in billing
- Row-level locking (`FOR UPDATE`) ensures data consistency

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2025-12-04

### Added
- **Privacy:** Global `PrivacyLogFilter` to automatically sanitize PII from all log messages
- **Core:** Logging configuration in `app/main.py` with privacy filter applied to root logger
- **Testing:** 8 unit tests for logging filter (100% coverage)

### Changed
- **Logging:** All application logs now automatically sanitized before output

## [0.1.6] - 2025-12-03

### Added
- Implemented API key validation middleware via FastAPI dependency injection
- Created SQL migration for licenses and tenants tables with demo data
- Added 12 comprehensive security tests (100% coverage on security.py)

### Changed  
- Updated /v1/generate endpoint to use X-License-Key header (via Depends)
- Removed license_key field from GenerateRequest body
- Updated 12 generate endpoint tests for header-based authentication
- Changed authentication method from request body to HTTP header

### Security
- Real-time license validation against Supabase on every request
- Error codes: 401 (missing header), 403 (invalid/inactive/expired), 402 (no credits)
- Automatic credit balance checking
- FastAPI dependency injection for selective route protection

### Technical
- Using Supabase client for direct database queries
- Header validation via FastAPI Header() parameter
- Test mocking via app.dependency_overrides for clean testing
- SQL migration includes triggers for updated_at timestamps
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
