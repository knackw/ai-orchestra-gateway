"""
Tests for GDPR/DSGVO compliance features.

Tests:
- GDPR-001: EU Data Residency Configuration
- GDPR-002: Data Processing Agreement
- GDPR-003: Model Selection Logic with EU-only enforcement

Version: 0.6.1
"""
import pytest
from datetime import date
from app.core.gdpr import (
    GDPRComplianceChecker,
    DataResidency,
    GDPRRegion,
    LegalBasis,
    DataProcessingInfo,
)


class TestGDPRComplianceChecker:
    """Test GDPR-001: EU Data Residency Configuration."""

    def test_is_provider_gdpr_compliant_eu_providers(self):
        """Test that EU providers are correctly identified as GDPR-compliant."""
        assert GDPRComplianceChecker.is_provider_gdpr_compliant("scaleway") is True
        assert (
            GDPRComplianceChecker.is_provider_gdpr_compliant("vertex_claude") is True
        )
        assert (
            GDPRComplianceChecker.is_provider_gdpr_compliant("vertex_gemini") is True
        )

    def test_is_provider_gdpr_compliant_non_eu_providers(self):
        """Test that non-EU providers are correctly identified as non-compliant."""
        assert GDPRComplianceChecker.is_provider_gdpr_compliant("anthropic") is False

    def test_get_compliant_providers(self):
        """Test retrieving list of GDPR-compliant providers."""
        compliant = GDPRComplianceChecker.get_compliant_providers()

        assert isinstance(compliant, list)
        assert len(compliant) == 3
        assert "scaleway" in compliant
        assert "vertex_claude" in compliant
        assert "vertex_gemini" in compliant
        assert "anthropic" not in compliant

    def test_validate_request_eu_only_with_eu_provider(self):
        """Test that EU providers pass validation when eu_only=True."""
        is_valid, message = GDPRComplianceChecker.validate_request(
            "scaleway", eu_only=True
        )
        assert is_valid is True
        assert message == "OK"

        is_valid, message = GDPRComplianceChecker.validate_request(
            "vertex_claude", eu_only=True
        )
        assert is_valid is True
        assert message == "OK"

    def test_validate_request_eu_only_with_non_eu_provider(self):
        """Test that non-EU providers fail validation when eu_only=True."""
        is_valid, message = GDPRComplianceChecker.validate_request(
            "anthropic", eu_only=True
        )
        assert is_valid is False
        assert "not EU-compliant" in message
        assert "anthropic" in message

    def test_validate_request_no_eu_only(self):
        """Test that all providers pass validation when eu_only=False."""
        is_valid, message = GDPRComplianceChecker.validate_request(
            "anthropic", eu_only=False
        )
        assert is_valid is True
        assert message == "OK"

        is_valid, message = GDPRComplianceChecker.validate_request(
            "scaleway", eu_only=False
        )
        assert is_valid is True
        assert message == "OK"

    def test_get_processing_info_anthropic(self):
        """Test data processing info for Anthropic (US provider)."""
        info = GDPRComplianceChecker.get_processing_info("anthropic")

        assert isinstance(info, DataProcessingInfo)
        assert info.provider == "anthropic"
        assert info.data_residency == DataResidency.US
        assert info.is_gdpr_compliant is False
        assert info.legal_basis == LegalBasis.CONTRACT.value
        assert info.data_retention_days == 30
        assert info.processor_name == "Anthropic PBC"
        assert info.processor_location == "United States"
        assert len(info.sub_processors) > 0
        assert len(info.security_measures) > 0
        assert len(info.data_subject_rights) > 0

    def test_get_processing_info_scaleway(self):
        """Test data processing info for Scaleway (EU provider)."""
        info = GDPRComplianceChecker.get_processing_info("scaleway")

        assert isinstance(info, DataProcessingInfo)
        assert info.provider == "scaleway"
        assert info.region == GDPRRegion.FR_PAR.value
        assert info.data_residency == DataResidency.EU
        assert info.is_gdpr_compliant is True
        assert info.legal_basis == LegalBasis.CONTRACT.value
        assert info.data_retention_days == 0
        assert info.processor_name == "Scaleway SAS"
        assert info.processor_location == "France (Paris)"
        assert "France" in info.processor_location or "Paris" in info.processor_location
        assert len(info.security_measures) > 0

    def test_get_processing_info_vertex_claude(self):
        """Test data processing info for Vertex AI Claude (EU provider)."""
        info = GDPRComplianceChecker.get_processing_info("vertex_claude")

        assert isinstance(info, DataProcessingInfo)
        assert info.provider == "vertex_claude"
        assert info.region == GDPRRegion.EUROPE_WEST3.value
        assert info.data_residency == DataResidency.EU
        assert info.is_gdpr_compliant is True
        assert info.data_retention_days == 0
        assert "Germany" in info.processor_location or "Frankfurt" in info.processor_location
        assert "ISO 27001" in str(info.security_measures)

    def test_get_processing_info_vertex_gemini(self):
        """Test data processing info for Vertex AI Gemini (EU provider)."""
        info = GDPRComplianceChecker.get_processing_info("vertex_gemini")

        assert isinstance(info, DataProcessingInfo)
        assert info.provider == "vertex_gemini"
        assert info.region == GDPRRegion.EUROPE_WEST3.value
        assert info.data_residency == DataResidency.EU
        assert info.is_gdpr_compliant is True
        assert info.data_retention_days == 0

    def test_get_processing_info_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            GDPRComplianceChecker.get_processing_info("invalid_provider")

        assert "Unknown provider" in str(exc_info.value)
        assert "invalid_provider" in str(exc_info.value)

    def test_get_fallback_provider_eu_only_non_compliant(self):
        """Test that fallback provider is returned for non-EU provider when eu_only=True."""
        fallback = GDPRComplianceChecker.get_fallback_provider(
            "anthropic", eu_only=True
        )

        assert fallback is not None
        assert fallback in ["vertex_claude", "scaleway", "vertex_gemini"]
        # Should prefer vertex_claude
        assert fallback == "vertex_claude"

    def test_get_fallback_provider_eu_only_compliant(self):
        """Test that no fallback is needed for EU provider when eu_only=True."""
        fallback = GDPRComplianceChecker.get_fallback_provider(
            "scaleway", eu_only=True
        )
        assert fallback is None

        fallback = GDPRComplianceChecker.get_fallback_provider(
            "vertex_claude", eu_only=True
        )
        assert fallback is None

    def test_get_fallback_provider_no_eu_only(self):
        """Test that no fallback is needed when eu_only=False."""
        fallback = GDPRComplianceChecker.get_fallback_provider(
            "anthropic", eu_only=False
        )
        assert fallback is None

    def test_log_compliance_info_logs_correctly(self, caplog):
        """Test that compliance info is logged correctly."""
        import logging

        with caplog.at_level(logging.INFO):
            GDPRComplianceChecker.log_compliance_info(
                provider="scaleway", eu_only=True, fallback_used=False
            )

        # Check that log was created
        assert len(caplog.records) > 0

        # Check log content
        log_message = caplog.records[0].message
        assert "GDPR Compliance Check" in log_message
        assert "provider=scaleway" in log_message
        assert "eu_only=True" in log_message
        assert "eu_compliant=True" in log_message
        assert "fallback_used=False" in log_message

    def test_all_eu_providers_have_metadata(self):
        """Test that all EU-compliant providers have metadata defined."""
        for provider in GDPRComplianceChecker.EU_COMPLIANT_PROVIDERS:
            # Should not raise ValueError
            info = GDPRComplianceChecker.get_processing_info(provider)
            assert info.is_gdpr_compliant is True
            assert info.data_residency == DataResidency.EU

    def test_data_residency_enum(self):
        """Test DataResidency enum values."""
        assert DataResidency.EU.value == "EU"
        assert DataResidency.US.value == "US"
        assert DataResidency.GLOBAL.value == "GLOBAL"

    def test_gdpr_region_enum(self):
        """Test GDPRRegion enum values."""
        assert GDPRRegion.EUROPE_WEST3.value == "europe-west3"
        assert GDPRRegion.EUROPE_WEST1.value == "europe-west1"
        assert GDPRRegion.EUROPE_WEST4.value == "europe-west4"
        assert GDPRRegion.FR_PAR.value == "fr-par"

    def test_legal_basis_enum(self):
        """Test LegalBasis enum values."""
        assert LegalBasis.CONSENT.value == "consent"
        assert LegalBasis.CONTRACT.value == "contract"
        assert LegalBasis.LEGAL_OBLIGATION.value == "legal_obligation"
        assert LegalBasis.VITAL_INTERESTS.value == "vital_interests"
        assert LegalBasis.PUBLIC_INTEREST.value == "public_interest"
        assert LegalBasis.LEGITIMATE_INTERESTS.value == "legitimate_interests"

    def test_data_processing_info_all_fields(self):
        """Test that DataProcessingInfo contains all required fields."""
        info = GDPRComplianceChecker.get_processing_info("scaleway")

        # Verify all fields are present and non-empty
        assert info.provider
        assert info.region
        assert isinstance(info.data_residency, DataResidency)
        assert isinstance(info.is_gdpr_compliant, bool)
        assert info.legal_basis
        assert isinstance(info.data_retention_days, int)
        assert info.processor_name
        assert info.processor_location
        assert isinstance(info.sub_processors, list)
        assert isinstance(info.security_measures, list)
        assert isinstance(info.data_subject_rights, list)

    def test_security_measures_include_encryption(self):
        """Test that all providers include encryption in security measures."""
        for provider in ["anthropic", "scaleway", "vertex_claude", "vertex_gemini"]:
            info = GDPRComplianceChecker.get_processing_info(provider)
            security_text = " ".join(info.security_measures).lower()

            assert "tls" in security_text or "encryption" in security_text
            assert "aes" in security_text or "encryption at rest" in security_text

    def test_eu_providers_have_zero_or_low_retention(self):
        """Test that EU providers have appropriate data retention policies."""
        for provider in ["scaleway", "vertex_claude", "vertex_gemini"]:
            info = GDPRComplianceChecker.get_processing_info(provider)
            # EU providers should have 0 retention (no data stored)
            assert info.data_retention_days == 0

    def test_data_subject_rights_comprehensive(self):
        """Test that EU providers support comprehensive data subject rights."""
        for provider in ["scaleway", "vertex_claude", "vertex_gemini"]:
            info = GDPRComplianceChecker.get_processing_info(provider)

            # Should support at least access, deletion, rectification
            rights_text = " ".join(info.data_subject_rights).lower()
            assert "access" in rights_text
            assert "deletion" in rights_text or "erasure" in rights_text
            assert "rectification" in rights_text


