# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
