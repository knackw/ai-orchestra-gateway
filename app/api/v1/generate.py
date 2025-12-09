"""
AI text generation endpoint.

Provides /v1/generate endpoint for generating AI responses with:
- Automatic PII sanitization (DataPrivacyShield)
- AI generation via multiple providers (Anthropic, Scaleway, Vertex AI)
- Token usage tracking
- Credit calculation
- DSGVO-compliant EU providers (Vertex AI, Scaleway)
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


# Available providers and their default models
AVAILABLE_PROVIDERS = {
    "anthropic": "claude-3-5-sonnet-20241022",
    "scaleway": "llama-3.1-8b-instruct",
    "vertex_claude": "claude-3-5-sonnet-v2@20241022",
    "vertex_gemini": "gemini-1.5-flash-002",
}

# EU-compliant providers (DSGVO)
EU_PROVIDERS = ["scaleway", "vertex_claude", "vertex_gemini"]


def get_provider_instance(provider_name: str, model: Optional[str] = None):
    """
    Factory function to create provider instances.

    Args:
        provider_name: Name of the provider
        model: Optional model override

    Returns:
        AI provider instance

    Raises:
        HTTPException: If provider is invalid or not configured
    """
    if provider_name == "anthropic":
        return AnthropicProvider(model=model) if model else AnthropicProvider()

    elif provider_name == "scaleway":
        return ScalewayProvider(model=model) if model else ScalewayProvider()

    elif provider_name == "vertex_claude":
        try:
            from app.services.vertex_claude_provider import VertexClaudeProvider
            return VertexClaudeProvider(model=model) if model else VertexClaudeProvider()
        except ProviderConfigError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Vertex AI Claude not configured: {str(e)}"
            )

    elif provider_name == "vertex_gemini":
        try:
            from app.services.vertex_gemini_provider import VertexGeminiProvider
            return VertexGeminiProvider(model=model) if model else VertexGeminiProvider()
        except ProviderConfigError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Vertex AI Gemini not configured: {str(e)}"
            )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider '{provider_name}'. Available: {list(AVAILABLE_PROVIDERS.keys())}"
        )


class GenerateRequest(BaseModel):
    """Request model for /v1/generate endpoint."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User prompt for AI generation",
    )

    provider: str = Field(
        default="anthropic",
        description="AI provider: 'anthropic', 'scaleway', 'vertex_claude', 'vertex_gemini'",
    )

    model: Optional[str] = Field(
        default=None,
        description="Specific model to use (optional, uses provider default if not specified)",
    )

    eu_only: bool = Field(
        default=False,
        description="If true, only allow EU-compliant providers (DSGVO)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a professional email to my colleague",
                "provider": "anthropic",
                "model": None,
                "eu_only": False,
            }
        }


class GenerateResponse(BaseModel):
    """Response model for /v1/generate endpoint."""

    content: str = Field(..., description="Generated AI response")
    tokens_used: int = Field(..., description="Number of tokens consumed")
    credits_deducted: int = Field(
        ..., description="Credits deducted from tenant account"
    )
    pii_detected: bool = Field(
        ..., description="Whether PII was detected and sanitized in prompt"
    )
    provider_used: str = Field(
        ..., description="Actual provider used (may differ if fallback was applied)"
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
                "content": "Dear Colleague,\\n\\nI hope this message...",
                "tokens_used": 127,
                "credits_deducted": 127,
                "pii_detected": False,
                "provider_used": "vertex_claude",
                "eu_compliant": True,
                "fallback_applied": False,
            }
        }


