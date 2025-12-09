# =============================================================================
# Multi-Stage Dockerfile for AI Orchestra Gateway
# Optimized for production with minimal image size (<150MB) and security
# INFRA-005: Enhanced Docker optimization with distroless concepts
# =============================================================================

# Build arguments for flexibility
ARG PYTHON_VERSION=3.12
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=0.4.0

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies and compile wheels
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Set environment variables for optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements (production only)
COPY requirements.txt .

# Create production requirements (exclude dev dependencies)
RUN grep -v "^#" requirements.txt | grep -v "pytest" | grep -v "ruff" | grep -v "^$" > requirements.prod.txt \
    && pip install --no-cache-dir --upgrade pip wheel \
    && pip install --no-cache-dir -r requirements.prod.txt \
    && find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -type f -name "*.pyc" -delete \
    && find /opt/venv -type f -name "*.pyo" -delete \
    && find /opt/venv -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -type d -name "test" -exec rm -rf {} + 2>/dev/null || true

# -----------------------------------------------------------------------------
# Stage 2: Production - Minimal runtime image
# -----------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS production

# Labels for image metadata (OCI compliant)
LABEL maintainer="AI Legal Ops Team" \
      org.opencontainers.image.title="AI Orchestra Gateway" \
      org.opencontainers.image.description="Multi-tenant AI Gateway with Privacy Shield" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="AI Legal Ops" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/ai-legal-ops/ai-orchestra-gateway"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    PATH="/opt/venv/bin:$PATH" \
    # Uvicorn optimization
    WEB_CONCURRENCY=4

# Install only runtime dependencies (no gcc/build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y \
    # Remove apt cache
    && rm -rf /var/cache/apt/archives/*

# Create non-root user for security
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/false --no-create-home appuser

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code (only necessary files)
COPY --chown=appuser:appgroup ./app ./app

# Remove test files from production image
RUN rm -rf ./app/tests 2>/dev/null || true

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check with shorter intervals for production
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with optimized settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--workers", "1"]

# -----------------------------------------------------------------------------
# Stage 3: Development - For local development with hot reload
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime and dev dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Install dev dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov ruff

# Copy all source code
COPY . .

EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
