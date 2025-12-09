"""
GDPR/DSGVO Compliance API endpoints.

Provides endpoints for:
- Data Processing Agreement (DPA) retrieval and acceptance
- Data residency configuration
- GDPR compliance information
"""

import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.security import LicenseInfo, get_current_license
from app.core.rate_limit import limiter
from app.core.gdpr import GDPRComplianceChecker, DataProcessingInfo
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()


class DPAInfoResponse(BaseModel):
    """Response model for DPA information endpoint."""

    tenant_id: str
    dpa_accepted: bool
    dpa_accepted_at: Optional[str]
    dpa_version: str
    eu_only_enabled: bool
    processor_info: dict
    data_residency_options: list[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant-123",
                "dpa_accepted": True,
                "dpa_accepted_at": "2025-01-15T10:30:00Z",
                "dpa_version": "1.0",
                "eu_only_enabled": True,
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
                    {"value": "global", "label": "Global (All Providers)"},
                ],
            }
        }


class AcceptDPARequest(BaseModel):
    """Request model for accepting DPA."""

    accepted: bool = Field(..., description="Whether to accept the DPA")
    version: str = Field(default="1.0", description="DPA version being accepted")


class AcceptDPAResponse(BaseModel):
    """Response model for accepting DPA."""

    success: bool
    message: str
    dpa_accepted_at: str


class ProcessingInfoResponse(BaseModel):
    """Response model for data processing information."""

    provider: str
    region: str
    data_residency: str
    is_gdpr_compliant: bool
    legal_basis: str
    data_retention_days: int
    processor_name: str
    processor_location: str
    sub_processors: list[str]
    security_measures: list[str]
    data_subject_rights: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "scaleway",
                "region": "fr-par",
                "data_residency": "EU",
                "is_gdpr_compliant": True,
                "legal_basis": "contract",
                "data_retention_days": 0,
                "processor_name": "Scaleway SAS",
                "processor_location": "France (Paris)",
                "sub_processors": ["Scaleway Cloud Infrastructure (FR-PAR)"],
                "security_measures": [
                    "TLS 1.3 encryption in transit",
                    "AES-256 encryption at rest",
                    "ISO 27001 certified",
                ],
                "data_subject_rights": [
                    "Right to access",
                    "Right to deletion",
                    "Right to rectification",
                ],
            }
        }


