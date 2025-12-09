"""
GDPR/DSGVO Compliance Module.

Ensures all AI requests comply with EU data protection regulations.
Provides data residency validation, provider compliance checking,
and data processing transparency.

Version: 0.6.1 (GDPR-001)
"""
from enum import Enum
from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class DataResidency(Enum):
    """Data residency classification for AI providers."""

    EU = "EU"
    US = "US"
    GLOBAL = "GLOBAL"


class GDPRRegion(Enum):
    """GDPR-compliant regions for data processing."""

    EUROPE_WEST3 = "europe-west3"  # Frankfurt, Germany
    EUROPE_WEST1 = "europe-west1"  # St. Ghislain, Belgium
    EUROPE_WEST4 = "europe-west4"  # Eemshaven, Netherlands
    FR_PAR = "fr-par"  # Paris, France (Scaleway)


class LegalBasis(Enum):
    """Legal basis for data processing under GDPR Article 6."""

    CONSENT = "consent"  # Article 6(1)(a)
    CONTRACT = "contract"  # Article 6(1)(b)
    LEGAL_OBLIGATION = "legal_obligation"  # Article 6(1)(c)
    VITAL_INTERESTS = "vital_interests"  # Article 6(1)(d)
    PUBLIC_INTEREST = "public_interest"  # Article 6(1)(e)
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Article 6(1)(f)


@dataclass
class DataProcessingInfo:
    """
    Data Processing Information for GDPR transparency.

    Provides complete information about how data is processed
    by an AI provider, required for GDPR compliance.
    """

    provider: str
    region: str
    data_residency: DataResidency
    is_gdpr_compliant: bool
    legal_basis: str
    data_retention_days: int
    processor_name: str
    processor_location: str
    sub_processors: list[str]
    security_measures: list[str]
    data_subject_rights: list[str]


