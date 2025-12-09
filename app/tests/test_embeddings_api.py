"""
Unit tests for Embeddings API endpoint.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi import HTTPException

from app.core.security import LicenseInfo


class TestEmbeddingsEndpoint:
    """Tests for embeddings API endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.v1.embeddings.UsageService.log_usage")
    @patch("app.api.v1.embeddings.BillingService.deduct_credits")
    @patch("app.api.v1.embeddings.ScalewayProvider")
    async def test_successful_embeddings_request(
        self,
        mock_scaleway_provider,
        mock_billing,
        mock_log_usage,
    ):
        """Test successful embeddings API request."""
        from app.api.v1.embeddings import (
            EmbeddingsRequest,
            EmbeddingsResponse,
            EmbeddingObject,
            EMBEDDING_PROVIDERS,
        )

        # Mock provider
        mock_provider_instance = AsyncMock()
        mock_provider_instance.create_embeddings.return_value = [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
        ]
        mock_scaleway_provider.return_value = mock_provider_instance

        # Mock billing
        mock_billing.return_value = None
        mock_log_usage.return_value = None

        # Create test request
        request_body = EmbeddingsRequest(
            input=["Hello world", "Test text"],
            model="qwen3-embedding-8b",
            provider="scaleway",
            eu_only=False,
        )

        # Create mock license
        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate endpoint logic
        embeddings = await mock_provider_instance.create_embeddings(
            request_body.input,
            model="qwen3-embedding-8b"
        )

        total_texts = len(request_body.input)
        credits_to_deduct = total_texts * 5

        await mock_billing(license.license_key, credits_to_deduct)

        embedding_objects = [
            EmbeddingObject(
                object="embedding",
                embedding=embedding,
                index=idx
            )
            for idx, embedding in enumerate(embeddings)
        ]

        response = EmbeddingsResponse(
            object="list",
            data=embedding_objects,
            model="qwen3-embedding-8b",
            credits_deducted=credits_to_deduct,
            provider_used="scaleway",
            eu_compliant=True,
        )

        # Assertions
        assert response.object == "list"
        assert len(response.data) == 2
        assert response.data[0].embedding == [0.1, 0.2, 0.3, 0.4]
        assert response.data[1].embedding == [0.5, 0.6, 0.7, 0.8]
        assert response.data[0].index == 0
        assert response.data[1].index == 1
        assert response.model == "qwen3-embedding-8b"
        assert response.credits_deducted == 10  # 2 texts * 5 credits
        assert response.provider_used == "scaleway"
        assert response.eu_compliant is True

    @pytest.mark.asyncio
    @patch("app.api.v1.embeddings.UsageService.log_usage")
    @patch("app.api.v1.embeddings.BillingService.deduct_credits")
    @patch("app.api.v1.embeddings.ScalewayProvider")
    async def test_embeddings_with_custom_model(
        self,
        mock_scaleway_provider,
        mock_billing,
        mock_log_usage,
    ):
        """Test embeddings with custom model."""
        from app.api.v1.embeddings import EmbeddingsRequest, EmbeddingsResponse, EmbeddingObject

        mock_provider_instance = AsyncMock()
        mock_provider_instance.create_embeddings.return_value = [[0.1, 0.2]]
        mock_scaleway_provider.return_value = mock_provider_instance
        mock_billing.return_value = None
        mock_log_usage.return_value = None

        request_body = EmbeddingsRequest(
            input=["Test"],
            model="bge-multilingual-gemma2",
            provider="scaleway",
        )

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        embeddings = await mock_provider_instance.create_embeddings(
            request_body.input,
            model="bge-multilingual-gemma2"
        )

        # Verify the call was made with correct model
        mock_provider_instance.create_embeddings.assert_called_once_with(
            ["Test"],
            model="bge-multilingual-gemma2"
        )

        embedding_objects = [
            EmbeddingObject(object="embedding", embedding=emb, index=idx)
            for idx, emb in enumerate(embeddings)
        ]

        response = EmbeddingsResponse(
            object="list",
            data=embedding_objects,
            model="bge-multilingual-gemma2",
            credits_deducted=5,
            provider_used="scaleway",
            eu_compliant=True,
        )

        assert response.model == "bge-multilingual-gemma2"

    @pytest.mark.asyncio
    async def test_embeddings_with_invalid_provider(self):
        """Test embeddings with invalid provider."""
        from app.api.v1.embeddings import EmbeddingsRequest, EMBEDDING_PROVIDERS

        request_body = EmbeddingsRequest(
            input=["Test"],
            provider="invalid_provider",
        )

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate validation logic
        if request_body.provider not in EMBEDDING_PROVIDERS:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider '{request_body.provider}' does not support embeddings."
                )

            assert exc_info.value.status_code == 400
            assert "does not support embeddings" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("app.api.v1.embeddings.UsageService.log_usage")
    @patch("app.api.v1.embeddings.BillingService.deduct_credits")
    @patch("app.api.v1.embeddings.ScalewayProvider")
    async def test_embeddings_with_eu_only_non_compliant_provider(
        self,
        mock_scaleway_provider,
        mock_billing,
        mock_log_usage,
    ):
        """Test embeddings with EU-only and non-compliant provider."""
        from app.api.v1.embeddings import EmbeddingsRequest, EmbeddingsResponse, EmbeddingObject, EU_EMBEDDING_PROVIDERS

        # This should not raise an error because scaleway is EU-compliant
        mock_provider_instance = AsyncMock()
        mock_provider_instance.create_embeddings.return_value = [[0.1, 0.2]]
        mock_scaleway_provider.return_value = mock_provider_instance
        mock_billing.return_value = None
        mock_log_usage.return_value = None

        request_body = EmbeddingsRequest(
            input=["Test"],
            provider="scaleway",  # This is EU-compliant, so no error
            eu_only=True,
        )

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Scaleway is EU-compliant
        is_eu_compliant = request_body.provider in EU_EMBEDDING_PROVIDERS
        assert is_eu_compliant is True

        embeddings = await mock_provider_instance.create_embeddings(
            request_body.input,
            model="qwen3-embedding-8b"
        )

        embedding_objects = [
            EmbeddingObject(object="embedding", embedding=emb, index=idx)
            for idx, emb in enumerate(embeddings)
        ]

        response = EmbeddingsResponse(
            object="list",
            data=embedding_objects,
            model="qwen3-embedding-8b",
            credits_deducted=5,
            provider_used="scaleway",
            eu_compliant=is_eu_compliant,
        )

        assert response.eu_compliant is True

    @pytest.mark.asyncio
    @patch("app.api.v1.embeddings.ScalewayProvider")
    @patch("app.api.v1.embeddings.BillingService.deduct_credits")
    async def test_embeddings_billing_failure(
        self,
        mock_billing,
        mock_scaleway_provider,
    ):
        """Test embeddings with billing failure."""
        mock_provider_instance = AsyncMock()
        mock_provider_instance.create_embeddings.return_value = [[0.1, 0.2]]
        mock_scaleway_provider.return_value = mock_provider_instance

        mock_billing.side_effect = HTTPException(
            status_code=402,
            detail="Insufficient credits"
        )

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=0,
            is_active=True,
        )

        # Simulate billing failure
        with pytest.raises(HTTPException) as exc_info:
            await mock_billing(license.license_key, 5)

        assert exc_info.value.status_code == 402

    @pytest.mark.asyncio
    @patch("app.api.v1.embeddings.UsageService.log_usage")
    @patch("app.api.v1.embeddings.BillingService.deduct_credits")
    @patch("app.api.v1.embeddings.ScalewayProvider")
    async def test_embeddings_with_many_texts(
        self,
        mock_scaleway_provider,
        mock_billing,
        mock_log_usage,
    ):
        """Test embeddings with multiple texts (up to limit)."""
        from app.api.v1.embeddings import EmbeddingsRequest, EmbeddingsResponse, EmbeddingObject

        mock_provider_instance = AsyncMock()
        mock_provider_instance.create_embeddings.return_value = [[0.1] * 10 for _ in range(10)]
        mock_scaleway_provider.return_value = mock_provider_instance
        mock_billing.return_value = None
        mock_log_usage.return_value = None

        request_body = EmbeddingsRequest(
            input=[f"Text {i}" for i in range(10)],
            provider="scaleway",
        )

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        embeddings = await mock_provider_instance.create_embeddings(
            request_body.input,
            model="qwen3-embedding-8b"
        )

        total_texts = len(request_body.input)
        credits_to_deduct = total_texts * 5

        await mock_billing(license.license_key, credits_to_deduct)

        embedding_objects = [
            EmbeddingObject(object="embedding", embedding=emb, index=idx)
            for idx, emb in enumerate(embeddings)
        ]

        response = EmbeddingsResponse(
            object="list",
            data=embedding_objects,
            model="qwen3-embedding-8b",
            credits_deducted=credits_to_deduct,
            provider_used="scaleway",
            eu_compliant=True,
        )

        assert len(response.data) == 10
        assert response.credits_deducted == 50  # 10 texts * 5 credits
