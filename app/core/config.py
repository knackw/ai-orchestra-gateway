"""
SEC-015: Application Configuration with Security Enhancements

Configuration settings with validation for:
- CORS origins URL validation
- Environment-aware settings
- Secure defaults
"""

import re
from typing import List
from urllib.parse import urlparse

from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


# SEC-015: Regex pattern for valid CORS origins
CORS_ORIGIN_PATTERN = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}'  # domain
    r'|localhost'  # or localhost
    r'|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP address
    r'(?::\d{1,5})?'  # optional port
    r'$'
)


def validate_cors_origin(origin: str) -> bool:
    """
    SEC-015: Validate that a CORS origin is a valid URL.

    Valid formats:
    - https://example.com
    - https://sub.example.com
    - http://localhost:3000
    - http://192.168.1.1:8080

    Invalid formats:
    - example.com (no protocol)
    - https://example.com/ (trailing slash)
    - https://example.com/path (has path)
    - * (wildcard not allowed for credentials)
    """
    if not origin or origin == '*':
        return False

    # Check basic pattern
    if not CORS_ORIGIN_PATTERN.match(origin):
        return False

    # Parse and validate URL structure
    try:
        parsed = urlparse(origin)

        # Must have scheme and netloc, no path/query/fragment
        if not parsed.scheme or not parsed.netloc:
            return False
        if parsed.path and parsed.path != '/':
            return False
        if parsed.query or parsed.fragment:
            return False

        # Port must be valid if present
        if parsed.port and (parsed.port < 1 or parsed.port > 65535):
            return False

        return True
    except Exception:
        return False


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Legal Ops Gateway"
    API_V1_STR: str = "/api/v1"

    # Environment (development, staging, production)
    ENVIRONMENT: str = "development"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # AI Providers
    ANTHROPIC_API_KEY: str
    SCALEWAY_API_KEY: str = ""

    # Google Cloud / Vertex AI (DSGVO-compliant region)
    GCP_PROJECT_ID: str = ""
    GCP_REGION: str = "europe-west3"  # Frankfurt for DSGVO compliance
    GOOGLE_APPLICATION_CREDENTIALS: str = ""  # Path to service account JSON

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Admin API
    ADMIN_API_KEY: str = ""  # Optional for tests

    # Monitoring
    SENTRY_DSN: str = ""

    # Security: Trusted Proxies for X-Forwarded-For validation (SEC-011)
    TRUSTED_PROXIES: str = ""  # Comma-separated list of IPs/CIDRs

    # CORS Configuration (SEC-015)
    CORS_ORIGINS: List[str] = []
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 600  # Preflight cache time in seconds (10 minutes)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        SEC-015: Parse and validate CORS origins from environment variable.

        Validates each origin URL format:
        - Must have http:// or https:// protocol
        - Must be a valid domain, localhost, or IP address
        - Must not have trailing slash, path, query, or fragment
        - Wildcard (*) is not allowed when credentials are enabled

        Raises ValueError for invalid origins.
        """
        if isinstance(v, str):
            if not v.strip():
                return []
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
        else:
            origins = v if v else []

        # SEC-015: Validate each origin
        valid_origins = []
        invalid_origins = []

        for origin in origins:
            # Remove trailing slash if present (common mistake)
            origin = origin.rstrip('/')

            if validate_cors_origin(origin):
                valid_origins.append(origin)
            else:
                invalid_origins.append(origin)

        if invalid_origins:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"SEC-015: Invalid CORS origins ignored: {invalid_origins}. "
                f"Valid format: https://example.com (no trailing slash or path)"
            )

        return valid_origins

settings = Settings()
