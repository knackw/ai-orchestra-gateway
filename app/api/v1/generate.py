"""
AI text generation endpoint.

Provides /v1/generate endpoint for generating AI responses with:
- Automatic PII sanitization (DataPrivacyShield)
- AI generation via Anthropic Claude
- Token usage tracking
- Credit calculation
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_gateway import ProviderAPIError
from app.services.anthropic_provider import AnthropicProvider
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
    license_key: str = Field(
        ..., min_length=1, description="Tenant license key for authentication"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a professional email to my colleague",
                "license_key": "lic_abc123def456",
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
                "content": "Dear Colleague,\n\nI hope this message...",
                "tokens_used": 127,
                "credits_deducted": 127,
                "pii_detected": False,
            }
        }


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Generate AI response from user prompt.

    This endpoint:
    1. Sanitizes the prompt for PII (emails, phones, IBANs)
    2. Generates AI response using Anthropic Claude
    3. Calculates tokens and credits
    4. Returns formatted response

    Args:
        request: GenerateRequest with prompt and license_key

    Returns:
        GenerateResponse with content, tokens, credits, and pii flag

    Raises:
        HTTPException 422: Validation error (automatic)
        HTTPException 500: AI generation failed
    """
    try:
        # Step 1: Sanitize prompt for PII
        sanitized_prompt, pii_found = DataPrivacyShield.sanitize(request.prompt)

        if pii_found:
            logger.warning(
                "PII detected in prompt for license_key=%s",
                request.license_key[:10] + "...",
            )

        # Step 2: Generate AI response
        # Note: license_key validation will be added in API-002
        # For MVP, we accept any non-empty string
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
        # Future: Make configurable per model/tenant
        credits = tokens

        # Note: Actual credit deduction will be in BILLING-001
        # For now, we just return the calculated amount

        # Step 4: Return response
        logger.info(
            f"Generated response: {tokens} tokens, "
            f"{credits} credits, PII detected: {pii_found}"
        )

        return GenerateResponse(
            content=content,
            tokens_used=tokens,
            credits_deducted=credits,
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
