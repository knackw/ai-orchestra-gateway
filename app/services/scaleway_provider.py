"""
Scaleway AI provider implementation.

Provides integration with Scaleway Generative APIs supporting multiple LLM models,
including Chat, Vision, Audio, and Embeddings capabilities.
"""

import logging
from enum import Enum
from typing import Optional
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.services.ai_gateway import AIProvider, ProviderAPIError

logger = logging.getLogger(__name__)


class ModelCapability(Enum):
    """Scaleway model capabilities."""
    CHAT = "chat"
    VISION = "vision"
    AUDIO = "audio"
    EMBEDDINGS = "embeddings"
    TRANSCRIPTION = "transcription"


@dataclass
class ScalewayModel:
    """Scaleway model metadata."""
    id: str
    name: str
    capabilities: list[ModelCapability]
    context_window: int
    max_output_tokens: int
    description: str = ""


# Complete Scaleway model catalog (as of December 2025)
# Source: https://www.scaleway.com/en/docs/ai-data/generative-apis/reference-content/supported-models/
SCALEWAY_MODELS = {
    # ==========================================================================
    # Multimodal / Chat + Vision Models
    # ==========================================================================
    "gemma-3-27b-it": ScalewayModel(
        id="gemma-3-27b-it",
        name="Google Gemma 3 27B Instruct",
        capabilities=[ModelCapability.CHAT, ModelCapability.VISION],
        context_window=40000,  # 40k tokens
        max_output_tokens=8192,
        description="Google's open multimodal model (Preview). License: Gemma"
    ),
    "mistral-small-3.2-24b-instruct-2506": ScalewayModel(
        id="mistral-small-3.2-24b-instruct-2506",
        name="Mistral Small 3.2 24B Instruct",
        capabilities=[ModelCapability.CHAT, ModelCapability.VISION],
        context_window=128000,  # 128k tokens
        max_output_tokens=8192,
        description="Mistral's recommended multimodal model. License: Apache-2.0"
    ),
    "holo2-30b-a3b": ScalewayModel(
        id="holo2-30b-a3b",
        name="Holo2 30B A3B",
        capabilities=[ModelCapability.CHAT, ModelCapability.VISION],
        context_window=22000,  # 22k tokens
        max_output_tokens=8192,
        description="Advanced multimodal model. License: CC-BY-NC-4.0 (commercial use allowed via Scaleway)"
    ),

    # ==========================================================================
    # Chat + Audio Models
    # ==========================================================================
    "voxtral-small-24b-2507": ScalewayModel(
        id="voxtral-small-24b-2507",
        name="Voxtral Small 24B",
        capabilities=[ModelCapability.CHAT, ModelCapability.AUDIO, ModelCapability.TRANSCRIPTION],
        context_window=32000,  # 32k tokens
        max_output_tokens=8192,
        description="Mistral's audio model. Max 30min audio, 30s chunks, 25MB max. License: Apache-2.0"
    ),

    # ==========================================================================
    # Audio Transcription Models
    # ==========================================================================
    "whisper-large-v3": ScalewayModel(
        id="whisper-large-v3",
        name="OpenAI Whisper Large V3",
        capabilities=[ModelCapability.TRANSCRIPTION],
        context_window=0,  # Audio input, not text
        max_output_tokens=0,  # Returns transcription text
        description="OpenAI's speech recognition. 30s chunks, 25MB max. License: Apache-2.0"
    ),

    # ==========================================================================
    # Pure Chat Models
    # ==========================================================================
    "gpt-oss-120b": ScalewayModel(
        id="gpt-oss-120b",
        name="GPT-OSS 120B",
        capabilities=[ModelCapability.CHAT],
        context_window=128000,  # 128k tokens
        max_output_tokens=8192,
        description="Large open-source GPT-style model. License: Apache-2.0"
    ),
    "llama-3.3-70b-instruct": ScalewayModel(
        id="llama-3.3-70b-instruct",
        name="Meta Llama 3.3 70B Instruct",
        capabilities=[ModelCapability.CHAT],
        context_window=100000,  # 100k tokens
        max_output_tokens=4096,
        description="Meta's Llama 3.3. License: Llama 3.3 Community"
    ),
    "llama-3.1-8b-instruct": ScalewayModel(
        id="llama-3.1-8b-instruct",
        name="Meta Llama 3.1 8B Instruct",
        capabilities=[ModelCapability.CHAT],
        context_window=128000,  # 128k tokens
        max_output_tokens=16384,
        description="Efficient 8B model. License: Llama 3.1 Community"
    ),
    "mistral-nemo-instruct-2407": ScalewayModel(
        id="mistral-nemo-instruct-2407",
        name="Mistral Nemo Instruct",
        capabilities=[ModelCapability.CHAT],
        context_window=128000,  # 128k tokens
        max_output_tokens=8192,
        description="Mistral's Nemo series. License: Apache-2.0"
    ),
    "qwen3-235b-a22b-instruct-2507": ScalewayModel(
        id="qwen3-235b-a22b-instruct-2507",
        name="Qwen 3 235B A22B Instruct",
        capabilities=[ModelCapability.CHAT],
        context_window=250000,  # 250k tokens - largest context!
        max_output_tokens=8192,
        description="Alibaba's massive 235B model with 250k context. License: Apache-2.0"
    ),
    "qwen3-coder-30b-a3b-instruct": ScalewayModel(
        id="qwen3-coder-30b-a3b-instruct",
        name="Qwen 3 Coder 30B A3B Instruct",
        capabilities=[ModelCapability.CHAT],
        context_window=128000,  # 128k tokens
        max_output_tokens=8192,
        description="Alibaba's coding model. License: Apache-2.0"
    ),
    "deepseek-r1-distill-llama-70b": ScalewayModel(
        id="deepseek-r1-distill-llama-70b",
        name="DeepSeek R1 Distill Llama 70B",
        capabilities=[ModelCapability.CHAT],
        context_window=32000,  # 32k tokens
        max_output_tokens=4096,
        description="DeepSeek's reasoning model. License: MIT"
    ),

    # ==========================================================================
    # Vision Models
    # ==========================================================================
    "pixtral-12b-2409": ScalewayModel(
        id="pixtral-12b-2409",
        name="Pixtral 12B",
        capabilities=[ModelCapability.VISION, ModelCapability.CHAT],
        context_window=128000,  # 128k tokens
        max_output_tokens=4096,
        description="Mistral's vision model. Max 32M pixels (~8096x4048). License: Apache-2.0"
    ),

    # ==========================================================================
    # Embedding Models
    # ==========================================================================
    "qwen3-embedding-8b": ScalewayModel(
        id="qwen3-embedding-8b",
        name="Qwen 3 Embedding 8B",
        capabilities=[ModelCapability.EMBEDDINGS],
        context_window=32000,  # 32k tokens
        max_output_tokens=0,  # Returns embeddings (dim: 32-4096)
        description="Alibaba's embedding model. Dimensions: 32-4096. License: Apache-2.0"
    ),
    "bge-multilingual-gemma2": ScalewayModel(
        id="bge-multilingual-gemma2",
        name="BGE Multilingual Gemma2",
        capabilities=[ModelCapability.EMBEDDINGS],
        context_window=8192,  # 8k tokens
        max_output_tokens=0,  # Returns embeddings (dim: 3584 fixed)
        description="BAAI's multilingual embeddings. Dimension: 3584 fixed. License: Gemma"
    ),
}