class TestLegalDocumentsAPI:
    """Test GDPR-002: Data Processing Agreement and Legal Documents API."""

    @pytest.mark.asyncio
    async def test_get_terms_of_service_german(self):
        """Test AGB endpoint returns German terms."""
        from app.api.v1.legal import get_terms_of_service

        doc = await get_terms_of_service(language="de")

        assert doc.title == "Allgemeine Geschäftsbedingungen"
        assert doc.version == "1.0"
        assert isinstance(doc.effective_date, date)
        assert doc.language == "de"
        assert "Geltungsbereich" in doc.content
        assert "DSGVO" in doc.content or "Datenschutz" in doc.content

    @pytest.mark.asyncio
    async def test_get_terms_of_service_english(self):
        """Test AGB endpoint returns English terms."""
        from app.api.v1.legal import get_terms_of_service

        doc = await get_terms_of_service(language="en")

        assert doc.title == "Terms of Service"
        assert doc.version == "1.0"
        assert doc.language == "en"
        assert "Scope" in doc.content or "Service" in doc.content

    @pytest.mark.asyncio
    async def test_get_privacy_policy_german(self):
        """Test Datenschutz endpoint returns German privacy policy."""
        from app.api.v1.legal import get_privacy_policy

        doc = await get_privacy_policy(language="de")

        assert doc.title == "Datenschutzerklärung"
        assert doc.language == "de"
        assert "Verantwortlicher" in doc.content
        assert "PII-Shield" in doc.content or "personenbezogene Daten" in doc.content
        assert "DSGVO" in doc.content

    @pytest.mark.asyncio
    async def test_get_privacy_policy_english(self):
        """Test Privacy Policy endpoint returns English policy."""
        from app.api.v1.legal import get_privacy_policy

        doc = await get_privacy_policy(language="en")

        assert doc.title == "Privacy Policy"
        assert doc.language == "en"
        assert "Privacy" in doc.content or "Data" in doc.content
        assert "PII Shield" in doc.content or "personal data" in doc.content

    @pytest.mark.asyncio
    async def test_get_data_processing_agreement_german(self):
        """Test AVV endpoint returns German DPA with processor info."""
        from app.api.v1.legal import get_data_processing_agreement

        doc = await get_data_processing_agreement(language="de")

        assert doc.title == "Auftragsverarbeitungsvertrag"
        assert doc.language == "de"
        assert "Art. 28 DSGVO" in doc.content
        assert "Auftragsverarbeiter" in doc.content or "Sub-Auftragsverarbeiter" in doc.content

        # Check processors are included
        assert len(doc.processors) > 0
        assert any(p.provider == "scaleway" for p in doc.processors)
        assert any(p.is_gdpr_compliant for p in doc.processors)

    @pytest.mark.asyncio
    async def test_get_data_processing_agreement_english(self):
        """Test DPA endpoint returns English agreement."""
        from app.api.v1.legal import get_data_processing_agreement

        doc = await get_data_processing_agreement(language="en")

        assert doc.title == "Data Processing Agreement"
        assert doc.language == "en"
        assert "Art. 28 GDPR" in doc.content or "Article 28" in doc.content
        assert len(doc.processors) > 0

    @pytest.mark.asyncio
    async def test_get_legal_notice_german(self):
        """Test Impressum endpoint returns German legal notice."""
        from app.api.v1.legal import get_legal_notice

        doc = await get_legal_notice(language="de")

        assert doc.title == "Impressum"
        assert doc.language == "de"
        assert "§ 5 TMG" in doc.content or "Angaben gemäß" in doc.content

    @pytest.mark.asyncio
    async def test_get_legal_notice_english(self):
        """Test Legal Notice endpoint returns English notice."""
        from app.api.v1.legal import get_legal_notice

        doc = await get_legal_notice(language="en")

        assert doc.title == "Legal Notice"
        assert doc.language == "en"
        assert "Legal" in doc.content

    @pytest.mark.asyncio
    async def test_list_data_processors(self):
        """Test processors endpoint lists all data processors."""
        from app.api.v1.legal import list_data_processors

        processors = await list_data_processors()

        assert len(processors) == 4
        providers = [p.provider for p in processors]

        assert "anthropic" in providers
        assert "scaleway" in providers
        assert "vertex_claude" in providers
        assert "vertex_gemini" in providers

        # Check EU providers are marked as compliant
        for processor in processors:
            if processor.provider in ["scaleway", "vertex_claude", "vertex_gemini"]:
                assert processor.is_gdpr_compliant is True
                assert processor.data_residency == DataResidency.EU
            elif processor.provider == "anthropic":
                assert processor.is_gdpr_compliant is False
                assert processor.data_residency == DataResidency.US

    @pytest.mark.asyncio
    async def test_avv_contains_all_providers(self):
        """Test that AVV document lists all AI providers."""
        from app.api.v1.legal import get_data_processing_agreement

        doc = await get_data_processing_agreement(language="de")

        # Check processors
        provider_names = [p.provider for p in doc.processors]
        assert "anthropic" in provider_names
        assert "scaleway" in provider_names
        assert "vertex_claude" in provider_names
        assert "vertex_gemini" in provider_names

    @pytest.mark.asyncio
    async def test_avv_processor_details_complete(self):
        """Test that AVV processors have complete information."""
        from app.api.v1.legal import get_data_processing_agreement

        doc = await get_data_processing_agreement(language="de")

        for processor in doc.processors:
            # All required fields must be present
            assert processor.provider
            assert processor.region
            assert isinstance(processor.is_gdpr_compliant, bool)
            assert processor.legal_basis
            assert isinstance(processor.data_retention_days, int)
            assert processor.processor_name
            assert processor.processor_location
            assert len(processor.security_measures) > 0
            assert len(processor.data_subject_rights) > 0


