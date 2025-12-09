"""
AI Audio Transcription API endpoint.

Provides /v1/audio/transcriptions endpoint for transcribing audio to text:
- Audio transcription using Whisper and other models
- Multi-provider support (Scaleway)
- Token usage tracking
- Credit calculation
- DSGVO-compliant EU providers
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
from pydantic import BaseModel, Field

from app.core.security import LicenseInfo, get_current_license
from app.core.rate_limit import limiter
from app.services.ai_gateway import ProviderAPIError
from app.services.billing import BillingService
from app.services.scaleway_provider import ScalewayProvider
from app.services.usage import UsageService

logger = logging.getLogger(__name__)

router = APIRouter()


# Transcription providers and their default models
TRANSCRIPTION_PROVIDERS = {
    "scaleway": "whisper-large-v3",
}

# EU-compliant transcription providers
EU_TRANSCRIPTION_PROVIDERS = ["scaleway"]


def get_transcription_provider_instance(provider_name: str, model: Optional[str] = None):
    """
    Factory function to create transcription provider instances.

    Args:
        provider_name: Name of the provider
        model: Optional model override

    Returns:
        AI provider instance with transcription capabilities

    Raises:
        HTTPException: If provider is invalid or not configured
    """
    if provider_name == "scaleway":
        return ScalewayProvider(model=model) if model else ScalewayProvider()

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider '{provider_name}'. "
                   f"Transcription-capable providers: {list(TRANSCRIPTION_PROVIDERS.keys())}"
        )


class TranscriptionResponse(BaseModel):
    """Response model for /v1/audio/transcriptions endpoint."""

    text: str = Field(..., description="The transcribed text")
    tokens_used: int = Field(..., description="Number of tokens consumed (estimated)")
    credits_deducted: int = Field(
        ..., description="Credits deducted from tenant account"
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

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a test transcription of the audio file.",
                "tokens_used": 45,
                "credits_deducted": 45,
                "provider_used": "scaleway",
                "model_used": "whisper-large-v3",
                "eu_compliant": True,
            }
        }


@router.post("/audio/transcriptions", response_model=TranscriptionResponse)
@limiter.limit("30/minute")
async def transcribe_audio(
    request: Request,
    file: UploadFile = File(..., description="Audio file to transcribe (max 25MB)"),
    model: Optional[str] = Form(None, description="Transcription model (e.g., 'whisper-large-v3')"),
    provider: str = Form("scaleway", description="AI provider"),
    eu_only: bool = Form(False, description="If true, only allow EU-compliant providers"),
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Transcribe audio to text using AI models.

    This endpoint:
    1. Validates license key from X-License-Key header
    2. Accepts audio file upload (WAV, MP3, etc.)
    3. Transcribes audio using selected provider
    4. Deducts credits based on audio duration/tokens
    5. Returns transcribed text

    Args:
        request: FastAPI request object
        file: Audio file to transcribe
        model: Model to use for transcription
        provider: Provider to use
        eu_only: Whether to enforce EU-only processing
        license: Validated license info (from X-License-Key header)

    Returns:
        TranscriptionResponse with transcribed text and metadata

    Raises:
        HTTPException 401: Missing X-License-Key header
        HTTPException 403: Invalid/inactive/expired license
        HTTPException 402: No credits remaining
        HTTPException 413: File too large
        HTTPException 500: Transcription failed
    """
    try:
        # Step 1: Validate file size (max 25MB as per Scaleway limits)
        MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
        audio_data = await file.read()

        if len(audio_data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 25MB, got {len(audio_data) / 1024 / 1024:.2f}MB"
            )

        # Step 2: Validate provider selection
        requested_provider = provider

        if requested_provider not in TRANSCRIPTION_PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{requested_provider}' does not support transcription. "
                       f"Use one of: {list(TRANSCRIPTION_PROVIDERS.keys())}"
            )

        # GDPR validation
        if eu_only and requested_provider not in EU_TRANSCRIPTION_PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{requested_provider}' is not EU-compliant. "
                       f"EU-compliant transcription providers: {EU_TRANSCRIPTION_PROVIDERS}"
            )

        provider_name = requested_provider

        # Get provider instance
        provider_instance = get_transcription_provider_instance(provider_name, model)
        model_used = model or TRANSCRIPTION_PROVIDERS.get(provider_name, "whisper-large-v3")

        # Check if provider is EU-compliant
        is_eu_compliant = provider_name in EU_TRANSCRIPTION_PROVIDERS

        logger.info(
            f"Transcription API - Using provider: {provider_name}, model: {model_used}, "
            f"EU-only: {eu_only}, EU-compliant: {is_eu_compliant}, "
            f"File size: {len(audio_data) / 1024:.2f}KB"
        )

        # Step 3: Transcribe audio
        try:
            if isinstance(provider_instance, ScalewayProvider):
                text, tokens = await provider_instance.transcribe_audio(
                    audio_data,
                    filename=file.filename or "audio.wav",
                    model=model_used
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Provider does not support transcription API"
                )
        except ProviderAPIError as e:
            logger.error(f"Transcription API provider error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Audio transcription failed. Please try again later.",
            ) from e

        # Step 4: Calculate credits
        # Base cost + token-based cost
        # For audio: 10 base credits + 1 credit per token
        credits_to_deduct = 10 + tokens

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
                prompt_length=len(audio_data),
                pii_detected=False,
                response_status="success"
            )
        except Exception as log_error:
            logger.error(f"Failed to log usage: {log_error}")
            # Do not fail request

        # Step 7: Return response
        logger.info(
            f"Transcribed audio: {tokens} tokens, "
            f"{credits_to_deduct} credits deducted, "
            f"Provider: {provider_name}, EU-compliant: {is_eu_compliant} "
            f"(tenant: {license.tenant_id})"
        )

        return TranscriptionResponse(
            text=text,
            tokens_used=tokens,
            credits_deducted=credits_to_deduct,
            provider_used=provider_name,
            model_used=model_used,
            eu_compliant=is_eu_compliant,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in transcription endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later.",
        ) from e
