"""
AI Gateway service for the AI Legal Ops Gateway.

Provides abstract provider interface and registry pattern for managing
multiple AI providers (Anthropic, Scaleway, etc.) with consistent interface.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# Custom Exceptions
class ProviderError(Exception):
    """Base exception for AI provider errors."""

    pass


class ProviderNotFoundError(ProviderError):
    """Raised when requested provider is not found in registry."""

    pass


class ProviderAPIError(ProviderError):
    """Raised when AI provider API call fails."""

    pass


class ProviderConfigError(ProviderError):
    """Raised when provider configuration is invalid."""

    pass


# Abstract Provider Interface
class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All AI provider implementations must inherit from this class
    and implement the required methods.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the name of the provider.

        Returns:
            Provider name identifier (e.g., "anthropic", "scaleway")
        """
        pass

    @abstractmethod
    async def generate(self, prompt: str) -> tuple[str, int]:
        """
        Generate AI response for the given prompt.

        Args:
            prompt: User input prompt for the AI

        Returns:
            Tuple of (response_text, token_count)

        Raises:
            ProviderAPIError: If the API call fails
            ProviderConfigError: If provider is misconfigured
        """
        pass


# Provider Registry
class ProviderRegistry:
    """Registry for managing AI provider instances."""

    def __init__(self):
        """Initialize empty provider registry."""
        self._providers: dict[str, AIProvider] = {}

    def register(self, name: str, provider: AIProvider) -> None:
        """
        Register an AI provider.

        Args:
            name: Provider identifier (e.g., "anthropic")
            provider: AI provider instance

        Raises:
            ValueError: If provider with same name already registered
            TypeError: If provider doesn't implement AIProvider interface
        """
        if not isinstance(provider, AIProvider):
            raise TypeError(
                f"Provider must implement AIProvider interface, "
                f"got {type(provider).__name__}"
            )

        if name in self._providers:
            logger.warning(
                f"Provider '{name}' already registered. Overwriting."
            )

        self._providers[name] = provider
        logger.info(f"Registered AI provider: {name}")

    def get(self, name: str) -> AIProvider:
        """
        Retrieve AI provider by name.

        Args:
            name: Provider identifier

        Returns:
            AI provider instance

        Raises:
            ProviderNotFoundError: If provider not found
        """
        if name not in self._providers:
            raise ProviderNotFoundError(
                f"Provider '{name}' not found. "
                f"Available providers: {self.list_providers()}"
            )

        return self._providers[name]

    def list_providers(self) -> list[str]:
        """
        List all registered provider names.

        Returns:
            List of provider identifiers
        """
        return list(self._providers.keys())

    def has_provider(self, name: str) -> bool:
        """
        Check if provider is registered.

        Args:
            name: Provider identifier

        Returns:
            True if provider is registered, False otherwise
        """
        return name in self._providers

    def unregister(self, name: str) -> None:
        """
        Remove provider from registry.

        Args:
            name: Provider identifier

        Raises:
            ProviderNotFoundError: If provider not found
        """
        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider '{name}' not found")

        del self._providers[name]
        logger.info(f"Unregistered AI provider: {name}")


# Global registry instance
_global_registry = ProviderRegistry()


def get_registry() -> ProviderRegistry:
    """
    Get the global provider registry instance.

    Returns:
        Global ProviderRegistry instance
    """
    return _global_registry


# Gateway Manager
class AIGateway:
    """
    Facade for AI provider access and management.

    Provides high-level interface for interacting with AI providers
    through the registry.
    """

    def __init__(self, registry: ProviderRegistry | None = None):
        """
        Initialize AI Gateway.

        Args:
            registry: Provider registry (uses global if not provided)
        """
        self.registry = registry or get_registry()

    async def generate(
        self, prompt: str, provider_name: str = "anthropic"
    ) -> tuple[str, int]:
        """
        Generate AI response using specified provider.

        Args:
            prompt: User input prompt
            provider_name: Provider to use (default: "anthropic")

        Returns:
            Tuple of (response_text, token_count)

        Raises:
            ProviderNotFoundError: If provider not found
            ProviderAPIError: If API call fails
        """
        try:
            provider = self.registry.get(provider_name)
            logger.info(
                f"Generating response with provider: {provider_name}"
            )
            return await provider.generate(prompt)

        except ProviderNotFoundError:
            logger.error(
                f"Provider '{provider_name}' not found. "
                f"Available: {self.registry.list_providers()}"
            )
            raise

        except Exception as e:
            logger.error(
                f"Error generating response with {provider_name}: {e}"
            )
            raise ProviderAPIError(
                f"Failed to generate response: {str(e)}"
            ) from e

    def list_available_providers(self) -> list[str]:
        """
        List all available AI providers.

        Returns:
            List of provider names
        """
        return self.registry.list_providers()
