"""
AI Embeddings API endpoint.

Provides /v1/embeddings endpoint for generating text embeddings:
- Text embedding generation for semantic search, RAG, etc.
- Multi-provider support (Scaleway)
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
from app.services.billing import BillingService
from app.services.scaleway_provider import ScalewayProvider
from app.services.usage import UsageService

logger = logging.getLogger(__name__)

router = APIRouter()


# Embedding providers and their default models
EMBEDDING_PROVIDERS = {
    "scaleway": "qwen3-embedding-8b",
}

# EU-compliant embedding providers
EU_EMBEDDING_PROVIDERS = ["scaleway"]


def get_embedding_provider_instance(provider_name: str, model: Optional[str] = None):
    """
    Factory function to create embedding provider instances.

    Args:
        provider_name: Name of the provider
        model: Optional model override

    Returns:
        AI provider instance with embedding capabilities

    Raises:
        HTTPException: If provider is invalid or not configured
    """
    if provider_name == "scaleway":
        return ScalewayProvider(model=model) if model else ScalewayProvider()

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider '{provider_name}'. "
                   f"Embedding-capable providers: {list(EMBEDDING_PROVIDERS.keys())}"
        )


class EmbeddingsRequest(BaseModel):
    """Request model for /v1/embeddings endpoint."""

    input: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of texts to embed (max 100 texts)",
    )

    model: Optional[str] = Field(
        default=None,
        description="Embedding model to use (e.g., 'qwen3-embedding-8b', 'bge-multilingual-gemma2')",
    )

    provider: str = Field(
        default="scaleway",
        description="AI provider: 'scaleway'",
    )

    eu_only: bool = Field(
        default=False,
        description="If true, only allow EU-compliant providers (DSGVO)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "input": [
                    "Machine learning is a subset of artificial intelligence.",
                    "Natural language processing enables computers to understand text.",
                ],
                "model": "qwen3-embedding-8b",
                "provider": "scaleway",
                "eu_only": False,
            }
        }


class EmbeddingObject(BaseModel):
    """Individual embedding object."""

    object: str = "embedding"
    embedding: list[float] = Field(..., description="The embedding vector")
    index: int = Field(..., description="The index of this embedding in the input list")


class EmbeddingsResponse(BaseModel):
    """Response model for /v1/embeddings endpoint."""

    object: str = "list"
    data: list[EmbeddingObject] = Field(..., description="List of embedding objects")
    model: str = Field(..., description="Model used for embeddings")
    credits_deducted: int = Field(
        ..., description="Credits deducted from tenant account"
    )
    provider_used: str = Field(
        ..., description="Actual provider used"
    )
    eu_compliant: bool = Field(
        ..., description="Whether the provider used is EU-compliant (GDPR)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": [0.123, -0.456, 0.789],
                        "index": 0,
                    },
                    {
                        "object": "embedding",
                        "embedding": [0.234, -0.567, 0.890],
                        "index": 1,
                    },
                ],
                "model": "qwen3-embedding-8b",
                "credits_deducted": 10,
                "provider_used": "scaleway",
                "eu_compliant": True,
            }
        }


@router.post("/embeddings", response_model=EmbeddingsResponse)
@limiter.limit("100/minute")
async def create_embeddings(
    request: Request,
    request_body: EmbeddingsRequest,
    license: LicenseInfo = Depends(get_current_license),
):
    """
    Generate text embeddings using AI models.

    This endpoint:
    1. Validates license key from X-License-Key header
    2. Generates embeddings for provided texts
    3. Deducts credits based on input tokens
    4. Returns embeddings in OpenAI-compatible format

    Args:
        request: FastAPI request object
        request_body: EmbeddingsRequest with texts to embed
        license: Validated license info (from X-License-Key header)

    Returns:
        EmbeddingsResponse with embedding vectors and metadata

    Raises:
        HTTPException 401: Missing X-License-Key header
        HTTPException 403: Invalid/inactive/expired license
        HTTPException 402: No credits remaining
        HTTPException 422: Validation error (automatic)
        HTTPException 500: Embedding generation failed
    """
    try:
        # Step 1: Validate provider selection and apply GDPR compliance
        requested_provider = request_body.provider

        # Check if requested provider is valid for embeddings
        if requested_provider not in EMBEDDING_PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{requested_provider}' does not support embeddings. "
                       f"Use one of: {list(EMBEDDING_PROVIDERS.keys())}"
            )

        # GDPR validation
        if request_body.eu_only and requested_provider not in EU_EMBEDDING_PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{requested_provider}' is not EU-compliant. "
                       f"EU-compliant embedding providers: {EU_EMBEDDING_PROVIDERS}"
            )

        provider_name = requested_provider

        # Get provider instance
        provider = get_embedding_provider_instance(provider_name, request_body.model)
        model_used = request_body.model or EMBEDDING_PROVIDERS.get(provider_name, "qwen3-embedding-8b")

        # Check if provider is EU-compliant
        is_eu_compliant = provider_name in EU_EMBEDDING_PROVIDERS

        logger.info(
            f"Embeddings API - Using provider: {provider_name}, model: {model_used}, "
            f"EU-only: {request_body.eu_only}, EU-compliant: {is_eu_compliant}, "
            f"Input count: {len(request_body.input)}"
        )

        # Step 2: Generate embeddings
        try:
            if isinstance(provider, ScalewayProvider):
                embeddings = await provider.create_embeddings(
                    request_body.input,
                    model=model_used
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Provider does not support embeddings API"
                )
        except ProviderAPIError as e:
            logger.error(f"Embeddings API provider error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Embedding generation failed. Please try again later.",
            ) from e

        # Step 3: Calculate credits
        # Credit calculation: Base cost per text + token-based cost
        # For simplicity: 5 credits per text embedded
        total_texts = len(request_body.input)
        credits_to_deduct = total_texts * 5

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
            logger.error(
                f"Billing failed for tenant {license.tenant_id}: "
                f"{billing_error.detail}"
            )
            raise

        # Step 5: Log usage
        try:
            await UsageService.log_usage(
                license_id=license.license_uuid,
                app_id=license.app_id,
                tenant_id=license.tenant_id,
                tokens_used=total_texts * 10,  # Rough estimate
                credits_deducted=credits_to_deduct,
                provider=provider_name,
                model=model_used,
                prompt_length=sum(len(text) for text in request_body.input),
                pii_detected=False,  # No PII sanitization for embeddings
                response_status="success"
            )
        except Exception as log_error:
            logger.error(f"Failed to log usage: {log_error}")
            # Do not fail request

        # Step 6: Format response in OpenAI-compatible format
        embedding_objects = [
            EmbeddingObject(
                object="embedding",
                embedding=embedding,
                index=idx
            )
            for idx, embedding in enumerate(embeddings)
        ]

        logger.info(
            f"Generated {len(embeddings)} embeddings, "
            f"{credits_to_deduct} credits deducted, "
            f"Provider: {provider_name}, EU-compliant: {is_eu_compliant} "
            f"(tenant: {license.tenant_id})"
        )

        return EmbeddingsResponse(
            object="list",
            data=embedding_objects,
            model=model_used,
            credits_deducted=credits_to_deduct,
            provider_used=provider_name,
            eu_compliant=is_eu_compliant,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in embeddings endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later.",
        ) from e
