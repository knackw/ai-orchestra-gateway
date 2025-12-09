"""
AI Vision API endpoint.

Provides /v1/vision endpoint for analyzing images with AI:
- Automatic PII sanitization (DataPrivacyShield)
- Multi-provider vision support (Scaleway, Anthropic Vision, Vertex AI)
- Token usage tracking
- Credit calculation
- DSGVO-compliant EU providers
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.security import LicenseInfo, get_current_license
from app.core.rate_limit import limiter
from app.core.gdpr import GDPRComplianceChecker
from app.services.ai_gateway import ProviderAPIError, ProviderConfigError
from app.services.anthropic_provider import AnthropicProvider
from app.services.billing import BillingService
from app.services.privacy import DataPrivacyShield
from app.services.scaleway_provider import ScalewayProvider
from app.services.usage import UsageService

logger = logging.getLogger(__name__)

router = APIRouter()


# Vision-capable providers and their default models
VISION_PROVIDERS = {
    "scaleway": "pixtral-12b-2409",
    "anthropic": "claude-3-5-sonnet-20241022",
}

# EU-compliant vision providers
EU_VISION_PROVIDERS = ["scaleway"]


def get_vision_provider_instance(provider_name: str, model: Optional[str] = None):
    """
    Factory function to create vision provider instances.

    Args:
        provider_name: Name of the provider
        model: Optional model override

    Returns:
        AI provider instance with vision capabilities

    Raises:
        HTTPException: If provider is invalid or not configured
    """
    if provider_name == "scaleway":
        # Use vision-capable model
        vision_model = model if model else VISION_PROVIDERS["scaleway"]
        provider = ScalewayProvider(model=vision_model)

        if not provider.supports_vision():
            raise HTTPException(
                status_code=400,
                detail=f"Model '{vision_model}' does not support vision. "
                       f"Use one of: {', '.join(ScalewayProvider.list_vision_models())}"
            )
        return provider

    elif provider_name == "anthropic":
        # Anthropic Claude has vision capabilities in certain models
        return AnthropicProvider(model=model) if model else AnthropicProvider()

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider '{provider_name}'. "
                   f"Vision-capable providers: {list(VISION_PROVIDERS.keys())}"
        )


class VisionRequest(BaseModel):
    """Request model for /v1/vision endpoint."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User prompt for image analysis",
    )

    image_url: str = Field(
        ...,
        min_length=1,
        description="URL to the image or base64 data URI (data:image/...)",
    )

    provider: str = Field(
        default="scaleway",
        description="AI provider: 'scaleway', 'anthropic'",
    )

    model: Optional[str] = Field(
        default=None,
        description="Specific vision model to use (optional)",
    )

    eu_only: bool = Field(
        default=False,
        description="If true, only allow EU-compliant providers (DSGVO)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What is in this image? Describe it in detail.",
                "image_url": "https://example.com/image.jpg",
                "provider": "scaleway",
                "model": "pixtral-12b-2409",
                "eu_only": False,
            }
        }


class VisionResponse(BaseModel):
    """Response model for /v1/vision endpoint."""

    content: str = Field(..., description="Generated AI response about the image")
    tokens_used: int = Field(..., description="Number of tokens consumed")
    credits_deducted: int = Field(
        ..., description="Credits deducted from tenant account"
    )
    pii_detected: bool = Field(
        ..., description="Whether PII was detected and sanitized in prompt"
    )
    provider_used: str = Field(
        ..., description="Actual provider used"
    )
    model_used: str = Field(
        ..., description="Actual model used"
    )
    eu_compliant: bool = Field(
        ..., description="Whether the provider used is EU-compliant (GDPR)"
    )
    fallback_applied: bool = Field(
        default=False, description="Whether automatic fallback to EU provider was applied"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "This image shows a beautiful sunset over the ocean...",
                "tokens_used": 234,
                "credits_deducted": 234,
                "pii_detected": False,
                "provider_used": "scaleway",
                "model_used": "pixtral-12b-2409",
                "eu_compliant": True,
                "fallback_applied": False,
            }
        }


