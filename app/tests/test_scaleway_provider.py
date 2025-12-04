"""
Unit tests for ScalewayProvider.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.scaleway_provider import ScalewayProvider
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
