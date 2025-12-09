"""
Unit tests for ScalewayProvider.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.scaleway_provider import (
    ScalewayProvider,
    SCALEWAY_MODELS,
    ModelCapability,
    get_chat_models,
    get_vision_models,
    get_embedding_models,
)
from app.services.ai_gateway import ProviderAPIError


class TestScalewayProvider:
    """Tests for ScalewayProvider."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        provider = ScalewayProvider(api_key="test_key_123")
        assert provider.api_key == "test_key_123"
        assert provider.provider_name == "scaleway"
        assert provider.model == ScalewayProvider.DEFAULT_MODEL

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch("app.services.scaleway_provider.settings") as mock_settings:
            mock_settings.SCALEWAY_API_KEY = ""
            with pytest.raises(ValueError, match="SCALEWAY_API_KEY must be set"):
                ScalewayProvider()

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="llama-3.1-70b-instruct"
        )
        assert provider.model == "llama-3.1-70b-instruct"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_successful_generation(self, mock_client_class):
        """Test successful AI generation."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Generated response text"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20
            }
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        content, tokens = await provider.generate("Test prompt")

        assert content == "Generated response text"
        assert tokens == 30  # 10 + 20

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_authentication_error(self, mock_client_class):
        """Test handling of 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="invalid_key")
        
        with pytest.raises(ProviderAPIError, match="Authentication failed"):
            await provider.generate("Test prompt")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_rate_limit_error(self, mock_client_class):
        """Test handling of 429 rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        
        with pytest.raises(ProviderAPIError, match="Rate limit exceeded"):
            await provider.generate("Test prompt")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_server_error(self, mock_client_class):
        """Test handling of 500 server error."""
        mock_response = Mock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        
        with pytest.raises(ProviderAPIError, match="server error"):
            await provider.generate("Test prompt")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_network_error(self, mock_client_class):
        """Test handling of network errors."""
        import httpx

        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.RequestError("Network error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        
        with pytest.raises(ProviderAPIError, match="Network error"):
            await provider.generate("Test prompt")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_invalid_response_format(self, mock_client_class):
        """Test handling of invalid response format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "format"}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        
        with pytest.raises(ProviderAPIError, match="Invalid response"):
            await provider.generate("Test prompt")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_custom_model_selection(self, mock_client_class):
        """Test that custom model is used in API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10}
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(
            api_key="test_key",
            model="llama-3.1-70b-instruct"
        )
        await provider.generate("Test")

        # Verify correct model in API call
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["model"] == "llama-3.1-70b-instruct"


class TestScalewayVisionAPI:
    """Tests for Scaleway Vision API support."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_generate_with_vision_success(self, mock_client_class):
        """Test successful vision API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This image shows a cat sitting on a couch."
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 20
            }
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Use a vision-capable model
        provider = ScalewayProvider(
            api_key="test_key",
            model="pixtral-12b-2409"
        )
        content, tokens = await provider.generate_with_vision(
            "What's in this image?",
            "https://example.com/image.jpg"
        )

        assert content == "This image shows a cat sitting on a couch."
        assert tokens == 70

        # Verify the API call format
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["model"] == "pixtral-12b-2409"
        assert len(payload["messages"]) == 1
        assert len(payload["messages"][0]["content"]) == 2
        assert payload["messages"][0]["content"][0]["type"] == "text"
        assert payload["messages"][0]["content"][1]["type"] == "image_url"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_generate_with_image_success(self, mock_client_class):
        """Test generate_with_image method (original method name)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Image description"}}],
            "usage": {"prompt_tokens": 30, "completion_tokens": 10}
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(
            api_key="test_key",
            model="mistral-small-3.2-24b-instruct-2506"
        )
        content, tokens = await provider.generate_with_image(
            "Describe this",
            "data:image/png;base64,iVBORw0KG..."
        )

        assert content == "Image description"
        assert tokens == 40

    @pytest.mark.asyncio
    async def test_vision_with_non_vision_model_fails(self):
        """Test that vision API fails when using non-vision model."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="llama-3.1-8b-instruct"  # Chat-only model
        )

        with pytest.raises(
            ProviderAPIError,
            match="does not support vision"
        ):
            await provider.generate_with_vision(
                "What's in this image?",
                "https://example.com/image.jpg"
            )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_vision_api_http_error(self, mock_client_class):
        """Test vision API HTTP error handling."""
        import httpx

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request",
            request=Mock(),
            response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(
            api_key="test_key",
            model="pixtral-12b-2409"
        )

        with pytest.raises(ProviderAPIError, match="Vision API error"):
            await provider.generate_with_vision(
                "Analyze",
                "https://example.com/image.jpg"
            )

    def test_supports_vision_true(self):
        """Test supports_vision returns True for vision models."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="pixtral-12b-2409"
        )
        assert provider.supports_vision() is True

    def test_supports_vision_false(self):
        """Test supports_vision returns False for chat-only models."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="llama-3.1-8b-instruct"
        )
        assert provider.supports_vision() is False


class TestScalewayAudioTranscription:
    """Tests for Scaleway Audio Transcription API."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_transcribe_audio_success(self, mock_client_class):
        """Test successful audio transcription."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "text": "Hello, this is a test transcription."
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        audio_data = b"fake_audio_bytes"

        text, tokens = await provider.transcribe_audio(
            audio_data,
            filename="test.wav",
            model="whisper-large-v3"
        )

        assert text == "Hello, this is a test transcription."
        assert tokens > 0  # Should estimate tokens from text length

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_transcribe_audio_with_default_model(self, mock_client_class):
        """Test transcription with default model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "text": "Test transcription"
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        audio_data = b"fake_audio"

        text, tokens = await provider.transcribe_audio(audio_data)

        assert text == "Test transcription"
        assert tokens > 0

        # Verify correct model used
        call_args = mock_client.post.call_args
        data = call_args.kwargs["data"]
        assert data["model"] == "whisper-large-v3"

    @pytest.mark.asyncio
    async def test_transcribe_audio_invalid_model(self):
        """Test transcription with non-transcription model."""
        provider = ScalewayProvider(api_key="test_key")
        audio_data = b"fake_audio"

        with pytest.raises(
            Exception,  # Should raise ProviderAPIError
            match="does not support transcription"
        ):
            await provider.transcribe_audio(
                audio_data,
                model="llama-3.1-8b-instruct"  # Not a transcription model
            )

    def test_supports_audio_false_for_chat_model(self):
        """Test supports_audio returns False for chat-only models."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="llama-3.1-8b-instruct"
        )
        assert provider.supports_audio() is False

    def test_supports_audio_true_for_voxtral(self):
        """Test supports_audio returns True for Voxtral model."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="voxtral-small-24b-2507"
        )
        assert provider.supports_audio() is True


