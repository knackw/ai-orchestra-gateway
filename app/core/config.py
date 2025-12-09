from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        """Parse comma-separated CORS origins from environment variable."""
        if isinstance(v, str):
            if not v.strip():
                return []
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if v else []

settings = Settings()