class TestGDPRModelSelection:
    """Test GDPR-003: Model Selection Logic with EU-only enforcement."""

    def test_validate_and_fallback_eu_only_anthropic(self):
        """Test automatic fallback from Anthropic to EU provider."""
        # Validate request
        is_valid, error_msg = GDPRComplianceChecker.validate_request(
            "anthropic", eu_only=True
        )
        assert is_valid is False

        # Get fallback
        fallback = GDPRComplianceChecker.get_fallback_provider(
            "anthropic", eu_only=True
        )
        assert fallback == "vertex_claude"  # Should prefer vertex_claude

    def test_validate_and_fallback_eu_only_scaleway(self):
        """Test no fallback needed for Scaleway when eu_only=True."""
        is_valid, error_msg = GDPRComplianceChecker.validate_request(
            "scaleway", eu_only=True
        )
        assert is_valid is True

        fallback = GDPRComplianceChecker.get_fallback_provider(
            "scaleway", eu_only=True
        )
        assert fallback is None

    def test_fallback_order(self):
        """Test that fallback follows correct priority order."""
        # Fallback order should be: vertex_claude > scaleway > vertex_gemini
        fallback = GDPRComplianceChecker.get_fallback_provider(
            "anthropic", eu_only=True
        )
        assert fallback == "vertex_claude"

    def test_logging_compliance_with_fallback(self, caplog):
        """Test that fallback usage is logged."""
        import logging

        with caplog.at_level(logging.WARNING):
            fallback = GDPRComplianceChecker.get_fallback_provider(
                "anthropic", eu_only=True
            )

        # Should log warning about non-compliant provider
        assert any("not EU-compliant" in record.message for record in caplog.records)
        assert any("vertex_claude" in record.message for record in caplog.records)