class GDPRComplianceChecker:
    """Check and enforce GDPR compliance for AI requests."""

    # EU-compliant providers (data processed in EU)
    EU_COMPLIANT_PROVIDERS = ["vertex_claude", "vertex_gemini", "scaleway"]

    # Provider metadata for GDPR transparency
    PROVIDER_METADATA = {
        "anthropic": {
            "region": "us-east-1",
            "data_residency": DataResidency.US,
            "is_gdpr_compliant": False,
            "legal_basis": LegalBasis.CONTRACT.value,
            "data_retention_days": 30,
            "processor_name": "Anthropic PBC",
            "processor_location": "United States",
            "sub_processors": ["Amazon Web Services (AWS US)"],
            "security_measures": [
                "TLS 1.3 encryption in transit",
                "AES-256 encryption at rest",
                "SOC 2 Type II certified",
                "Data deletion after 30 days",
            ],
            "data_subject_rights": [
                "Right to access",
                "Right to deletion",
                "Right to rectification",
            ],
        },
        "scaleway": {
            "region": GDPRRegion.FR_PAR.value,
            "data_residency": DataResidency.EU,
            "is_gdpr_compliant": True,
            "legal_basis": LegalBasis.CONTRACT.value,
            "data_retention_days": 0,
            "processor_name": "Scaleway SAS",
            "processor_location": "France (Paris)",
            "sub_processors": ["Scaleway Cloud Infrastructure (FR-PAR)"],
            "security_measures": [
                "TLS 1.3 encryption in transit",
                "AES-256 encryption at rest",
                "ISO 27001 certified",
                "Data stored in France",
                "No data retention policy",
            ],
            "data_subject_rights": [
                "Right to access",
                "Right to deletion",
                "Right to rectification",
                "Right to data portability",
                "Right to object",
            ],
        },
        "vertex_claude": {
            "region": GDPRRegion.EUROPE_WEST3.value,
            "data_residency": DataResidency.EU,
            "is_gdpr_compliant": True,
            "legal_basis": LegalBasis.CONTRACT.value,
            "data_retention_days": 0,
            "processor_name": "Google Cloud Platform",
            "processor_location": "Germany (Frankfurt)",
            "sub_processors": [
                "Google Cloud Platform (europe-west3)",
                "Anthropic PBC (model inference only)",
            ],
            "security_measures": [
                "TLS 1.3 encryption in transit",
                "AES-256 encryption at rest",
                "ISO 27001, ISO 27017, ISO 27018 certified",
                "Data stored in Germany (Frankfurt)",
                "No data retention by Google or Anthropic",
            ],
            "data_subject_rights": [
                "Right to access",
                "Right to deletion",
                "Right to rectification",
                "Right to data portability",
                "Right to object",
                "Right to restrict processing",
            ],
        },
        "vertex_gemini": {
            "region": GDPRRegion.EUROPE_WEST3.value,
            "data_residency": DataResidency.EU,
            "is_gdpr_compliant": True,
            "legal_basis": LegalBasis.CONTRACT.value,
            "data_retention_days": 0,
            "processor_name": "Google Cloud Platform",
            "processor_location": "Germany (Frankfurt)",
            "sub_processors": ["Google Cloud Platform (europe-west3)"],
            "security_measures": [
                "TLS 1.3 encryption in transit",
                "AES-256 encryption at rest",
                "ISO 27001, ISO 27017, ISO 27018 certified",
                "Data stored in Germany (Frankfurt)",
                "No data retention by Google",
            ],
            "data_subject_rights": [
                "Right to access",
                "Right to deletion",
                "Right to rectification",
                "Right to data portability",
                "Right to object",
                "Right to restrict processing",
            ],
        },
    }

    @classmethod
    def is_provider_gdpr_compliant(cls, provider: str) -> bool:
        """
        Check if provider is GDPR compliant.

        Args:
            provider: Provider name

        Returns:
            True if provider processes data in EU, False otherwise
        """
        return provider in cls.EU_COMPLIANT_PROVIDERS

    @classmethod
    def get_compliant_providers(cls) -> list[str]:
        """
        Get list of GDPR-compliant providers.

        Returns:
            List of EU-compliant provider names
        """
        return cls.EU_COMPLIANT_PROVIDERS.copy()

    @classmethod
    def validate_request(
        cls, provider: str, eu_only: bool = False
    ) -> tuple[bool, str]:
        """
        Validate if request meets GDPR requirements.

        Args:
            provider: Provider name to validate
            eu_only: Whether to enforce EU-only data processing

        Returns:
            Tuple of (is_valid, error_message)
            - (True, "OK") if valid
            - (False, error_message) if invalid
        """
        if eu_only and provider not in cls.EU_COMPLIANT_PROVIDERS:
            return (
                False,
                f"Provider '{provider}' is not EU-compliant. "
                f"Use one of: {', '.join(cls.EU_COMPLIANT_PROVIDERS)}",
            )
        return True, "OK"

    @classmethod
    def get_processing_info(cls, provider: str) -> DataProcessingInfo:
        """
        Get data processing information for a provider.

        Provides complete transparency about data processing
        as required by GDPR Article 13/14.

        Args:
            provider: Provider name

        Returns:
            DataProcessingInfo object with complete processing details

        Raises:
            ValueError: If provider is not recognized
        """
        if provider not in cls.PROVIDER_METADATA:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Available: {list(cls.PROVIDER_METADATA.keys())}"
            )

        metadata = cls.PROVIDER_METADATA[provider]

        return DataProcessingInfo(
            provider=provider,
            region=metadata["region"],
            data_residency=metadata["data_residency"],
            is_gdpr_compliant=metadata["is_gdpr_compliant"],
            legal_basis=metadata["legal_basis"],
            data_retention_days=metadata["data_retention_days"],
            processor_name=metadata["processor_name"],
            processor_location=metadata["processor_location"],
            sub_processors=metadata["sub_processors"],
            security_measures=metadata["security_measures"],
            data_subject_rights=metadata["data_subject_rights"],
        )

    @classmethod
    def get_fallback_provider(
        cls, requested_provider: str, eu_only: bool = False
    ) -> Optional[str]:
        """
        Get fallback provider if requested provider is not compliant.

        Args:
            requested_provider: Originally requested provider
            eu_only: Whether EU-only processing is required

        Returns:
            Fallback provider name, or None if no fallback needed
        """
        if not eu_only:
            return None

        if requested_provider in cls.EU_COMPLIANT_PROVIDERS:
            return None

        # Fallback order: Vertex Claude > Scaleway > Vertex Gemini
        fallback_order = ["vertex_claude", "scaleway", "vertex_gemini"]

        logger.warning(
            f"Provider '{requested_provider}' is not EU-compliant. "
            f"Falling back to '{fallback_order[0]}'"
        )

        return fallback_order[0]

    @classmethod
    def log_compliance_info(
        cls, provider: str, eu_only: bool, fallback_used: bool = False
    ) -> None:
        """
        Log GDPR compliance information for audit trail.

        Args:
            provider: Provider being used
            eu_only: Whether EU-only was requested
            fallback_used: Whether fallback provider was used
        """
        try:
            processing_info = cls.get_processing_info(provider)

            logger.info(
                f"GDPR Compliance Check: provider={provider}, "
                f"eu_only={eu_only}, eu_compliant={processing_info.is_gdpr_compliant}, "
                f"region={processing_info.region}, "
                f"data_residency={processing_info.data_residency.value}, "
                f"fallback_used={fallback_used}"
            )
        except ValueError:
            logger.warning(f"No GDPR metadata available for provider: {provider}")

    @classmethod
    def select_model_for_tenant(
        cls,
        tenant_id: str,
        requested_provider: str,
        requested_model: Optional[str],
        eu_only: bool,
        capability: str = "chat",
    ) -> tuple[str, Optional[str], bool]:
        """
        Select appropriate model based on tenant's GDPR requirements.

        This method implements GDPR-003: automatic model selection logic
        based on tenant configuration and EU compliance requirements.

        Args:
            tenant_id: Tenant identifier
            requested_provider: Provider requested by the user
            requested_model: Model requested by the user (optional)
            eu_only: Whether EU-only processing is required
            capability: Required capability (chat, vision, embeddings, etc.)

        Returns:
            Tuple of (provider, model, fallback_applied)
            - provider: Selected provider name
            - model: Selected model name (or None for default)
            - fallback_applied: Whether fallback was applied

        Examples:
            >>> select_model_for_tenant("tenant-1", "anthropic", None, True, "chat")
            ("vertex_claude", "claude-3-5-sonnet-v2@20241022", True)

            >>> select_model_for_tenant("tenant-2", "scaleway", None, False, "chat")
            ("scaleway", None, False)
        """
        fallback_applied = False

        # Check if requested provider is GDPR compliant
        if eu_only and requested_provider not in cls.EU_COMPLIANT_PROVIDERS:
            # Apply fallback to EU-compliant provider
            fallback_provider = cls.get_fallback_provider(requested_provider, eu_only)

            if fallback_provider:
                logger.info(
                    f"GDPR-003: Automatic fallback applied for tenant {tenant_id}: "
                    f"{requested_provider} -> {fallback_provider} (capability: {capability})"
                )
                return fallback_provider, None, True
            else:
                # No fallback available
                logger.error(
                    f"GDPR-003: No EU-compliant fallback available for "
                    f"tenant {tenant_id}, provider {requested_provider}"
                )
                return requested_provider, requested_model, False

        # No fallback needed
        return requested_provider, requested_model, fallback_applied

    @classmethod
    def get_dpa_info(cls, tenant_id: str) -> dict:
        """
        Get Data Processing Agreement information for a tenant.

        This method implements GDPR-002: DPA status retrieval.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Dictionary with DPA information including:
            - dpa_accepted: Whether DPA has been accepted
            - dpa_accepted_at: Timestamp of acceptance (ISO 8601)
            - dpa_version: Version of DPA accepted
            - processor_info: Information about data processors
            - data_residency_options: Available data residency options

        Note:
            In production, this should query the database for tenant-specific DPA status.
            For MVP, we return template information.
        """
        # TODO: Query database for tenant-specific DPA status
        # For now, return template information
        return {
            "tenant_id": tenant_id,
            "dpa_accepted": False,
            "dpa_accepted_at": None,
            "dpa_version": "1.0",
            "eu_only_enabled": False,
            "processor_info": {
                "available_processors": [
                    {
                        "name": "Scaleway SAS",
                        "location": "France (Paris)",
                        "gdpr_compliant": True,
                        "certifications": ["ISO 27001"],
                    },
                    {
                        "name": "Google Cloud Platform",
                        "location": "Germany (Frankfurt)",
                        "gdpr_compliant": True,
                        "certifications": ["ISO 27001", "ISO 27017", "ISO 27018"],
                    },
                    {
                        "name": "Anthropic PBC",
                        "location": "United States",
                        "gdpr_compliant": False,
                        "certifications": ["SOC 2 Type II"],
                    },
                ],
            },
            "data_residency_options": [
                {"value": "eu_only", "label": "EU Only (GDPR Compliant)"},
                {"value": "global", "label": "Global (All Providers)"},
            ],
        }
