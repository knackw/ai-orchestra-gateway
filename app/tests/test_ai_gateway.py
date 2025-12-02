"""
Unit tests for AI Gateway service.
"""

from typing import Tuple

import pytest

from app.services.ai_gateway import (
    AIGateway,
    AIProvider,
    ProviderAPIError,
    ProviderConfigError,
    ProviderError,
    ProviderNotFoundError,
    ProviderRegistry,
    get_registry,
)


# Mock Provider for Testing
class MockProvider(AIProvider):
    """Mock AI provider for testing."""

    def __init__(self, name: str = "mock", fail: bool = False):
        self._name = name
        self._fail = fail

    @property
    def provider_name(self) -> str:
        return self._name

    async def generate(self, prompt: str) -> Tuple[str, int]:
        if self._fail:
            raise Exception("Mock provider failure")
        return f"Response to: {prompt}", 42


class TestAIProviderInterface:
    """Tests for AIProvider abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that AIProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AIProvider()  # type: ignore

    def test_mock_provider_implements_interface(self):
        """Test that mock provider correctly implements interface."""
        provider = MockProvider("test")
        assert isinstance(provider, AIProvider)
        assert provider.provider_name == "test"

    @pytest.mark.asyncio
    async def test_mock_provider_generate(self):
        """Test mock provider generate method."""
        provider = MockProvider()
        response, tokens = await provider.generate("Hello")
        assert response == "Response to: Hello"
        assert tokens == 42


class TestProviderRegistry:
    """Tests for ProviderRegistry."""

    def test_registry_initialization(self):
        """Test registry initializes empty."""
        registry = ProviderRegistry()
        assert registry.list_providers() == []

    def test_register_provider(self):
        """Test registering a provider."""
        registry = ProviderRegistry()
        provider = MockProvider("test1")

        registry.register("test1", provider)

        assert "test1" in registry.list_providers()
        assert registry.has_provider("test1")

    def test_register_provider_invalid_type(self):
        """Test registering non-provider raises TypeError."""
        registry = ProviderRegistry()

        with pytest.raises(TypeError) as exc_info:
            registry.register("invalid", "not_a_provider")  # type: ignore

        assert "must implement AIProvider interface" in str(exc_info.value)

    def test_register_duplicate_provider_warns(self, caplog):
        """Test registering duplicate provider logs warning."""
        registry = ProviderRegistry()
        provider1 = MockProvider("test")
        provider2 = MockProvider("test")

        registry.register("test", provider1)
        registry.register("test", provider2)

        assert "already registered" in caplog.text
        assert len(registry.list_providers()) == 1

    def test_get_provider(self):
        """Test retrieving registered provider."""
        registry = ProviderRegistry()
        provider = MockProvider("test")
        registry.register("test", provider)

        retrieved = registry.get("test")

        assert retrieved is provider
        assert retrieved.provider_name == "test"

    def test_get_nonexistent_provider(self):
        """Test getting non-existent provider raises error."""
        registry = ProviderRegistry()

        with pytest.raises(ProviderNotFoundError) as exc_info:
            registry.get("nonexistent")

        assert "not found" in str(exc_info.value)
        assert "Available providers" in str(exc_info.value)

    def test_list_providers(self):
        """Test listing all providers."""
        registry = ProviderRegistry()
        provider1 = MockProvider("provider1")
        provider2 = MockProvider("provider2")

        registry.register("provider1", provider1)
        registry.register("provider2", provider2)

        providers = registry.list_providers()

        assert len(providers) == 2
        assert "provider1" in providers
        assert "provider2" in providers

    def test_has_provider(self):
        """Test checking provider existence."""
        registry = ProviderRegistry()
        provider = MockProvider("test")

        assert not registry.has_provider("test")

        registry.register("test", provider)

        assert registry.has_provider("test")
        assert not registry.has_provider("other")

    def test_unregister_provider(self):
        """Test unregistering a provider."""
        registry = ProviderRegistry()
        provider = MockProvider("test")
        registry.register("test", provider)

        assert registry.has_provider("test")

        registry.unregister("test")

        assert not registry.has_provider("test")

    def test_unregister_nonexistent_provider(self):
        """Test unregistering non-existent provider raises error."""
        registry = ProviderRegistry()

        with pytest.raises(ProviderNotFoundError):
            registry.unregister("nonexistent")


class TestGlobalRegistry:
    """Tests for global registry singleton."""

    def test_get_global_registry(self):
        """Test getting global registry instance."""
        registry1 = get_registry()
        registry2 = get_registry()

        # Should return same instance
        assert registry1 is registry2


class TestAIGateway:
    """Tests for AIGateway facade."""

    def test_gateway_initialization_default_registry(self):
        """Test gateway initializes with global registry by default."""
        gateway = AIGateway()
        assert gateway.registry is not None

    def test_gateway_initialization_custom_registry(self):
        """Test gateway with custom registry."""
        custom_registry = ProviderRegistry()
        gateway = AIGateway(registry=custom_registry)

        assert gateway.registry is custom_registry

    @pytest.mark.asyncio
    async def test_generate_with_default_provider(self):
        """Test generating response with default provider."""
        registry = ProviderRegistry()
        provider = MockProvider("anthropic")
        registry.register("anthropic", provider)

        gateway = AIGateway(registry=registry)

        response, tokens = await gateway.generate("Test prompt")

        assert response == "Response to: Test prompt"
        assert tokens == 42

    @pytest.mark.asyncio
    async def test_generate_with_specific_provider(self):
        """Test generating response with specific provider."""
        registry = ProviderRegistry()
        provider = MockProvider("custom")
        registry.register("custom", provider)

        gateway = AIGateway(registry=registry)

        response, tokens = await gateway.generate(
            "Test prompt", provider_name="custom"
        )

        assert response == "Response to: Test prompt"
        assert tokens == 42

    @pytest.mark.asyncio
    async def test_generate_provider_not_found(self):
        """Test generate with non-existent provider."""
        registry = ProviderRegistry()
        gateway = AIGateway(registry=registry)

        with pytest.raises(ProviderNotFoundError) as exc_info:
            await gateway.generate("Test", provider_name="nonexistent")

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_provider_api_error(self):
        """Test generate when provider API fails."""
        registry = ProviderRegistry()
        failing_provider = MockProvider("failing", fail=True)
        registry.register("failing", failing_provider)

        gateway = AIGateway(registry=registry)

        with pytest.raises(ProviderAPIError) as exc_info:
            await gateway.generate("Test", provider_name="failing")

        assert "Failed to generate response" in str(exc_info.value)

    def test_list_available_providers(self):
        """Test listing available providers through gateway."""
        registry = ProviderRegistry()
        provider1 = MockProvider("provider1")
        provider2 = MockProvider("provider2")
        registry.register("provider1", provider1)
        registry.register("provider2", provider2)

        gateway = AIGateway(registry=registry)
        providers = gateway.list_available_providers()

        assert len(providers) == 2
        assert "provider1" in providers
        assert "provider2" in providers


class TestCustomExceptions:
    """Tests for custom exception hierarchy."""

    def test_provider_error_is_base_exception(self):
        """Test that ProviderError is base exception class."""
        error = ProviderNotFoundError("test")
        assert isinstance(error, ProviderError)
        assert isinstance(error, Exception)

    def test_provider_not_found_error(self):
        """Test ProviderNotFoundError message."""
        error = ProviderNotFoundError("Provider 'test' not found")
        assert "test" in str(error)

    def test_provider_api_error(self):
        """Test ProviderAPIError message."""
        error = ProviderAPIError("API call failed")
        assert "API call failed" in str(error)

    def test_provider_config_error(self):
        """Test ProviderConfigError message."""
        error = ProviderConfigError("Invalid configuration")
        assert "Invalid configuration" in str(error)
