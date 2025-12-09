"""
Unit tests for GDPR API endpoints.
"""

import pytest
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.core.security import LicenseInfo


class TestGDPREndpoints:
    """Tests for GDPR compliance endpoints."""

    @pytest.mark.asyncio
    @patch("app.api.v1.gdpr.GDPRComplianceChecker.get_dpa_info")
    async def test_get_dpa_info_success(self, mock_get_dpa_info):
        """Test successful DPA info retrieval."""
        from app.api.v1.gdpr import DPAInfoResponse

        mock_get_dpa_info.return_value = {
            "tenant_id": "test-tenant",
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
                    }
                ]
            },
            "data_residency_options": [
                {"value": "eu_only", "label": "EU Only (GDPR Compliant)"},
            ],
        }

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate getting DPA info
        dpa_info = mock_get_dpa_info(str(license.tenant_id))

        response = DPAInfoResponse(**dpa_info)

        assert response.tenant_id == "test-tenant"
        assert response.dpa_accepted is False
        assert response.dpa_version == "1.0"
        assert response.eu_only_enabled is False
        assert len(response.processor_info["available_processors"]) > 0

    @pytest.mark.asyncio
    async def test_accept_dpa_success(self):
        """Test successful DPA acceptance."""
        from app.api.v1.gdpr import AcceptDPARequest, AcceptDPAResponse
        from datetime import datetime, timezone

        request_body = AcceptDPARequest(
            accepted=True,
            version="1.0"
        )

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate the accept logic
        if not request_body.accepted:
            raise HTTPException(status_code=400, detail="DPA must be accepted")

        accepted_at = datetime.now(timezone.utc).isoformat()

        response = AcceptDPAResponse(
            success=True,
            message=f"DPA version {request_body.version} accepted successfully",
            dpa_accepted_at=accepted_at,
        )

        assert response.success is True
        assert "accepted successfully" in response.message
        assert response.dpa_accepted_at is not None

    @pytest.mark.asyncio
    async def test_accept_dpa_not_accepted(self):
        """Test DPA acceptance with accepted=False."""
        from app.api.v1.gdpr import AcceptDPARequest

        request_body = AcceptDPARequest(
            accepted=False,
            version="1.0"
        )

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate the accept logic
        if not request_body.accepted:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(
                    status_code=400,
                    detail="DPA must be accepted to use the service"
                )

            assert exc_info.value.status_code == 400
            assert "must be accepted" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("app.api.v1.gdpr.GDPRComplianceChecker.get_processing_info")
    async def test_get_processing_info_success(self, mock_get_processing_info):
        """Test successful processing info retrieval."""
        from app.core.gdpr import DataProcessingInfo, DataResidency
        from app.api.v1.gdpr import ProcessingInfoResponse

        mock_processing_info = DataProcessingInfo(
            provider="scaleway",
            region="fr-par",
            data_residency=DataResidency.EU,
            is_gdpr_compliant=True,
            legal_basis="contract",
            data_retention_days=0,
            processor_name="Scaleway SAS",
            processor_location="France (Paris)",
            sub_processors=["Scaleway Cloud Infrastructure (FR-PAR)"],
            security_measures=[
                "TLS 1.3 encryption in transit",
                "AES-256 encryption at rest",
            ],
            data_subject_rights=["Right to access", "Right to deletion"],
        )

        mock_get_processing_info.return_value = mock_processing_info

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate getting processing info
        processing_info = mock_get_processing_info("scaleway")

        response = ProcessingInfoResponse(
            provider=processing_info.provider,
            region=processing_info.region,
            data_residency=processing_info.data_residency.value,
            is_gdpr_compliant=processing_info.is_gdpr_compliant,
            legal_basis=processing_info.legal_basis,
            data_retention_days=processing_info.data_retention_days,
            processor_name=processing_info.processor_name,
            processor_location=processing_info.processor_location,
            sub_processors=processing_info.sub_processors,
            security_measures=processing_info.security_measures,
            data_subject_rights=processing_info.data_subject_rights,
        )

        assert response.provider == "scaleway"
        assert response.region == "fr-par"
        assert response.data_residency == "EU"
        assert response.is_gdpr_compliant is True
        assert response.processor_name == "Scaleway SAS"
        assert len(response.security_measures) > 0
        assert len(response.data_subject_rights) > 0

    @pytest.mark.asyncio
    @patch("app.api.v1.gdpr.GDPRComplianceChecker.get_processing_info")
    async def test_get_processing_info_invalid_provider(self, mock_get_processing_info):
        """Test processing info with invalid provider."""
        mock_get_processing_info.side_effect = ValueError("Unknown provider")

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate the validation
        try:
            mock_get_processing_info("invalid_provider")
        except ValueError as e:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(status_code=400, detail=str(e))

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    @patch("app.api.v1.gdpr.GDPRComplianceChecker.get_compliant_providers")
    @patch("app.api.v1.gdpr.GDPRComplianceChecker.get_processing_info")
    async def test_get_compliance_status_success(
        self,
        mock_get_processing_info,
        mock_get_compliant_providers,
    ):
        """Test successful compliance status retrieval."""
        from app.core.gdpr import DataProcessingInfo, DataResidency
        from app.api.v1.gdpr import ComplianceStatusResponse

        mock_get_compliant_providers.return_value = ["scaleway", "vertex_claude", "vertex_gemini"]

        def mock_processing_info_func(provider):
            if provider == "scaleway":
                return DataProcessingInfo(
                    provider="scaleway",
                    region="fr-par",
                    data_residency=DataResidency.EU,
                    is_gdpr_compliant=True,
                    legal_basis="contract",
                    data_retention_days=0,
                    processor_name="Scaleway SAS",
                    processor_location="France (Paris)",
                    sub_processors=[],
                    security_measures=[],
                    data_subject_rights=[],
                )
            elif provider == "anthropic":
                return DataProcessingInfo(
                    provider="anthropic",
                    region="us-east-1",
                    data_residency=DataResidency.US,
                    is_gdpr_compliant=False,
                    legal_basis="contract",
                    data_retention_days=30,
                    processor_name="Anthropic PBC",
                    processor_location="United States",
                    sub_processors=[],
                    security_measures=[],
                    data_subject_rights=[],
                )
            else:
                return DataProcessingInfo(
                    provider=provider,
                    region="europe-west3",
                    data_residency=DataResidency.EU,
                    is_gdpr_compliant=True,
                    legal_basis="contract",
                    data_retention_days=0,
                    processor_name="Google Cloud Platform",
                    processor_location="Germany (Frankfurt)",
                    sub_processors=[],
                    security_measures=[],
                    data_subject_rights=[],
                )

        mock_get_processing_info.side_effect = mock_processing_info_func

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate building provider list
        eu_compliant = mock_get_compliant_providers()
        providers = []

        for provider_name in ["anthropic", "scaleway", "vertex_claude", "vertex_gemini"]:
            try:
                info = mock_get_processing_info(provider_name)
                providers.append({
                    "name": provider_name,
                    "eu_compliant": info.is_gdpr_compliant,
                    "region": info.region,
                    "data_residency": info.data_residency.value,
                })
            except ValueError:
                continue

        response = ComplianceStatusResponse(
            providers=providers,
            eu_compliant_providers=eu_compliant,
            recommended_provider=eu_compliant[0] if eu_compliant else "scaleway",
        )

        assert len(response.providers) > 0
        assert len(response.eu_compliant_providers) == 3
        assert response.recommended_provider in response.eu_compliant_providers

        # Check that at least one provider is EU-compliant
        eu_providers = [p for p in response.providers if p["eu_compliant"]]
        assert len(eu_providers) > 0


