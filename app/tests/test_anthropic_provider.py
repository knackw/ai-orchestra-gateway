"""
Unit tests for Anthropic provider.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai_gateway import AIProvider, ProviderAPIError
from app.services.anthropic_provider import AnthropicProvider


class TestAnthropicProviderInitialization:
    """Tests for AnthropicProvider initialization."""

    def test_provider_inherits_from_ai_provider(self):
        """Test that AnthropicProvider implements AIProvider interface."""
        with patch("app.services.anthropic_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            provider = AnthropicProvider()
            assert isinstance(provider, AIProvider)

    def test_provider_name_property(self):
        """Test provider_name property returns 'anthropic'."""
        with patch("app.services.anthropic_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            provider = AnthropicProvider()
            assert provider.provider_name == "anthropic"

    def test_initialization_with_defaults(self):
        """Test initialization uses default values from settings."""
        with patch("app.services.anthropic_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-api-key"
            provider = AnthropicProvider()

            assert provider.api_key == "test-api-key"
            assert provider.model == AnthropicProvider.DEFAULT_MODEL
            assert provider.max_tokens == AnthropicProvider.DEFAULT_MAX_TOKENS

    def test_initialization_with_custom_values(self):
        """Test initialization with custom parameters."""
        provider = AnthropicProvider(
            api_key="custom-key",
            model="claude-3-opus-20240229",
            max_tokens=2048,
        )

        assert provider.api_key == "custom-key"
        assert provider.model == "claude-3-opus-20240229"
        assert provider.max_tokens == 2048

    def test_initialization_without_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with patch("app.services.anthropic_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None

            with pytest.raises(ValueError) as exc_info:
                AnthropicProvider()

            assert "ANTHROPIC_API_KEY must be set" in str(exc_info.value)


class TestAnthropicProviderGenerate:
    """Tests for generate method."""

    @pytest.mark.asyncio
    async def test_successful_generation(self):
        """Test successful API call and response parsing."""
        provider = AnthropicProvider(api_key="test-key")

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "Hello from Claude!"}],
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            text, tokens = await provider.generate("Hello")

            assert text == "Hello from Claude!"
            assert tokens == 15  # 10 input + 5 output

    @pytest.mark.asyncio
    async def test_request_format(self):
        """Test that request is formatted correctly."""
        provider = AnthropicProvider(
            api_key="test-key", model="claude-3-opus", max_tokens=512
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "Response"}],
            "usage": {"input_tokens": 5, "output_tokens": 3},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            await provider.generate("Test prompt")

            # Verify post was called with correct parameters
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args

            # Check URL
            assert call_args[0][0] == AnthropicProvider.API_URL

            # Check headers
            headers = call_args[1]["headers"]
            assert headers["x-api-key"] == "test-key"
            assert headers["anthropic-version"] == "2023-06-01"
            assert headers["content-type"] == "application/json"

            # Check payload
            payload = call_args[1]["json"]
            assert payload["model"] == "claude-3-opus"
            assert payload["max_tokens"] == 512
            assert payload["messages"] == [
                {"role": "user", "content": "Test prompt"}
            ]

    @pytest.mark.asyncio
    async def test_authentication_error_401(self):
        """Test handling of authentication error."""
        provider = AnthropicProvider(api_key="invalid-key")

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ProviderAPIError) as exc_info:
                await provider.generate("Test")

            assert "Invalid API key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_error_429(self):
        """Test handling of rate limit error."""
        provider = AnthropicProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 429

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ProviderAPIError) as exc_info:
                await provider.generate("Test")

            assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_server_error_500(self):
        """Test handling of server error."""
        provider = AnthropicProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ProviderAPIError) as exc_info:
                await provider.generate("Test")

            assert "server error: 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test handling of network error."""
        import httpx

        provider = AnthropicProvider(api_key="test-key")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.RequestError(
                "Connection refused"
            )
            mock_client_class.return_value = mock_client

            with pytest.raises(ProviderAPIError) as exc_info:
                await provider.generate("Test")

            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_response_format(self):
        """Test handling of invalid response format."""
        provider = AnthropicProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "invalid": "response"
            # Missing 'content' and 'usage' fields
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(ProviderAPIError) as exc_info:
                await provider.generate("Test")

            assert "Invalid response" in str(exc_info.value)


class TestAnthropicProviderResponseParsing:
    """Tests for response parsing methods."""

    def test_extract_text_success(self):
        """Test text extraction from valid response."""
        provider = AnthropicProvider(api_key="test-key")

        response_data = {
            "content": [{"type": "text", "text": "Test response"}]
        }

        text = provider._extract_text(response_data)
        assert text == "Test response"

    def test_extract_text_empty_content(self):
        """Test text extraction with empty content blocks."""
        provider = AnthropicProvider(api_key="test-key")

        response_data = {"content": []}

        with pytest.raises(ValueError) as exc_info:
            provider._extract_text(response_data)

        assert "No content blocks" in str(exc_info.value)

    def test_extract_text_wrong_type(self):
        """Test text extraction with non-text content type."""
        provider = AnthropicProvider(api_key="test-key")

        response_data = {
            "content": [{"type": "image", "data": "..."}]
        }

        with pytest.raises(ValueError) as exc_info:
            provider._extract_text(response_data)

        assert "Unexpected content type" in str(exc_info.value)

    def test_count_tokens_success(self):
        """Test token counting from valid response."""
        provider = AnthropicProvider(api_key="test-key")

        response_data = {
            "usage": {"input_tokens": 100, "output_tokens": 50}
        }

        tokens = provider._count_tokens(response_data)
        assert tokens == 150

    def test_count_tokens_missing_usage(self):
        """Test token counting with missing usage data."""
        provider = AnthropicProvider(api_key="test-key")

        response_data = {}

        with pytest.raises(KeyError):
            provider._count_tokens(response_data)


class TestAnthropicProviderIntegration:
    """Integration tests for Anthropic provider."""

    @pytest.mark.asyncio
    async def test_provider_can_be_registered(self):
        """Test that provider can be registered in gateway."""
        from app.services.ai_gateway import ProviderRegistry

        provider = AnthropicProvider(api_key="test-key")
        registry = ProviderRegistry()

        registry.register("anthropic", provider)

        assert registry.has_provider("anthropic")
        retrieved = registry.get("anthropic")
        assert retrieved is provider
