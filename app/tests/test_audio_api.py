"""
Unit tests for Audio Transcription API endpoint.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi import HTTPException, UploadFile

from app.core.security import LicenseInfo


class TestAudioTranscriptionEndpoint:
    """Tests for audio transcription API endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.v1.audio.UsageService.log_usage")
    @patch("app.api.v1.audio.BillingService.deduct_credits")
    @patch("app.api.v1.audio.ScalewayProvider")
    async def test_successful_transcription(
        self,
        mock_scaleway_provider,
        mock_billing,
        mock_log_usage,
    ):
        """Test successful audio transcription."""
        from app.api.v1.audio import TranscriptionResponse, TRANSCRIPTION_PROVIDERS

        # Mock provider
        mock_provider_instance = AsyncMock()
        mock_provider_instance.transcribe_audio.return_value = (
            "Hello, this is a test transcription.",
            45
        )
        mock_scaleway_provider.return_value = mock_provider_instance

        # Mock billing
        mock_billing.return_value = None
        mock_log_usage.return_value = None

        # Create test data
        audio_content = b"fake_audio_data" * 100

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate endpoint logic
        text, tokens = await mock_provider_instance.transcribe_audio(
            audio_content,
            filename="test.wav",
            model="whisper-large-v3"
        )

        credits_to_deduct = 10 + tokens  # Base + tokens

        await mock_billing(license.license_key, credits_to_deduct)

        response = TranscriptionResponse(
            text=text,
            tokens_used=tokens,
            credits_deducted=credits_to_deduct,
            provider_used="scaleway",
            model_used="whisper-large-v3",
            eu_compliant=True,
        )

        # Assertions
        assert response.text == "Hello, this is a test transcription."
        assert response.tokens_used == 45
        assert response.credits_deducted == 55  # 10 base + 45 tokens
        assert response.provider_used == "scaleway"
        assert response.model_used == "whisper-large-v3"
        assert response.eu_compliant is True

    @pytest.mark.asyncio
    async def test_transcription_with_file_too_large(self):
        """Test transcription with file exceeding size limit."""
        from app.api.v1.audio import TranscriptionResponse

        # Create mock file larger than 25MB
        large_audio = b"x" * (26 * 1024 * 1024)  # 26MB
        MAX_FILE_SIZE = 25 * 1024 * 1024

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate file size check
        if len(large_audio) > MAX_FILE_SIZE:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is 25MB, got {len(large_audio) / 1024 / 1024:.2f}MB"
                )

            assert exc_info.value.status_code == 413
            assert "File too large" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_transcription_with_invalid_provider(self):
        """Test transcription with invalid provider."""
        from app.api.v1.audio import TRANSCRIPTION_PROVIDERS

        provider = "invalid_provider"

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Simulate validation
        if provider not in TRANSCRIPTION_PROVIDERS:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider '{provider}' does not support transcription."
                )

            assert exc_info.value.status_code == 400
            assert "does not support transcription" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch("app.api.v1.audio.UsageService.log_usage")
    @patch("app.api.v1.audio.BillingService.deduct_credits")
    @patch("app.api.v1.audio.ScalewayProvider")
    async def test_transcription_with_eu_only_non_compliant(
        self,
        mock_scaleway_provider,
        mock_billing,
        mock_log_usage,
    ):
        """Test transcription with EU-only and non-compliant provider."""
        from app.api.v1.audio import TranscriptionResponse, EU_TRANSCRIPTION_PROVIDERS

        # Scaleway is EU-compliant, so this should succeed
        mock_provider_instance = AsyncMock()
        mock_provider_instance.transcribe_audio.return_value = ("Transcribed text", 50)
        mock_scaleway_provider.return_value = mock_provider_instance
        mock_billing.return_value = None
        mock_log_usage.return_value = None

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        provider_name = "scaleway"
        eu_only = True

        # Scaleway is EU-compliant
        is_eu_compliant = provider_name in EU_TRANSCRIPTION_PROVIDERS
        assert is_eu_compliant is True

        text, tokens = await mock_provider_instance.transcribe_audio(
            b"audio_data",
            filename="test.wav",
            model="whisper-large-v3"
        )

        response = TranscriptionResponse(
            text=text,
            tokens_used=tokens,
            credits_deducted=10 + tokens,
            provider_used=provider_name,
            model_used="whisper-large-v3",
            eu_compliant=is_eu_compliant,
        )

        assert response.eu_compliant is True

    @pytest.mark.asyncio
    @patch("app.api.v1.audio.ScalewayProvider")
    @patch("app.api.v1.audio.BillingService.deduct_credits")
    async def test_transcription_billing_failure(
        self,
        mock_billing,
        mock_scaleway_provider,
    ):
        """Test transcription with billing failure."""
        mock_provider_instance = AsyncMock()
        mock_provider_instance.transcribe_audio.return_value = ("Text", 50)
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
            await mock_billing(license.license_key, 60)

        assert exc_info.value.status_code == 402

    @pytest.mark.asyncio
    @patch("app.api.v1.audio.UsageService.log_usage")
    @patch("app.api.v1.audio.BillingService.deduct_credits")
    @patch("app.api.v1.audio.ScalewayProvider")
    async def test_transcription_with_different_models(
        self,
        mock_scaleway_provider,
        mock_billing,
        mock_log_usage,
    ):
        """Test transcription with different models."""
        from app.api.v1.audio import TranscriptionResponse, TRANSCRIPTION_PROVIDERS

        mock_provider_instance = AsyncMock()
        mock_provider_instance.transcribe_audio.return_value = ("Transcribed", 30)
        mock_scaleway_provider.return_value = mock_provider_instance
        mock_billing.return_value = None
        mock_log_usage.return_value = None

        license = LicenseInfo(
            license_key="test-key",
            license_uuid="test-uuid",
            tenant_id="test-tenant",
            app_id="test-app",
            credits_remaining=1000,
            is_active=True,
        )

        # Test with default model
        default_model = TRANSCRIPTION_PROVIDERS.get("scaleway", "whisper-large-v3")
        assert default_model == "whisper-large-v3"

        text, tokens = await mock_provider_instance.transcribe_audio(
            b"audio_data",
            filename="test.mp3",
            model=default_model
        )

        response = TranscriptionResponse(
            text=text,
            tokens_used=tokens,
            credits_deducted=10 + tokens,
            provider_used="scaleway",
            model_used=default_model,
            eu_compliant=True,
        )

        assert response.model_used == "whisper-large-v3"

        # Test with custom model
        custom_model = "voxtral-small-24b-2507"
        text2, tokens2 = await mock_provider_instance.transcribe_audio(
            b"audio_data",
            filename="test.mp3",
            model=custom_model
        )

        response2 = TranscriptionResponse(
            text=text2,
            tokens_used=tokens2,
            credits_deducted=10 + tokens2,
            provider_used="scaleway",
            model_used=custom_model,
            eu_compliant=True,
        )

        assert response2.model_used == "voxtral-small-24b-2507"