class TestScalewayEmbeddingsAPI:
    """Tests for Scaleway Embeddings API."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_create_embeddings_success(self, mock_client_class):
        """Test successful embeddings creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3, 0.4]},
                {"embedding": [0.5, 0.6, 0.7, 0.8]},
            ]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        embeddings = await provider.create_embeddings(
            ["Hello world", "Test text"]
        )

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3, 0.4]
        assert embeddings[1] == [0.5, 0.6, 0.7, 0.8]

        # Verify API call
        call_args = mock_client.post.call_args
        assert call_args.args[0] == ScalewayProvider.EMBEDDINGS_URL
        payload = call_args.kwargs["json"]
        assert payload["model"] == "qwen3-embedding-8b"
        assert payload["input"] == ["Hello world", "Test text"]

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_create_embeddings_custom_model(self, mock_client_class):
        """Test embeddings with custom model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2]}]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")
        await provider.create_embeddings(
            ["Test"],
            model="bge-multilingual-gemma2"
        )

        # Verify correct model used
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["model"] == "bge-multilingual-gemma2"

    @pytest.mark.asyncio
    async def test_create_embeddings_invalid_model(self):
        """Test embeddings with non-embedding model fails."""
        provider = ScalewayProvider(api_key="test_key")

        with pytest.raises(
            ProviderAPIError,
            match="is not an embedding model"
        ):
            await provider.create_embeddings(
                ["Test"],
                model="llama-3.1-8b-instruct"  # Chat model, not embedding
            )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_create_embeddings_http_error(self, mock_client_class):
        """Test embeddings API HTTP error handling."""
        import httpx

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error",
            request=Mock(),
            response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")

        with pytest.raises(ProviderAPIError, match="Embeddings API error"):
            await provider.create_embeddings(["Test"])

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_create_embeddings_network_error(self, mock_client_class):
        """Test embeddings API network error handling."""
        import httpx

        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.RequestError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")

        with pytest.raises(ProviderAPIError, match="Network error"):
            await provider.create_embeddings(["Test"])


class TestScalewayModelSelection:
    """Tests for model listing and info retrieval."""

    def test_list_models_returns_all_models(self):
        """Test list_models returns complete model catalog."""
        models = ScalewayProvider.list_models()

        assert isinstance(models, dict)
        assert len(models) > 0

        # Check for specific models mentioned in requirements
        assert "llama-3.1-8b-instruct" in models
        assert "llama-3.3-70b-instruct" in models
        assert "mistral-small-3.2-24b-instruct-2506" in models
        assert "qwen3-235b-a22b-instruct-2507" in models

    def test_list_chat_models(self):
        """Test list_chat_models returns only chat-capable models."""
        chat_models = ScalewayProvider.list_chat_models()

        assert isinstance(chat_models, list)
        assert len(chat_models) > 0
        assert "llama-3.1-8b-instruct" in chat_models
        assert "llama-3.3-70b-instruct" in chat_models
        assert "qwen3-235b-a22b-instruct-2507" in chat_models

        # Embedding-only models should not be in chat list
        assert "qwen3-embedding-8b" not in chat_models

    def test_list_vision_models(self):
        """Test list_vision_models returns only vision-capable models."""
        vision_models = ScalewayProvider.list_vision_models()

        assert isinstance(vision_models, list)
        assert len(vision_models) > 0
        assert "pixtral-12b-2409" in vision_models
        assert "mistral-small-3.2-24b-instruct-2506" in vision_models

        # Chat-only models should not be in vision list
        assert "llama-3.1-8b-instruct" not in vision_models

    def test_list_embedding_models(self):
        """Test list_embedding_models returns only embedding models."""
        embedding_models = ScalewayProvider.list_embedding_models()

        assert isinstance(embedding_models, list)
        assert len(embedding_models) >= 2
        assert "qwen3-embedding-8b" in embedding_models
        assert "bge-multilingual-gemma2" in embedding_models

        # Chat models should not be in embedding list
        assert "llama-3.1-8b-instruct" not in embedding_models

    def test_get_model_specifications_success(self):
        """Test get_model_specifications returns correct model specifications."""
        info = ScalewayProvider.get_model_specifications("llama-3.1-8b-instruct")

        assert isinstance(info, dict)
        assert info["id"] == "llama-3.1-8b-instruct"
        assert info["name"] == "Meta Llama 3.1 8B Instruct"
        assert "chat" in info["capabilities"]
        assert info["context_window"] == 128000
        assert info["max_output_tokens"] == 16384
        assert "Llama 3.1" in info["description"]

    def test_get_model_specifications_qwen(self):
        """Test get_model_specifications for Qwen 3 235B model."""
        info = ScalewayProvider.get_model_specifications("qwen3-235b-a22b-instruct-2507")

        assert info["id"] == "qwen3-235b-a22b-instruct-2507"
        assert info["name"] == "Qwen 3 235B A22B Instruct"
        assert "chat" in info["capabilities"]
        assert info["context_window"] == 250000  # Largest context window
        assert info["max_output_tokens"] == 8192

    def test_get_model_specifications_vision_model(self):
        """Test get_model_specifications for vision-capable model."""
        info = ScalewayProvider.get_model_specifications("pixtral-12b-2409")

        assert info["id"] == "pixtral-12b-2409"
        assert "vision" in info["capabilities"]
        assert "chat" in info["capabilities"]
        assert info["context_window"] == 128000

    def test_get_model_specifications_embedding_model(self):
        """Test get_model_specifications for embedding model."""
        info = ScalewayProvider.get_model_specifications("qwen3-embedding-8b")

        assert info["id"] == "qwen3-embedding-8b"
        assert "embeddings" in info["capabilities"]
        assert info["context_window"] == 32000
        assert info["max_output_tokens"] == 0  # Embeddings don't have output tokens

    def test_get_model_specifications_invalid_model(self):
        """Test get_model_specifications raises ValueError for unknown model."""
        with pytest.raises(ValueError, match="Model 'invalid-model' not found"):
            ScalewayProvider.get_model_specifications("invalid-model")

    def test_instance_get_model_info(self):
        """Test instance method get_model_info returns current model info."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="llama-3.3-70b-instruct"
        )

        info = provider.get_model_info()
        assert info is not None
        assert info.id == "llama-3.3-70b-instruct"
        assert info.context_window == 100000

    def test_get_context_window(self):
        """Test get_context_window returns correct value."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="qwen3-235b-a22b-instruct-2507"
        )

        assert provider.get_context_window() == 250000

    def test_get_max_output_tokens(self):
        """Test get_max_output_tokens returns correct value."""
        provider = ScalewayProvider(
            api_key="test_key",
            model="llama-3.1-8b-instruct"
        )

        assert provider.get_max_output_tokens() == 16384


class TestScalewayModelCatalog:
    """Tests for model catalog data integrity."""

    def test_all_required_models_present(self):
        """Test that all models specified in requirements are present."""
        required_models = [
            "llama-3.1-8b-instruct",
            "llama-3.3-70b-instruct",
            "mistral-small-3.2-24b-instruct-2506",
            "qwen3-235b-a22b-instruct-2507",
        ]

        for model_id in required_models:
            assert model_id in SCALEWAY_MODELS, f"Model {model_id} not found"

    def test_model_specifications_complete(self):
        """Test that all models have complete specifications."""
        for model_id, model in SCALEWAY_MODELS.items():
            assert model.id == model_id
            assert len(model.name) > 0
            assert len(model.capabilities) > 0
            assert model.context_window >= 0
            assert model.max_output_tokens >= 0
            # Description can be empty but should be a string
            assert isinstance(model.description, str)

    def test_chat_models_have_positive_context_window(self):
        """Test that chat models have positive context windows."""
        chat_models = get_chat_models()

        for model_id in chat_models:
            model = SCALEWAY_MODELS[model_id]
            assert model.context_window > 0, f"{model_id} has invalid context window"

    def test_embedding_models_have_embedding_capability(self):
        """Test that all embedding models have the embeddings capability."""
        embedding_models = get_embedding_models()

        for model_id in embedding_models:
            model = SCALEWAY_MODELS[model_id]
            assert ModelCapability.EMBEDDINGS in model.capabilities

    def test_vision_models_have_vision_capability(self):
        """Test that all vision models have the vision capability."""
        vision_models = get_vision_models()

        for model_id in vision_models:
            model = SCALEWAY_MODELS[model_id]
            assert ModelCapability.VISION in model.capabilities


class TestScalewayProviderErrorHandling:
    """Additional error handling tests."""

    def test_init_with_unknown_model_logs_warning(self, caplog):
        """Test that initializing with unknown model logs warning."""
        import logging

        with caplog.at_level(logging.WARNING):
            provider = ScalewayProvider(
                api_key="test_key",
                model="unknown-model-xyz"
            )

            assert provider.model == "unknown-model-xyz"
            assert "not in known models list" in caplog.text

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_empty_choices_in_response(self, mock_client_class):
        """Test handling of response with empty choices array."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [],  # Empty choices
            "usage": {"prompt_tokens": 5, "completion_tokens": 0}
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        provider = ScalewayProvider(api_key="test_key")

        with pytest.raises(ProviderAPIError, match="Invalid response"):
            await provider.generate("Test")
