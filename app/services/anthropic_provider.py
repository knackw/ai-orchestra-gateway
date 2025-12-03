"""
Anthropic provider implementation for Claude API.

Provides integration with Anthropic's Claude models via direct HTTP API calls.
"""

import logging
from typing import Tuple

import httpx

from app.core.config import settings
from app.services.ai_gateway import AIProvider, ProviderAPIError

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """
    Anthropic Claude API provider implementation.

    Uses httpx async client to make direct API calls to Anthropic's
    Claude models.
    """

    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_MAX_TOKENS = 1024

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        max_tokens: int = None,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (defaults to config)
            model: Claude model to use (defaults to claude-3-5-sonnet)
            max_tokens: Max tokens in response (defaults to 1024)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in config")

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "anthropic"

    async def generate(self, prompt: str) -> Tuple[str, int]:
        """
        Generate AI response using Claude API.

        Args:
            prompt: User input prompt

        Returns:
            Tuple of (response_text, total_tokens)

        Raises:
            ProviderAPIError: If API call fails
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Calling Anthropic API with model {self.model}"
                )
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )

                # Handle HTTP errors
                if response.status_code == 401:
                    logger.error("Anthropic API authentication failed")
                    raise ProviderAPIError(
                        "Authentication failed: Invalid API key"
                    )
                elif response.status_code == 429:
                    logger.warning("Anthropic API rate limit exceeded")
                    raise ProviderAPIError(
                        "Rate limit exceeded. Please try again later."
                    )
                elif response.status_code >= 500:
                    logger.error(
                        f"Anthropic API server error: {response.status_code}"
                    )
                    raise ProviderAPIError(
                        f"Anthropic API server error: {response.status_code}"
                    )

                response.raise_for_status()

                # Parse response
                data = response.json()
                text = self._extract_text(data)
                tokens = self._count_tokens(data)

                logger.info(
                    f"Successfully generated response with {tokens} tokens"
                )
                return text, tokens

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Anthropic API: {e}")
            raise ProviderAPIError(
                f"Anthropic API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error calling Anthropic API: {e}")
            raise ProviderAPIError(
                f"Network error connecting to Anthropic: {str(e)}"
            ) from e
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing Anthropic API response: {e}")
            raise ProviderAPIError(
                f"Invalid response from Anthropic API: {str(e)}"
            ) from e

    def _extract_text(self, response_data: dict) -> str:
        """
        Extract text content from API response.

        Args:
            response_data: Parsed JSON response from API

        Returns:
            Extracted text content

        Raises:
            KeyError: If response format is unexpected
        """
        # Response format: {"content": [{"type": "text", "text": "..."}]}
        content_blocks = response_data["content"]
        if not content_blocks:
            raise ValueError("No content blocks in response")

        # Get first text block
        text_block = content_blocks[0]
        if text_block.get("type") != "text":
            raise ValueError(
                f"Unexpected content type: {text_block.get('type')}"
            )

        return text_block["text"]

    def _count_tokens(self, response_data: dict) -> int:
        """
        Count total tokens from API response.

        Args:
            response_data: Parsed JSON response from API

        Returns:
            Total tokens (input + output)

        Raises:
            KeyError: If usage data is missing
        """
        # Response format: {"usage": {"input_tokens": X, "output_tokens": Y}}
        usage = response_data["usage"]
        input_tokens = usage["input_tokens"]
        output_tokens = usage["output_tokens"]

        total = input_tokens + output_tokens
        logger.debug(
            f"Token usage: {input_tokens} input + "
            f"{output_tokens} output = {total} total"
        )
        return total
