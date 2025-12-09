"""
Claude via Google Vertex AI provider implementation.

Provides integration with Anthropic Claude models through Google Vertex AI,
enabling DSGVO-compliant Claude usage with EU data residency.

Region: europe-west3 (Frankfurt) for DSGVO compliance.
"""

import logging
from typing import Optional, AsyncIterator

from app.services.ai_gateway import ProviderAPIError, ProviderConfigError
from app.services.vertex_provider import (
    VertexAIProvider,
    VERTEX_CLAUDE_MODELS,
    get_vertex_model,
)

logger = logging.getLogger(__name__)


class VertexClaudeProvider(VertexAIProvider):
    """
    Claude provider via Google Vertex AI.

    Uses Anthropic's official anthropic[vertex] SDK to access Claude models
    through Google Cloud with EU data residency.

    DSGVO Compliance:
    - Region: europe-west3 (Frankfurt)
    - Data never leaves EU
    - Uses Google's Standard Contractual Clauses (SCCs)

    Supported Models:
    - claude-3-5-sonnet-v2@20241022 (recommended)
    - claude-3-5-sonnet@20240620
    - claude-3-opus@20240229
    - claude-3-sonnet@20240229
    - claude-3-haiku@20240307
    """

    DEFAULT_MODEL = "claude-3-5-sonnet-v2@20241022"
    DEFAULT_MAX_TOKENS = 1024

    def __init__(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        credentials_path: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize Claude via Vertex AI provider.

        Args:
            project_id: GCP project ID
            region: GCP region (defaults to europe-west3)
            credentials_path: Path to service account JSON
            model: Claude model to use
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            project_id=project_id,
            region=region,
            credentials_path=credentials_path,
        )

        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self._client = None

        # Validate model
        if self.model not in VERTEX_CLAUDE_MODELS:
            available = list(VERTEX_CLAUDE_MODELS.keys())
            raise ProviderConfigError(
                f"Model '{self.model}' is not a valid Claude model. "
                f"Available: {available}"
            )

        logger.info(
            f"Initialized Claude via Vertex AI: model={self.model}, "
            f"region={self.region}, project={self.project_id}"
        )

    def _get_client(self):
        """
        Get or create the AnthropicVertex client.

        Lazy initialization to avoid import errors if SDK not installed.
        """
        if self._client is None:
            try:
                from anthropic import AnthropicVertex
            except ImportError as e:
                raise ProviderConfigError(
                    "anthropic[vertex] package not installed. "
                    "Install with: pip install anthropic[vertex]"
                ) from e

            self._client = AnthropicVertex(
                region=self.region,
                project_id=self.project_id,
            )
            logger.debug(
                f"Created AnthropicVertex client for region={self.region}"
            )

        return self._client

    @property
    def provider_name(self) -> str:
        """Return provider name identifier."""
        return "vertex_claude"

    async def generate(self, prompt: str) -> tuple[str, int]:
        """
        Generate AI response using Claude via Vertex AI.

        Args:
            prompt: User input prompt

        Returns:
            Tuple of (response_text, total_tokens)

        Raises:
            ProviderAPIError: If API call fails
        """
        client = self._get_client()

        try:
            logger.info(
                f"Calling Claude via Vertex AI: model={self.model}, "
                f"region={self.region}"
            )

            # Use synchronous API wrapped in async context
            # AnthropicVertex uses sync calls internally
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract response
            text = self._extract_text(response)
            tokens = self._count_tokens(response)

            logger.info(
                f"Claude via Vertex AI response: {tokens} tokens used"
            )
            return text, tokens

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Claude via Vertex AI error: {error_msg}")

            # Handle specific error types
            if "authentication" in error_msg.lower() or "credentials" in error_msg.lower():
                raise ProviderAPIError(
                    "Authentication failed. Check GCP credentials and project ID."
                ) from e
            elif "rate" in error_msg.lower() or "quota" in error_msg.lower():
                raise ProviderAPIError(
                    "Rate limit or quota exceeded. Please try again later."
                ) from e
            elif "not found" in error_msg.lower():
                raise ProviderAPIError(
                    f"Model '{self.model}' not found in region '{self.region}'. "
                    f"Check model availability."
                ) from e
            else:
                raise ProviderAPIError(
                    f"Claude via Vertex AI error: {error_msg}"
                ) from e

    async def generate_with_vision(
        self,
        prompt: str,
        image_url: str,
    ) -> tuple[str, int]:
        """
        Generate AI response with image input.

        Args:
            prompt: User input prompt
            image_url: URL or base64 data URI of the image

        Returns:
            Tuple of (response_text, total_tokens)

        Raises:
            ProviderAPIError: If API call fails
        """
        client = self._get_client()

        model_info = get_vertex_model(self.model)
        if not model_info or not model_info.supports_vision:
            raise ProviderAPIError(
                f"Model '{self.model}' does not support vision input."
            )

        try:
            logger.info(
                f"Calling Claude Vision via Vertex AI: model={self.model}"
            )

            # Build content with image
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image",
                    "source": {
                        "type": "url" if image_url.startswith("http") else "base64",
                        "url": image_url if image_url.startswith("http") else None,
                        "media_type": "image/jpeg",
                        "data": image_url.split(",")[1] if "base64" in image_url else None,
                    }
                }
            ]

            # Handle URL vs base64
            if image_url.startswith("http"):
                content[1]["source"] = {
                    "type": "url",
                    "url": image_url,
                }
            else:
                # Assume base64 data URI format: data:image/jpeg;base64,/9j/4AAQ...
                parts = image_url.split(",")
                media_type = "image/jpeg"
                if ";" in parts[0]:
                    media_type = parts[0].split(":")[1].split(";")[0]
                content[1]["source"] = {
                    "type": "base64",
                    "media_type": media_type,
                    "data": parts[1] if len(parts) > 1 else image_url,
                }

            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": content}],
            )

            text = self._extract_text(response)
            tokens = self._count_tokens(response)

            logger.info(
                f"Claude Vision via Vertex AI response: {tokens} tokens"
            )
            return text, tokens

        except Exception as e:
            logger.error(f"Claude Vision via Vertex AI error: {e}")
            raise ProviderAPIError(
                f"Claude Vision via Vertex AI error: {str(e)}"
            ) from e

    async def generate_stream(
        self,
        prompt: str,
    ) -> AsyncIterator[str]:
        """
        Generate AI response with streaming.

        Args:
            prompt: User input prompt

        Yields:
            Text chunks as they are generated

        Raises:
            ProviderAPIError: If API call fails
        """
        client = self._get_client()

        try:
            logger.info(
                f"Streaming Claude via Vertex AI: model={self.model}"
            )

            with client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Claude streaming via Vertex AI error: {e}")
            raise ProviderAPIError(
                f"Claude streaming error: {str(e)}"
            ) from e

    def _extract_text(self, response) -> str:
        """
        Extract text content from Claude response.

        Args:
            response: Claude API response object

        Returns:
            Extracted text content
        """
        if not response.content:
            return ""

        # Claude response format: content is a list of content blocks
        text_blocks = [
            block.text for block in response.content
            if hasattr(block, "text")
        ]

        return "".join(text_blocks)

    def _count_tokens(self, response) -> int:
        """
        Count total tokens from Claude response.

        Args:
            response: Claude API response object

        Returns:
            Total tokens (input + output)
        """
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        total = input_tokens + output_tokens
        logger.debug(
            f"Token usage: {input_tokens} input + "
            f"{output_tokens} output = {total} total"
        )
        return total

    def get_model_info(self):
        """Get metadata for current model."""
        return get_vertex_model(self.model)

    def supports_vision(self) -> bool:
        """Check if current model supports vision."""
        model_info = self.get_model_info()
        return model_info.supports_vision if model_info else False

    @classmethod
    def list_models(cls) -> list[str]:
        """List available Claude models on Vertex AI."""
        return list(VERTEX_CLAUDE_MODELS.keys())