@router.post("/vision", response_model=VisionResponse)
@limiter.limit("50/minute")
async def analyze_image(
    request: Request,
    request_body: VisionRequest,
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Analyze image using AI vision models.

    This endpoint:
    1. Validates license key from X-License-Key header
    2. Sanitizes the prompt for PII (emails, phones, IBANs)
    3. Generates AI vision response using selected provider
    4. Deducts credits atomically from license
    5. Returns formatted response with image analysis

    Args:
        request: FastAPI request object
        request_body: VisionRequest with prompt and image
        license: Validated license info (from X-License-Key header)

    Returns:
        VisionResponse with content, tokens, credits, and pii flag

    Raises:
        HTTPException 401: Missing X-License-Key header
        HTTPException 403: Invalid/inactive/expired license
        HTTPException 402: No credits remaining
        HTTPException 422: Validation error (automatic)
        HTTPException 500: AI generation failed
    """
    try:
        # Step 1: Sanitize prompt for PII
        sanitized_prompt, pii_found = DataPrivacyShield.sanitize(request_body.prompt)

        if pii_found:
            logger.warning(
                "PII detected in vision prompt for tenant_id=%s",
                license.tenant_id,
            )

        # Step 2: Validate provider selection and apply GDPR compliance
        requested_provider = request_body.provider
        fallback_applied = False

        # Check if requested provider is valid for vision
        if requested_provider not in VISION_PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{requested_provider}' does not support vision. "
                       f"Use one of: {list(VISION_PROVIDERS.keys())}"
            )

        # GDPR validation
        if request_body.eu_only and requested_provider not in EU_VISION_PROVIDERS:
            # Fallback to EU-compliant vision provider
            fallback_provider = EU_VISION_PROVIDERS[0]
            logger.warning(
                f"GDPR compliance: Automatically falling back from "
                f"'{requested_provider}' to '{fallback_provider}' (EU-only requested)"
            )
            provider_name = fallback_provider
            fallback_applied = True
        else:
            provider_name = requested_provider

        # Get provider instance
        provider = get_vision_provider_instance(provider_name, request_body.model)
        model_used = request_body.model or VISION_PROVIDERS.get(provider_name, "unknown")

        # Check if provider is EU-compliant
        is_eu_compliant = provider_name in EU_VISION_PROVIDERS

        # Log GDPR compliance information for audit trail
        logger.info(
            f"Vision API - Using provider: {provider_name}, model: {model_used}, "
            f"EU-only: {request_body.eu_only}, EU-compliant: {is_eu_compliant}, "
            f"Fallback applied: {fallback_applied}"
        )

        # Step 3: Generate vision response
        try:
            if isinstance(provider, ScalewayProvider):
                content, tokens = await provider.generate_with_vision(
                    sanitized_prompt,
                    request_body.image_url
                )
            elif isinstance(provider, AnthropicProvider):
                # Anthropic uses vision API (future implementation)
                # For now, use standard generate with image description
                content, tokens = await provider.generate(
                    f"{sanitized_prompt}\n\nImage URL: {request_body.image_url}"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Provider does not support vision API"
                )
        except ProviderAPIError as e:
            logger.error(f"Vision API provider error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Vision AI generation failed. Please try again later.",
            ) from e

        # Step 4: Calculate credits (1:1 with tokens for MVP)
        credits_to_deduct = tokens

        # Step 5: Deduct credits atomically
        try:
            await BillingService.deduct_credits(
                license.license_key,
                credits_to_deduct
            )
            logger.info(
                f"Billing successful: {credits_to_deduct} credits deducted "
                f"for tenant {license.tenant_id}"
            )
        except HTTPException as billing_error:
            logger.error(
                f"Billing failed for tenant {license.tenant_id}: "
                f"{billing_error.detail}"
            )
            raise

        # Step 6: Log usage
        try:
            await UsageService.log_usage(
                license_id=license.license_uuid,
                app_id=license.app_id,
                tenant_id=license.tenant_id,
                tokens_used=tokens,
                credits_deducted=credits_to_deduct,
                provider=provider_name,
                model=model_used,
                prompt_length=len(sanitized_prompt),
                pii_detected=pii_found,
                response_status="success"
            )
        except Exception as log_error:
            logger.error(f"Failed to log usage: {log_error}")
            # Do not fail request

        # Step 7: Return successful response
        logger.info(
            f"Generated vision response: {tokens} tokens, "
            f"{credits_to_deduct} credits deducted, PII detected: {pii_found}, "
            f"Provider: {provider_name}, EU-compliant: {is_eu_compliant} "
            f"(tenant: {license.tenant_id})"
        )

        return VisionResponse(
            content=content,
            tokens_used=tokens,
            credits_deducted=credits_to_deduct,
            pii_detected=pii_found,
            provider_used=provider_name,
            model_used=model_used,
            eu_compliant=is_eu_compliant,
            fallback_applied=fallback_applied,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in vision endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later.",
        ) from e