@router.get("/gdpr/dpa", response_model=DPAInfoResponse)
@limiter.limit("20/minute")
async def get_dpa_info(
    request: Request,
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Get Data Processing Agreement information for the authenticated tenant.

    This endpoint implements GDPR-002: DPA status retrieval.

    Returns information about:
    - DPA acceptance status
    - Available data processors
    - Data residency options
    - EU-only configuration

    Args:
        request: FastAPI request object
        license: Validated license info (from X-License-Key header)

    Returns:
        DPAInfoResponse with DPA information

    Raises:
        HTTPException 401: Missing X-License-Key header
        HTTPException 403: Invalid/inactive/expired license
    """
    try:
        # Get DPA information for tenant
        dpa_info = GDPRComplianceChecker.get_dpa_info(str(license.tenant_id))

        logger.info(
            f"Retrieved DPA info for tenant {license.tenant_id}: "
            f"accepted={dpa_info['dpa_accepted']}, eu_only={dpa_info['eu_only_enabled']}"
        )

        return DPAInfoResponse(**dpa_info)

    except Exception as e:
        logger.error(f"Error retrieving DPA info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve DPA information. Please try again later.",
        ) from e


@router.post("/gdpr/dpa/accept", response_model=AcceptDPAResponse)
@limiter.limit("5/minute")
async def accept_dpa(
    request: Request,
    request_body: AcceptDPARequest,
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Accept the Data Processing Agreement for the authenticated tenant.

    This endpoint implements GDPR-002: DPA acceptance.

    Args:
        request: FastAPI request object
        request_body: AcceptDPARequest with acceptance status
        license: Validated license info (from X-License-Key header)

    Returns:
        AcceptDPAResponse with acceptance confirmation

    Raises:
        HTTPException 401: Missing X-License-Key header
        HTTPException 403: Invalid/inactive/expired license
        HTTPException 500: Database error
    """
    try:
        if not request_body.accepted:
            raise HTTPException(
                status_code=400,
                detail="DPA must be accepted to use the service"
            )

        # TODO: Store DPA acceptance in database
        # For MVP, we just log the acceptance
        accepted_at = datetime.now(timezone.utc).isoformat()

        logger.info(
            f"Tenant {license.tenant_id} accepted DPA version {request_body.version} "
            f"at {accepted_at}"
        )

        # In production, update the tenant record in the database:
        # supabase = get_supabase_client(use_service_role=True)
        # supabase.table("tenants").update({
        #     "dpa_accepted": True,
        #     "dpa_accepted_at": accepted_at,
        #     "dpa_version": request_body.version
        # }).eq("id", license.tenant_id).execute()

        return AcceptDPAResponse(
            success=True,
            message=f"DPA version {request_body.version} accepted successfully",
            dpa_accepted_at=accepted_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting DPA: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to accept DPA. Please try again later.",
        ) from e


@router.get("/gdpr/processing-info/{provider}", response_model=ProcessingInfoResponse)
@limiter.limit("20/minute")
async def get_processing_info(
    request: Request,
    provider: str,
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Get detailed data processing information for a specific AI provider.

    This endpoint provides transparency about how data is processed
    by each AI provider, as required by GDPR Articles 13/14.

    Args:
        request: FastAPI request object
        provider: Provider name (anthropic, scaleway, vertex_claude, vertex_gemini)
        license: Validated license info (from X-License-Key header)

    Returns:
        ProcessingInfoResponse with detailed processing information

    Raises:
        HTTPException 400: Invalid provider
        HTTPException 401: Missing X-License-Key header
        HTTPException 403: Invalid/inactive/expired license
    """
    try:
        # Get processing information
        processing_info = GDPRComplianceChecker.get_processing_info(provider)

        logger.info(
            f"Retrieved processing info for provider {provider} "
            f"(tenant: {license.tenant_id})"
        )

        return ProcessingInfoResponse(
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

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.error(f"Error retrieving processing info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve processing information. Please try again later.",
        ) from e


class ComplianceStatusResponse(BaseModel):
    """Response model for compliance status endpoint."""

    providers: list[dict]
    eu_compliant_providers: list[str]
    recommended_provider: str

    class Config:
        json_schema_extra = {
            "example": {
                "providers": [
                    {
                        "name": "scaleway",
                        "eu_compliant": True,
                        "region": "fr-par",
                        "data_residency": "EU",
                    },
                    {
                        "name": "anthropic",
                        "eu_compliant": False,
                        "region": "us-east-1",
                        "data_residency": "US",
                    },
                ],
                "eu_compliant_providers": ["scaleway", "vertex_claude", "vertex_gemini"],
                "recommended_provider": "vertex_claude",
            }
        }


@router.get("/gdpr/compliance-status", response_model=ComplianceStatusResponse)
@limiter.limit("20/minute")
async def get_compliance_status(
    request: Request,
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Get GDPR compliance status for all available AI providers.

    This endpoint helps tenants understand which providers are
    GDPR-compliant and suitable for EU data processing.

    Args:
        request: FastAPI request object
        license: Validated license info (from X-License-Key header)

    Returns:
        ComplianceStatusResponse with compliance status for all providers

    Raises:
        HTTPException 401: Missing X-License-Key header
        HTTPException 403: Invalid/inactive/expired license
    """
    try:
        # Get list of EU-compliant providers
        eu_compliant = GDPRComplianceChecker.get_compliant_providers()

        # Build provider list with compliance info
        providers = []
        for provider_name in ["anthropic", "scaleway", "vertex_claude", "vertex_gemini"]:
            try:
                info = GDPRComplianceChecker.get_processing_info(provider_name)
                providers.append({
                    "name": provider_name,
                    "eu_compliant": info.is_gdpr_compliant,
                    "region": info.region,
                    "data_residency": info.data_residency.value,
                    "processor_location": info.processor_location,
                })
            except ValueError:
                continue

        logger.info(
            f"Retrieved compliance status for tenant {license.tenant_id}"
        )

        return ComplianceStatusResponse(
            providers=providers,
            eu_compliant_providers=eu_compliant,
            recommended_provider=eu_compliant[0] if eu_compliant else "scaleway",
        )

    except Exception as e:
        logger.error(f"Error retrieving compliance status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve compliance status. Please try again later.",
        ) from e