class TestGDPRIntegration:
    """Integration tests for GDPR features."""

    def test_all_providers_have_complete_metadata(self):
        """Test that all providers in AVAILABLE_PROVIDERS have GDPR metadata."""
        from app.api.v1.generate import AVAILABLE_PROVIDERS

        for provider in AVAILABLE_PROVIDERS.keys():
            # Should not raise ValueError
            info = GDPRComplianceChecker.get_processing_info(provider)
            assert info is not None
            assert info.provider == provider

    def test_eu_providers_consistency(self):
        """Test consistency between EU_PROVIDERS constant and GDPR checker."""
        from app.api.v1.generate import EU_PROVIDERS

        compliant = GDPRComplianceChecker.get_compliant_providers()

        # Should be identical
        assert set(EU_PROVIDERS) == set(compliant)

    def test_gdpr_metadata_quality(self):
        """Test quality of GDPR metadata for all providers."""
        for provider in ["anthropic", "scaleway", "vertex_claude", "vertex_gemini"]:
            info = GDPRComplianceChecker.get_processing_info(provider)

            # Security measures should be comprehensive
            assert len(info.security_measures) >= 3

            # Data subject rights should be specified
            assert len(info.data_subject_rights) >= 3

            # Sub-processors should be listed
            assert len(info.sub_processors) >= 1

            # Legal basis should be valid
            assert info.legal_basis in [basis.value for basis in LegalBasis]
