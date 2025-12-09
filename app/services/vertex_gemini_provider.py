"""
Google Gemini via Vertex AI provider implementation.

Provides integration with Google Gemini models through Vertex AI,
enabling DSGVO-compliant usage with EU data residency.

Region: europe-west3 (Frankfurt) for DSGVO compliance.
"""

import logging
from typing import Optional, AsyncIterator

from app.services.ai_gateway import ProviderAPIError, ProviderConfigError
from app.services.vertex_provider import (
    VertexAIProvider,
    VERTEX_GEMINI_MODELS,
    get_vertex_model,
)

logger = logging.getLogger(__name__)


class VertexGeminiProvider(VertexAIProvider):
    """
    Google Gemini provider via Vertex AI.

    Uses Google's official Vertex AI SDK to access Gemini models
    with EU data residency.

    DSGVO Compliance:
    - Region: europe-west3 (Frankfurt)
    - Data never leaves EU
    - Uses Google's Standard Contractual Clauses (SCCs)

    Supported Models:
    - gemini-2.0-flash-001 (fast and efficient)
    - gemini-1.5-pro-002 (2M context, most capable)
    - gemini-1.5-flash-002 (1M context, fast)
    """

    DEFAULT_MODEL = "gemini-1.5-flash-002"
    DEFAULT_MAX_TOKENS = 1024
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_TOP_P = 0.95

    def __init__(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        credentials_path: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ):
        """
        Initialize Gemini via Vertex AI provider.

        Args:
            project_id: GCP project ID
            region: GCP region (defaults to europe-west3)
            credentials_path: Path to service account JSON
            model: Gemini model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling parameter
        """
        super().__init__(
            project_id=project_id,
            region=region,
            credentials_path=credentials_path,
        )

        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self.temperature = temperature if temperature is not None else self.DEFAULT_TEMPERATURE
        self.top_p = top_p if top_p is not None else self.DEFAULT_TOP_P
        self._initialized = False
        self._model_instance = None

        # Validate model
        if self.model not in VERTEX_GEMINI_MODELS:
            available = list(VERTEX_GEMINI_MODELS.keys())
            raise ProviderConfigError(
                f"Model '{self.model}' is not a valid Gemini model. "
                f"Available: {available}"
            )

        # Validate temperature
        model_info = get_vertex_model(self.model)
        if model_info:
            min_temp, max_temp = model_info.temperature_range
            if not (min_temp <= self.temperature <= max_temp):
                logger.warning(
                    f"Temperature {self.temperature} outside recommended range "
                    f"[{min_temp}, {max_temp}] for model {self.model}"
                )

        logger.info(
            f"Initialized Gemini via Vertex AI: model={self.model}, "
            f"region={self.region}, project={self.project_id}"
        )

    def _initialize_vertex(self):
        """
        Initialize Vertex AI SDK.

        Lazy initialization to avoid import errors if SDK not installed.
        """
        if self._initialized:
            return

        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
        except ImportError as e:
            raise ProviderConfigError(
                "google-cloud-aiplatform package not installed. "
                "Install with: pip install google-cloud-aiplatform"
            ) from e

        # Initialize Vertex AI
        vertexai.init(
            project=self.project_id,
            location=self.region,
        )

        # Create model instance
        self._model_instance = GenerativeModel(self.model)
        self._initialized = True

        logger.debug(
            f"Initialized Vertex AI SDK for region={self.region}"
        )

    def _get_generation_config(self):
        """Create generation config for Gemini."""
        try:
            from vertexai.generative_models import GenerationConfig
        except ImportError:
            return {
                "max_output_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }

        return GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        )

    @property
    def provider_name(self) -> str:
        """Return provider name identifier."""
        return "vertex_gemini"

    async def generate(self, prompt: str) -> tuple[str, int]:
        """
        Generate AI response using Gemini via Vertex AI.

        Args:
            prompt: User input prompt

        Returns:
            Tuple of (response_text, total_tokens)

        Raises:
            ProviderAPIError: If API call fails
        """
        self._initialize_vertex()

        try:
            logger.info(
                f"Calling Gemini via Vertex AI: model={self.model}, "
                f"region={self.region}"
            )

            generation_config = self._get_generation_config()

            response = self._model_instance.generate_content(
                prompt,
                generation_config=generation_config,
            )

            # Extract response
            text = self._extract_text(response)
            tokens = self._count_tokens(response)

            logger.info(
                f"Gemini via Vertex AI response: {tokens} tokens used"
            )
            return text, tokens

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini via Vertex AI error: {error_msg}")

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
            elif "blocked" in error_msg.lower() or "safety" in error_msg.lower():
                raise ProviderAPIError(
                    "Content was blocked by safety filters."
                ) from e
            else:
                raise ProviderAPIError(
                    f"Gemini via Vertex AI error: {error_msg}"
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
        self._initialize_vertex()

        model_info = get_vertex_model(self.model)
        if not model_info or not model_info.supports_vision:
            raise ProviderAPIError(
                f"Model '{self.model}' does not support vision input."
            )

        try:
            from vertexai.generative_models import Part, Image
            import base64
            import httpx
        except ImportError as e:
            raise ProviderConfigError(
                "Required packages not installed for vision support."
            ) from e

        try:
            logger.info(
                f"Calling Gemini Vision via Vertex AI: model={self.model}"
            )

            # Build content parts
            parts = [prompt]

            if image_url.startswith("http"):
                # Download image from URL
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, timeout=30.0)
                    response.raise_for_status()
                    image_bytes = response.content

                # Determine MIME type
                content_type = response.headers.get("content-type", "image/jpeg")
                parts.append(Part.from_data(image_bytes, mime_type=content_type))

            else:
                # Assume base64 data URI format
                if "base64," in image_url:
                    header, data = image_url.split("base64,", 1)
                    mime_type = "image/jpeg"
                    if ":" in header and ";" in header:
                        mime_type = header.split(":")[1].split(";")[0]
                    image_bytes = base64.b64decode(data)
                else:
                    # Raw base64
                    image_bytes = base64.b64decode(image_url)
                    mime_type = "image/jpeg"

                parts.append(Part.from_data(image_bytes, mime_type=mime_type))

            generation_config = self._get_generation_config()

            response = self._model_instance.generate_content(
                parts,
                generation_config=generation_config,
            )

            text = self._extract_text(response)
            tokens = self._count_tokens(response)

            logger.info(
                f"Gemini Vision via Vertex AI response: {tokens} tokens"
            )
            return text, tokens

        except Exception as e:
            logger.error(f"Gemini Vision via Vertex AI error: {e}")
            raise ProviderAPIError(
                f"Gemini Vision via Vertex AI error: {str(e)}"
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
        self._initialize_vertex()

        try:
            logger.info(
                f"Streaming Gemini via Vertex AI: model={self.model}"
            )

            generation_config = self._get_generation_config()

            response = self._model_instance.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini streaming via Vertex AI error: {e}")
            raise ProviderAPIError(
                f"Gemini streaming error: {str(e)}"
            ) from e

    def _extract_text(self, response) -> str:
        """
        Extract text content from Gemini response.

        Args:
            response: Gemini API response object

        Returns:
            Extracted text content
        """
        try:
            # Handle potential blocked responses
            if not response.candidates:
                logger.warning("No candidates in Gemini response")
                return ""

            candidate = response.candidates[0]

            # Check for blocked content
            if hasattr(candidate, "finish_reason"):
                finish_reason = str(candidate.finish_reason)
                if "SAFETY" in finish_reason or "BLOCKED" in finish_reason:
                    logger.warning(f"Content blocked: {finish_reason}")
                    return "[Content blocked by safety filters]"

            return response.text

        except (AttributeError, IndexError) as e:
            logger.error(f"Error extracting text from Gemini response: {e}")
            return ""

    def _count_tokens(self, response) -> int:
        """
        Count total tokens from Gemini response.

        Args:
            response: Gemini API response object

        Returns:
            Total tokens (input + output)
        """
        try:
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count

            total = input_tokens + output_tokens
            logger.debug(
                f"Token usage: {input_tokens} input + "
                f"{output_tokens} output = {total} total"
            )
            return total

        except (AttributeError, TypeError) as e:
            logger.warning(f"Could not extract token count: {e}")
            # Estimate based on text length
            text = self._extract_text(response)
            estimated = len(text) // 4  # Rough estimate
            logger.debug(f"Estimated token count: {estimated}")
            return estimated

    def get_model_info(self):
        """Get metadata for current model."""
        return get_vertex_model(self.model)

    def supports_vision(self) -> bool:
        """Check if current model supports vision."""
        model_info = self.get_model_info()
        return model_info.supports_vision if model_info else False

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens for a given text without generating.

        Args:
            text: Text to count tokens for

        Returns:
            Token count
        """
        self._initialize_vertex()

        try:
            response = self._model_instance.count_tokens(text)
            return response.total_tokens
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            # Fallback to estimation
            return len(text) // 4

    @classmethod
    def list_models(cls) -> list[str]:
        """List available Gemini models on Vertex AI."""
        return list(VERTEX_GEMINI_MODELS.keys())
