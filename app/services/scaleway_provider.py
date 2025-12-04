"""
Scaleway AI provider implementation.

Provides integration with Scaleway Generative APIs supporting multiple LLM models.
"""

import logging
from typing import Tuple

import httpx

from app.core.config import settings
from app.services.ai_gateway import AIProvider, ProviderAPIError

logger = logging.getLogger(__name__)


class ScalewayProvider(AIProvider):
    """
    Scaleway Generative APIs provider implementation.

    Supports multiple LLM models including Llama, Mistral, Qwen, and more.
    """

    API_URL = "https://api.scaleway.ai/v1/chat/completions"
    DEFAULT_MODEL = "llama-3.1-8b-instruct"
    DEFAULT_MAX_TOKENS = 1024

    # Available models
    AVAILABLE_MODELS = [
        "llama-3.3-70b-instruct",
        "llama-3.1-70b-instruct",
        "llama-3.1-8b-instruct",
        "mistral-nemo-instruct-2407",
        "mistral-7b-instruct-v0.3",
        "deepseek-r1-distill-llama-70b",
        "qwen3-235b-a22b-instruct-2507",
    ]

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        max_tokens: int = None,
    ):
        """
        Initialize Scaleway provider.

        Args:
            api_key: Scaleway API key (defaults to config)
            model: LLM model to use (defaults to llama-3.1-8b-instruct)
            max_tokens: Max tokens in response (defaults to 1024)
        """
        self.api_key = api_key or settings.SCALEWAY_API_KEY
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

        if not self.api_key:
            raise ValueError("SCALEWAY_API_KEY must be set in config")

        if self.model not in self.AVAILABLE_MODELS:
            logger.warning(
                f"Model '{self.model}' not in known models list. "
                f"Available: {', '.join(self.AVAILABLE_MODELS)}"
            )

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "scaleway"

    async def generate(self, prompt: str) -> Tuple[str, int]:
        """
        Generate AI response using Scaleway Generative APIs.

        Args:
            prompt: User input prompt

        Returns:
            Tuple of (response_text, total_tokens)

        Raises:
            ProviderAPIError: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Calling Scaleway API with model {self.model}"
                )
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )

                # Handle HTTP errors
                if response.status_code == 401:
                    logger.error("Scaleway API authentication failed")
                    raise ProviderAPIError(
                        "Authentication failed: Invalid API key"
                    )
                elif response.status_code == 429:
                    logger.warning("Scaleway API rate limit exceeded")
                    raise ProviderAPIError(
                        "Rate limit exceeded. Please try again later."
                    )
                elif response.status_code >= 500:
                    logger.error(
                        f"Scaleway API server error: {response.status_code}"
                    )
                    raise ProviderAPIError(
                        f"Scaleway API server error: {response.status_code}"
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
            logger.error(f"HTTP error calling Scaleway API: {e}")
            raise ProviderAPIError(
                f"Scaleway API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error calling Scaleway API: {e}")
            raise ProviderAPIError(
                f"Network error connecting to Scaleway: {str(e)}"
            ) from e
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing Scaleway API response: {e}")
            raise ProviderAPIError(
                f"Invalid response from Scaleway API: {str(e)}"
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
        # OpenAI-compatible format: {"choices": [{"message": {"content": "..."}}]}
        choices = response_data["choices"]
        if not choices:
            raise ValueError("No choices in response")

        message = choices[0]["message"]
        content = message["content"]

        return content

    def _count_tokens(self, response_data: dict) -> int:
        """
        Count total tokens from API response.

        Args:
            response_data: Parsed JSON response from API

        Returns:
            Total tokens (prompt + completion)

        Raises:
            KeyError: If usage data is missing
        """
        # OpenAI-compatible format: {"usage": {"prompt_tokens": X, "completion_tokens": Y}}
        usage = response_data["usage"]
        prompt_tokens = usage["prompt_tokens"]
        completion_tokens = usage["completion_tokens"]

        total = prompt_tokens + completion_tokens
        logger.debug(
            f"Token usage: {prompt_tokens} prompt + "
            f"{completion_tokens} completion = {total} total"
        )
        return total
