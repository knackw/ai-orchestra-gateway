"""
AI text generation endpoint.

Provides /v1/generate endpoint for generating AI responses with:
- Automatic PII sanitization (DataPrivacyShield)
- AI generation via Anthropic Claude
- Token usage tracking
- Credit calculation
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import LicenseInfo, get_current_license
from app.services.ai_gateway import ProviderAPIError
from app.services.anthropic_provider import AnthropicProvider
from app.services.billing import BillingService
from app.services.privacy import DataPrivacyShield

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request model for /v1/generate endpoint."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User prompt for AI generation",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a professional email to my colleague",
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

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Dear Colleague,\\n\\nI hope this message...",
                "tokens_used": 127,
                "credits_deducted": 127,
                "pii_detected": False,
            }
        }


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
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
        sanitized_prompt, pii_found = DataPrivacyShield.sanitize(request.prompt)

        if pii_found:
            logger.warning(
                "PII detected in prompt for tenant_id=%s",
                license.tenant_id,
            )

        # Step 2: Generate AI response
        # License already validated by dependency
        provider = AnthropicProvider()

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

        # Step 5: Return successful response
        logger.info(
            f"Generated response: {tokens} tokens, "
            f"{credits_to_deduct} credits deducted, PII detected: {pii_found} "
            f"(tenant: {license.tenant_id})"
        )

        return GenerateResponse(
            content=content,
            tokens_used=tokens,
            credits_deducted=credits_to_deduct,
            pii_detected=pii_found,
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