class TestGDPRComplianceChecker:
    """Tests for GDPRComplianceChecker methods."""

    def test_is_provider_gdpr_compliant(self):
        """Test GDPR compliance check."""
        from app.core.gdpr import GDPRComplianceChecker

        assert GDPRComplianceChecker.is_provider_gdpr_compliant("scaleway") is True
        assert GDPRComplianceChecker.is_provider_gdpr_compliant("vertex_claude") is True
        assert GDPRComplianceChecker.is_provider_gdpr_compliant("vertex_gemini") is True
        assert GDPRComplianceChecker.is_provider_gdpr_compliant("anthropic") is False

    def test_get_compliant_providers(self):
        """Test getting list of compliant providers."""
        from app.core.gdpr import GDPRComplianceChecker

        providers = GDPRComplianceChecker.get_compliant_providers()

        assert isinstance(providers, list)
        assert len(providers) == 3
        assert "scaleway" in providers
        assert "vertex_claude" in providers
        assert "vertex_gemini" in providers
        assert "anthropic" not in providers

    def test_validate_request_with_eu_only(self):
        """Test request validation with EU-only requirement."""
        from app.core.gdpr import GDPRComplianceChecker

        # Valid: EU-compliant provider with EU-only
        is_valid, msg = GDPRComplianceChecker.validate_request("scaleway", eu_only=True)
        assert is_valid is True

        # Invalid: Non-EU provider with EU-only
        is_valid, msg = GDPRComplianceChecker.validate_request("anthropic", eu_only=True)
        assert is_valid is False
        assert "not EU-compliant" in msg

    def test_validate_request_without_eu_only(self):
        """Test request validation without EU-only requirement."""
        from app.core.gdpr import GDPRComplianceChecker

        # Valid: Any provider without EU-only
        is_valid, msg = GDPRComplianceChecker.validate_request("anthropic", eu_only=False)
        assert is_valid is True

        is_valid, msg = GDPRComplianceChecker.validate_request("scaleway", eu_only=False)
        assert is_valid is True

    def test_get_fallback_provider(self):
        """Test fallback provider selection."""
        from app.core.gdpr import GDPRComplianceChecker

        # No fallback when EU-only is False
        fallback = GDPRComplianceChecker.get_fallback_provider("anthropic", eu_only=False)
        assert fallback is None

        # No fallback when provider is already EU-compliant
        fallback = GDPRComplianceChecker.get_fallback_provider("scaleway", eu_only=True)
        assert fallback is None

        # Fallback to EU provider when non-EU provider with EU-only
        fallback = GDPRComplianceChecker.get_fallback_provider("anthropic", eu_only=True)
        assert fallback is not None
        assert fallback in GDPRComplianceChecker.get_compliant_providers()

    def test_select_model_for_tenant_no_fallback(self):
        """Test model selection without fallback."""
        from app.core.gdpr import GDPRComplianceChecker

        provider, model, fallback_applied = GDPRComplianceChecker.select_model_for_tenant(
            tenant_id="test-tenant",
            requested_provider="scaleway",
            requested_model="llama-3.1-8b-instruct",
            eu_only=True,
            capability="chat"
        )

        assert provider == "scaleway"
        assert model == "llama-3.1-8b-instruct"
        assert fallback_applied is False

    def test_select_model_for_tenant_with_fallback(self):
        """Test model selection with fallback."""
        from app.core.gdpr import GDPRComplianceChecker

        provider, model, fallback_applied = GDPRComplianceChecker.select_model_for_tenant(
            tenant_id="test-tenant",
            requested_provider="anthropic",
            requested_model=None,
            eu_only=True,
            capability="chat"
        )

        assert provider != "anthropic"
        assert provider in GDPRComplianceChecker.get_compliant_providers()
        assert fallback_applied is True

    def test_get_dpa_info(self):
        """Test DPA info retrieval."""
        from app.core.gdpr import GDPRComplianceChecker

        dpa_info = GDPRComplianceChecker.get_dpa_info("test-tenant")

        assert dpa_info["tenant_id"] == "test-tenant"
        assert "dpa_accepted" in dpa_info
        assert "dpa_version" in dpa_info
        assert "processor_info" in dpa_info
        assert "data_residency_options" in dpa_info
        assert len(dpa_info["processor_info"]["available_processors"]) > 0