@router.post("/generate", response_model=GenerateResponse)
@limiter.limit("100/minute")
async def generate_content(
    request: Request,
    request_body: GenerateRequest,
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Generate AI response from user prompt.

    This endpoint:
    1. Validates license key from X-License-Key header
    2. Sanitizes the prompt for PII (emails, phones, IBANs)
    3. Generates AI response using Anthropic Claude
    4. Deducts credits atomically from license
    5. Returns formatted response

    Args:
        request: GenerateRequest with prompt
        license: Validated license info (from X-License-Key header)

    Returns:
        GenerateResponse with content, tokens, credits, and pii flag

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
                "PII detected in prompt for tenant_id=%s",
                license.tenant_id,
            )

        # Step 2: Validate provider selection and apply GDPR compliance
        requested_provider = request_body.provider
        fallback_applied = False

        # GDPR-003: Validate request and apply automatic fallback if needed
        is_valid, error_message = GDPRComplianceChecker.validate_request(
            requested_provider, request_body.eu_only
        )

        if not is_valid:
            # Get fallback provider if EU-only is requested
            fallback_provider = GDPRComplianceChecker.get_fallback_provider(
                requested_provider, request_body.eu_only
            )

            if fallback_provider:
                logger.warning(
                    f"GDPR compliance: Automatically falling back from "
                    f"'{requested_provider}' to '{fallback_provider}' (EU-only requested)"
                )
                provider_name = fallback_provider
                fallback_applied = True
            else:
                # No fallback available, raise error
                raise HTTPException(status_code=400, detail=error_message)
        else:
            provider_name = requested_provider

        # Get provider instance using factory
        provider = get_provider_instance(provider_name, request_body.model)
        model_used = request_body.model or AVAILABLE_PROVIDERS.get(provider_name, "unknown")

        # Check if provider is EU-compliant
        is_eu_compliant = GDPRComplianceChecker.is_provider_gdpr_compliant(provider_name)

        # Log GDPR compliance information for audit trail
        GDPRComplianceChecker.log_compliance_info(
            provider=provider_name,
            eu_only=request_body.eu_only,
            fallback_used=fallback_applied
        )

        logger.info(
            f"Using provider: {provider_name}, model: {model_used}, "
            f"EU-only: {request_body.eu_only}, EU-compliant: {is_eu_compliant}, "
            f"Fallback applied: {fallback_applied}"
        )

        try:
            content, tokens = await provider.generate(sanitized_prompt)
        except ProviderAPIError as e:
            logger.error(f"AI provider error: {e}")
            raise HTTPException(
                status_code=500,
                detail="AI generation failed. Please try again later.",
            ) from e

        # Step 3: Calculate credits (1:1 with tokens for MVP)
        credits_to_deduct = tokens

        # Step 4: Deduct credits atomically
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
            # Re-raise billing errors (402, 403, 500)
            logger.error(
                f"Billing failed for tenant {license.tenant_id}: "
                f"{billing_error.detail}"
            )
            raise

        # Step 4.1: Log usage
        # We launch this as a fire-and-forget task (but awaited to keep logic simple for now)
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

        # Step 5: Return successful response
        logger.info(
            f"Generated response: {tokens} tokens, "
            f"{credits_to_deduct} credits deducted, PII detected: {pii_found}, "
            f"Provider: {provider_name}, EU-compliant: {is_eu_compliant} "
            f"(tenant: {license.tenant_id})"
        )

        return GenerateResponse(
            content=content,
            tokens_used=tokens,
            credits_deducted=credits_to_deduct,
            pii_detected=pii_found,
            provider_used=provider_name,
            eu_compliant=is_eu_compliant,
            fallback_applied=fallback_applied,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in generate endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later.",
        ) from e


class ProviderInfo(BaseModel):
    """Provider information model."""
    name: str
    default_model: str
    eu_compliant: bool
    models: list[str]
    status: str = "available"


class ProvidersResponse(BaseModel):
    """Response model for /v1/providers endpoint."""
    providers: list[ProviderInfo]


@router.get("/providers", response_model=ProvidersResponse)
async def list_providers():
    """
    List available AI providers and their models.

    Returns information about all configured providers including:
    - Provider name
    - Default model
    - EU compliance status (DSGVO)
    - Available models
    - Provider status (available/unavailable)
    """
    providers_list = []

    # Anthropic (Direct)
    providers_list.append(ProviderInfo(
        name="anthropic",
        default_model=AVAILABLE_PROVIDERS["anthropic"],
        eu_compliant=False,
        models=["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        status="available"
    ))

    # Scaleway (EU)
    providers_list.append(ProviderInfo(
        name="scaleway",
        default_model=AVAILABLE_PROVIDERS["scaleway"],
        eu_compliant=True,
        models=[
            "llama-3.1-8b-instruct",
            "llama-3.3-70b-instruct",
            "mistral-small-3.2-24b-instruct-2506",
            "qwen3-235b-a22b-instruct-2507",
        ],
        status="available"
    ))

    # Vertex AI Claude (EU)
    try:
        from app.services.vertex_claude_provider import VertexClaudeProvider
        providers_list.append(ProviderInfo(
            name="vertex_claude",
            default_model=AVAILABLE_PROVIDERS["vertex_claude"],
            eu_compliant=True,
            models=VertexClaudeProvider.list_models(),
            status="available"
        ))
    except Exception:
        providers_list.append(ProviderInfo(
            name="vertex_claude",
            default_model=AVAILABLE_PROVIDERS["vertex_claude"],
            eu_compliant=True,
            models=[],
            status="not_configured"
        ))

    # Vertex AI Gemini (EU)
    try:
        from app.services.vertex_gemini_provider import VertexGeminiProvider
        providers_list.append(ProviderInfo(
            name="vertex_gemini",
            default_model=AVAILABLE_PROVIDERS["vertex_gemini"],
            eu_compliant=True,
            models=VertexGeminiProvider.list_models(),
            status="available"
        ))
    except Exception:
        providers_list.append(ProviderInfo(
            name="vertex_gemini",
            default_model=AVAILABLE_PROVIDERS["vertex_gemini"],
            eu_compliant=True,
            models=[],
            status="not_configured"
        ))

    return ProvidersResponse(providers=providers_list)
