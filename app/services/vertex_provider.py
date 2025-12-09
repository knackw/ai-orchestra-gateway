"""
Google Vertex AI provider base implementation.

Provides shared configuration and utilities for Vertex AI providers
including Claude (via Anthropic on Vertex) and Gemini.

DSGVO Compliance: Uses europe-west3 (Frankfurt) region for EU data residency.
"""

import logging
import os
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.core.config import settings
from app.services.ai_gateway import AIProvider, ProviderAPIError, ProviderConfigError

logger = logging.getLogger(__name__)


class VertexRegion(Enum):
    """
    Google Cloud regions for Vertex AI.

    For DSGVO compliance, use EU regions only.
    """
    # EU Regions (DSGVO compliant)
    EUROPE_WEST3 = "europe-west3"  # Frankfurt, Germany (recommended)
    EUROPE_WEST1 = "europe-west1"  # Belgium
    EUROPE_WEST4 = "europe-west4"  # Netherlands
    EUROPE_WEST9 = "europe-west9"  # Paris, France

    # US Regions (not DSGVO compliant without SCCs)
    US_CENTRAL1 = "us-central1"
    US_EAST4 = "us-east4"

    @classmethod
    def get_eu_regions(cls) -> list["VertexRegion"]:
        """Get all EU-compliant regions."""
        return [
            cls.EUROPE_WEST3,
            cls.EUROPE_WEST1,
            cls.EUROPE_WEST4,
            cls.EUROPE_WEST9,
        ]

    @classmethod
    def is_eu_region(cls, region: str) -> bool:
        """Check if a region is EU-compliant."""
        eu_region_values = [r.value for r in cls.get_eu_regions()]
        return region in eu_region_values


class DataResidency(Enum):
    """Data residency classification for compliance."""
    EU = "eu"
    US = "us"
    GLOBAL = "global"


@dataclass
class VertexModel:
    """Vertex AI model metadata."""
    id: str
    name: str
    provider: str  # "anthropic" or "google"
    context_window: int
    max_output_tokens: int
    supports_vision: bool = False
    supports_streaming: bool = True
    temperature_range: tuple[float, float] = (0.0, 1.0)
    description: str = ""


# Claude models available on Vertex AI
VERTEX_CLAUDE_MODELS = {
    "claude-3-5-sonnet-v2@20241022": VertexModel(
        id="claude-3-5-sonnet-v2@20241022",
        name="Claude 3.5 Sonnet v2",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=8192,
        supports_vision=True,
        temperature_range=(0.0, 1.0),
        description="Latest Claude 3.5 Sonnet with improved performance"
    ),
    "claude-3-5-sonnet@20240620": VertexModel(
        id="claude-3-5-sonnet@20240620",
        name="Claude 3.5 Sonnet",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=8192,
        supports_vision=True,
        temperature_range=(0.0, 1.0),
        description="Claude 3.5 Sonnet - balanced performance and speed"
    ),
    "claude-3-opus@20240229": VertexModel(
        id="claude-3-opus@20240229",
        name="Claude 3 Opus",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        supports_vision=True,
        temperature_range=(0.0, 1.0),
        description="Most powerful Claude model for complex tasks"
    ),
    "claude-3-sonnet@20240229": VertexModel(
        id="claude-3-sonnet@20240229",
        name="Claude 3 Sonnet",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        supports_vision=True,
        temperature_range=(0.0, 1.0),
        description="Claude 3 Sonnet - balanced model"
    ),
    "claude-3-haiku@20240307": VertexModel(
        id="claude-3-haiku@20240307",
        name="Claude 3 Haiku",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        supports_vision=True,
        temperature_range=(0.0, 1.0),
        description="Fastest Claude model for quick responses"
    ),
}