# Backwards-compatible list for existing code
AVAILABLE_MODELS = list(SCALEWAY_MODELS.keys())


def get_models_by_capability(capability: ModelCapability) -> list[ScalewayModel]:
    """Get all models that support a specific capability."""
    return [
        model for model in SCALEWAY_MODELS.values()
        if capability in model.capabilities
    ]


def get_chat_models() -> list[str]:
    """Get all model IDs that support chat."""
    return [
        model_id for model_id, model in SCALEWAY_MODELS.items()
        if ModelCapability.CHAT in model.capabilities
    ]


def get_vision_models() -> list[str]:
    """Get all model IDs that support vision."""
    return [
        model_id for model_id, model in SCALEWAY_MODELS.items()
        if ModelCapability.VISION in model.capabilities
    ]


def get_embedding_models() -> list[str]:
    """Get all model IDs that support embeddings."""
    return [
        model_id for model_id, model in SCALEWAY_MODELS.items()
        if ModelCapability.EMBEDDINGS in model.capabilities
    ]


class ScalewayProvider(AIProvider):
    """
    Scaleway Generative APIs provider implementation.

    Supports multiple LLM models including Llama, Mistral, Qwen, and more.
    Now includes support for Chat, Vision, Audio, and Embeddings models.
    """

    API_URL = "https://api.scaleway.ai/v1/chat/completions"
    EMBEDDINGS_URL = "https://api.scaleway.ai/v1/embeddings"
    TRANSCRIPTION_URL = "https://api.scaleway.ai/v1/audio/transcriptions"
    DEFAULT_MODEL = "llama-3.1-8b-instruct"
    DEFAULT_MAX_TOKENS = 1024

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

        if self.model not in SCALEWAY_MODELS:
            logger.warning(
                f"Model '{self.model}' not in known models list. "
                f"Available: {', '.join(SCALEWAY_MODELS.keys())}"
            )

    def get_model_info(self) -> Optional[ScalewayModel]:
        """Get metadata for the current model."""
        return SCALEWAY_MODELS.get(self.model)

    def supports_vision(self) -> bool:
        """Check if current model supports vision/image input."""
        model_info = self.get_model_info()
        if model_info:
            return ModelCapability.VISION in model_info.capabilities
        return False

    def supports_audio(self) -> bool:
        """Check if current model supports audio input."""
        model_info = self.get_model_info()
        if model_info:
            return ModelCapability.AUDIO in model_info.capabilities
        return False

    def get_max_output_tokens(self) -> int:
        """Get the maximum output tokens for the current model."""
        model_info = self.get_model_info()
        if model_info and model_info.max_output_tokens > 0:
            return model_info.max_output_tokens
        return self.DEFAULT_MAX_TOKENS

    def get_context_window(self) -> int:
        """Get the context window size for the current model."""
        model_info = self.get_model_info()
        if model_info:
            return model_info.context_window
        return 0

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "scaleway"

    async def generate(self, prompt: str) -> tuple[str, int]:
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

    async def generate_with_image(
        self,
        prompt: str,
        image_url: str,
    ) -> tuple[str, int]:
        """
        Generate AI response with image input (vision models only).

        Args:
            prompt: User input prompt
            image_url: URL to the image or base64 data URI

        Returns:
            Tuple of (response_text, total_tokens)

        Raises:
            ProviderAPIError: If API call fails or model doesn't support vision
        """
        if not self.supports_vision():
            raise ProviderAPIError(
                f"Model '{self.model}' does not support vision. "
                f"Use one of: {', '.join(get_vision_models())}"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Vision API format with image content
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "max_tokens": self.max_tokens,
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Calling Scaleway Vision API with model {self.model}"
                )
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60.0,  # Vision requests may take longer
                )

                response.raise_for_status()

                data = response.json()
                text = self._extract_text(data)
                tokens = self._count_tokens(data)

                logger.info(
                    f"Successfully generated vision response with {tokens} tokens"
                )
                return text, tokens

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Scaleway Vision API: {e}")
            raise ProviderAPIError(
                f"Scaleway Vision API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error calling Scaleway Vision API: {e}")
            raise ProviderAPIError(
                f"Network error connecting to Scaleway: {str(e)}"
            ) from e

    async def create_embeddings(
        self,
        texts: list[str],
        model: str = None,
    ) -> list[list[float]]:
        """
        Create embeddings for the given texts.

        Args:
            texts: List of texts to embed
            model: Embedding model to use (defaults to qwen3-embedding-8b)

        Returns:
            List of embedding vectors

        Raises:
            ProviderAPIError: If API call fails
        """
        embedding_model = model or "qwen3-embedding-8b"

        if embedding_model not in get_embedding_models():
            raise ProviderAPIError(
                f"Model '{embedding_model}' is not an embedding model. "
                f"Use one of: {', '.join(get_embedding_models())}"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": embedding_model,
            "input": texts,
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Creating embeddings with model {embedding_model} "
                    f"for {len(texts)} texts"
                )
                response = await client.post(
                    self.EMBEDDINGS_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )

                response.raise_for_status()

                data = response.json()
                embeddings = [item["embedding"] for item in data["data"]]

                logger.info(
                    f"Successfully created {len(embeddings)} embeddings"
                )
                return embeddings

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Scaleway Embeddings API: {e}")
            raise ProviderAPIError(
                f"Scaleway Embeddings API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error calling Scaleway Embeddings API: {e}")
            raise ProviderAPIError(
                f"Network error connecting to Scaleway: {str(e)}"
            ) from e

    @classmethod
    def list_models(cls) -> dict[str, ScalewayModel]:
        """List all available Scaleway models with their metadata."""
        return SCALEWAY_MODELS.copy()

    @classmethod
    def list_chat_models(cls) -> list[str]:
        """List all models that support chat completion."""
        return get_chat_models()

    @classmethod
    def list_vision_models(cls) -> list[str]:
        """List all models that support vision/image input."""
        return get_vision_models()

    @classmethod
    def list_embedding_models(cls) -> list[str]:
        """List all embedding models."""
        return get_embedding_models()

    async def generate_with_vision(
        self,
        prompt: str,
        image_url: str,
    ) -> tuple[str, int]:
        """
        Generate AI response with image input (vision models only).
        Alias for generate_with_image() for API consistency.

        Args:
            prompt: User input prompt
            image_url: URL to the image or base64 data URI

        Returns:
            Tuple of (response_text, total_tokens)

        Raises:
            ProviderAPIError: If API call fails or model doesn't support vision
        """
        return await self.generate_with_image(prompt, image_url)

    async def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str = "audio.wav",
        model: str = None,
    ) -> tuple[str, int]:
        """
        Transcribe audio to text using Scaleway Whisper API.

        Args:
            audio_data: Audio file bytes
            filename: Name of audio file (e.g., "audio.wav", "recording.mp3")
            model: Transcription model (defaults to "whisper-large-v3")

        Returns:
            Tuple of (transcribed_text, estimated_tokens)

        Raises:
            ProviderAPIError: If API call fails
        """
        transcription_model = model or "whisper-large-v3"

        # Validate that model supports transcription
        if transcription_model not in SCALEWAY_MODELS:
            raise ProviderAPIError(
                f"Model '{transcription_model}' not found. "
                f"Available models: {', '.join(SCALEWAY_MODELS.keys())}"
            )

        model_info = SCALEWAY_MODELS[transcription_model]
        if ModelCapability.TRANSCRIPTION not in model_info.capabilities:
            raise ProviderAPIError(
                f"Model '{transcription_model}' does not support transcription. "
                f"Use one of: whisper-large-v3, voxtral-small-24b-2507"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        # Prepare multipart/form-data
        files = {
            "file": (filename, audio_data, "application/octet-stream"),
        }
        data = {
            "model": transcription_model,
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Calling Scaleway Transcription API with model {transcription_model}"
                )
                response = await client.post(
                    self.TRANSCRIPTION_URL,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=120.0,  # Audio transcription may take longer
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
                text = data.get("text", "")

                # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                estimated_tokens = max(len(text) // 4, 1)

                logger.info(
                    f"Successfully transcribed audio with ~{estimated_tokens} tokens"
                )
                return text, estimated_tokens

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Scaleway Transcription API: {e}")
            raise ProviderAPIError(
                f"Scaleway Transcription API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error calling Scaleway Transcription API: {e}")
            raise ProviderAPIError(
                f"Network error connecting to Scaleway: {str(e)}"
            ) from e
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing Scaleway API response: {e}")
            raise ProviderAPIError(
                f"Invalid response from Scaleway API: {str(e)}"
            ) from e

    @classmethod
    def get_model_specifications(cls, model_id: str) -> dict:
        """
        Get detailed specifications for a specific model.

        Args:
            model_id: The model identifier

        Returns:
            Dictionary with model specifications including:
            - id: Model identifier
            - name: Human-readable name
            - capabilities: List of supported capabilities (chat, vision, audio, embeddings)
            - context_window: Maximum context length in tokens
            - max_output_tokens: Maximum output tokens
            - description: Model description and license info

        Raises:
            ValueError: If model_id is not found
        """
        if model_id not in SCALEWAY_MODELS:
            available = ", ".join(SCALEWAY_MODELS.keys())
            raise ValueError(
                f"Model '{model_id}' not found. Available models: {available}"
            )

        model = SCALEWAY_MODELS[model_id]
        return {
            "id": model.id,
            "name": model.name,
            "capabilities": [cap.value for cap in model.capabilities],
            "context_window": model.context_window,
            "max_output_tokens": model.max_output_tokens,
            "description": model.description,
        }