# Gemini models available on Vertex AI
VERTEX_GEMINI_MODELS = {
    "gemini-2.0-flash-001": VertexModel(
        id="gemini-2.0-flash-001",
        name="Gemini 2.0 Flash",
        provider="google",
        context_window=1000000,  # 1M tokens
        max_output_tokens=8192,
        supports_vision=True,
        temperature_range=(0.0, 2.0),
        description="Fast and efficient Gemini model"
    ),
    "gemini-1.5-pro-002": VertexModel(
        id="gemini-1.5-pro-002",
        name="Gemini 1.5 Pro",
        provider="google",
        context_window=2000000,  # 2M tokens
        max_output_tokens=8192,
        supports_vision=True,
        temperature_range=(0.0, 2.0),
        description="Most capable Gemini model with 2M context"
    ),
    "gemini-1.5-flash-002": VertexModel(
        id="gemini-1.5-flash-002",
        name="Gemini 1.5 Flash",
        provider="google",
        context_window=1000000,  # 1M tokens
        max_output_tokens=8192,
        supports_vision=True,
        temperature_range=(0.0, 2.0),
        description="Fast Gemini model for quick tasks"
    ),
}

# Combined model catalog
VERTEX_MODELS = {**VERTEX_CLAUDE_MODELS, **VERTEX_GEMINI_MODELS}


def get_vertex_model(model_id: str) -> Optional[VertexModel]:
    """Get model metadata by ID."""
    return VERTEX_MODELS.get(model_id)


def list_vertex_models(provider: Optional[str] = None) -> list[str]:
    """
    List available Vertex AI model IDs.

    Args:
        provider: Filter by provider ("anthropic" or "google")

    Returns:
        List of model IDs
    """
    if provider:
        return [
            model_id for model_id, model in VERTEX_MODELS.items()
            if model.provider == provider
        ]
    return list(VERTEX_MODELS.keys())


class VertexAIProvider(AIProvider):
    """
    Base class for Google Vertex AI providers.

    Provides shared configuration and GCP authentication handling
    for both Claude (via Anthropic on Vertex) and Gemini providers.

    DSGVO Compliance:
    - Default region: europe-west3 (Frankfurt)
    - All data processed within EU
    - No transfer to US servers
    """

    DEFAULT_REGION = VertexRegion.EUROPE_WEST3.value

    def __init__(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ):
        """
        Initialize Vertex AI provider.

        Args:
            project_id: GCP project ID (defaults to GCP_PROJECT_ID env var)
            region: GCP region (defaults to europe-west3 for DSGVO compliance)
            credentials_path: Path to service account JSON (optional)

        Raises:
            ProviderConfigError: If required configuration is missing
        """
        self.project_id = project_id or getattr(settings, 'GCP_PROJECT_ID', None) or os.getenv('GCP_PROJECT_ID')
        self.region = region or getattr(settings, 'GCP_REGION', None) or os.getenv('GCP_REGION', self.DEFAULT_REGION)
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        # Validate configuration
        if not self.project_id:
            raise ProviderConfigError(
                "GCP_PROJECT_ID must be set in environment or config"
            )

        # Warn if using non-EU region
        if not VertexRegion.is_eu_region(self.region):
            logger.warning(
                f"Using non-EU region '{self.region}'. "
                f"For DSGVO compliance, use one of: "
                f"{[r.value for r in VertexRegion.get_eu_regions()]}"
            )
        else:
            logger.info(
                f"Vertex AI initialized with EU region: {self.region} (DSGVO compliant)"
            )

        # Set credentials path if provided
        if self.credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path

    @property
    def data_residency(self) -> DataResidency:
        """Get data residency classification based on region."""
        if VertexRegion.is_eu_region(self.region):
            return DataResidency.EU
        return DataResidency.US

    @property
    def is_dsgvo_compliant(self) -> bool:
        """Check if provider is configured for DSGVO compliance."""
        return self.data_residency == DataResidency.EU

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name identifier."""
        pass

    @abstractmethod
    async def generate(self, prompt: str) -> tuple[str, int]:
        """Generate response - must be implemented by subclasses."""
        pass

    def get_model_info(self, model_id: str) -> Optional[VertexModel]:
        """Get model metadata."""
        return get_vertex_model(model_id)

    @classmethod
    def list_available_models(cls, provider: Optional[str] = None) -> list[str]:
        """List available model IDs."""
        return list_vertex_models(provider)
