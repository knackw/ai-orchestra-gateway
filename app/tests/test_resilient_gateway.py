"""
Unit tests for Resilient Gateway with Failover and Retry Logic.

Tests:
- Retry with exponential backoff
- Provider failover
- Circuit breaker pattern
- Provider health tracking
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.services.resilient_gateway import (
    ResilientAIGateway,
    RetryConfig,
    FailoverConfig,
    ProviderStatus,
    ProviderHealth,
)
from app.services.ai_gateway import (
    AIProvider,
    ProviderRegistry,
    ProviderAPIError,
    ProviderNotFoundError,
)


# Mock Provider for testing
class MockProvider(AIProvider):
    """Mock AI provider for testing."""

    def __init__(self, name: str, should_fail: bool = False, fail_times: int = 0):
        self._name = name
        self.should_fail = should_fail
        self.fail_times = fail_times
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return self._name

    async def generate(self, prompt: str) -> tuple[str, int]:
        self.call_count += 1
        if self.should_fail:
            raise ProviderAPIError(f"Mock error from {self._name}")
        if self.fail_times > 0:
            self.fail_times -= 1
            raise ProviderAPIError(f"Temporary error from {self._name}")
        return f"Response from {self._name}", 10


class TestProviderStatus:
    """Tests for ProviderStatus tracking."""

    def test_initial_health_is_healthy(self):
        """New provider should be healthy."""
        status = ProviderStatus(name="test")
        assert status.health == ProviderHealth.HEALTHY
        assert status.consecutive_failures == 0

    def test_record_success_resets_failures(self):
        """Success should reset consecutive failures."""
        status = ProviderStatus(name="test", consecutive_failures=3)
        status.record_success()
        assert status.consecutive_failures == 0
        assert status.total_successes == 1
        assert status.last_success_time is not None

    def test_record_failure_increments_count(self):
        """Failure should increment consecutive failures."""
        status = ProviderStatus(name="test")
        status.record_failure()
        assert status.consecutive_failures == 1
        assert status.total_failures == 1
        assert status.last_failure_time is not None

    def test_degraded_after_2_failures(self):
        """Provider should be degraded after 2 consecutive failures."""
        status = ProviderStatus(name="test")
        status.record_failure()
        status.record_failure()
        assert status.health == ProviderHealth.DEGRADED

    def test_unhealthy_after_5_failures(self):
        """Provider should be unhealthy after 5 consecutive failures."""
        status = ProviderStatus(name="test")
        for _ in range(5):
            status.record_failure()
        assert status.health == ProviderHealth.UNHEALTHY

    def test_circuit_breaker_opens_after_5_failures(self):
        """Circuit breaker should open after 5 consecutive failures."""
        status = ProviderStatus(name="test")
        for _ in range(5):
            status.record_failure()
        assert status.circuit_open_until is not None
        assert status.circuit_open_until > datetime.now()

    def test_success_closes_circuit_breaker(self):
        """Success should close circuit breaker."""
        status = ProviderStatus(name="test")
        status.circuit_open_until = datetime.now() + timedelta(minutes=5)
        status.record_success()
        assert status.circuit_open_until is None


class TestRetryLogic:
    """Tests for retry with exponential backoff."""

    @pytest.fixture
    def registry(self):
        """Create a test registry with mock providers."""
        registry = ProviderRegistry()
        return registry

    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self, registry):
        """Successful call should not trigger retry."""
        provider = MockProvider("test")
        registry.register("test", provider)

        gateway = ResilientAIGateway(
            registry=registry,
            failover_config=FailoverConfig(
                primary_provider="test",
                enable_failover=False,
            ),
        )

        response, tokens, provider_used = await gateway.generate("Hello")

        assert response == "Response from test"
        assert tokens == 10
        assert provider_used == "test"
        assert provider.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, registry):
        """Should retry on transient failure."""
        # Provider fails twice, then succeeds
        provider = MockProvider("test", fail_times=2)
        registry.register("test", provider)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(
                max_retries=3,
                initial_delay=0.01,  # Fast for tests
            ),
            failover_config=FailoverConfig(
                primary_provider="test",
                enable_failover=False,
            ),
        )

        response, tokens, provider_used = await gateway.generate("Hello")

        assert response == "Response from test"
        assert provider.call_count == 3  # 2 failures + 1 success

    @pytest.mark.asyncio
    async def test_max_retries_exhausted(self, registry):
        """Should raise error after max retries exhausted."""
        provider = MockProvider("test", should_fail=True)
        registry.register("test", provider)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(
                max_retries=3,
                initial_delay=0.01,
            ),
            failover_config=FailoverConfig(
                primary_provider="test",
                enable_failover=False,
            ),
        )

        with pytest.raises(ProviderAPIError):
            await gateway.generate("Hello")

        assert provider.call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff_delay(self):
        """Delay should increase exponentially."""
        gateway = ResilientAIGateway(
            retry_config=RetryConfig(
                initial_delay=1.0,
                exponential_base=2.0,
                max_delay=30.0,
                jitter=False,
            ),
        )

        assert gateway._calculate_delay(0) == 1.0
        assert gateway._calculate_delay(1) == 2.0
        assert gateway._calculate_delay(2) == 4.0
        assert gateway._calculate_delay(3) == 8.0

    @pytest.mark.asyncio
    async def test_max_delay_cap(self):
        """Delay should be capped at max_delay."""
        gateway = ResilientAIGateway(
            retry_config=RetryConfig(
                initial_delay=1.0,
                exponential_base=2.0,
                max_delay=10.0,
                jitter=False,
            ),
        )

        # 2^5 = 32 should be capped at 10
        assert gateway._calculate_delay(5) == 10.0


class TestFailoverLogic:
    """Tests for provider failover."""

    @pytest.fixture
    def registry(self):
        """Create a test registry with mock providers."""
        registry = ProviderRegistry()
        return registry

    @pytest.mark.asyncio
    async def test_primary_provider_used_first(self, registry):
        """Primary provider should be tried first."""
        primary = MockProvider("primary")
        secondary = MockProvider("secondary")
        registry.register("primary", primary)
        registry.register("secondary", secondary)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(max_retries=1, initial_delay=0.01),
            failover_config=FailoverConfig(
                primary_provider="primary",
                secondary_provider="secondary",
                enable_failover=True,
            ),
        )

        response, tokens, provider_used = await gateway.generate("Hello")

        assert provider_used == "primary"
        assert primary.call_count == 1
        assert secondary.call_count == 0

    @pytest.mark.asyncio
    async def test_failover_to_secondary(self, registry):
        """Should failover to secondary when primary fails."""
        primary = MockProvider("primary", should_fail=True)
        secondary = MockProvider("secondary")
        registry.register("primary", primary)
        registry.register("secondary", secondary)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(max_retries=1, initial_delay=0.01),
            failover_config=FailoverConfig(
                primary_provider="primary",
                secondary_provider="secondary",
                enable_failover=True,
            ),
        )

        response, tokens, provider_used = await gateway.generate("Hello")

        assert provider_used == "secondary"
        assert response == "Response from secondary"
        assert primary.call_count == 1
        assert secondary.call_count == 1

    @pytest.mark.asyncio
    async def test_no_failover_when_disabled(self, registry):
        """Should not failover when disabled."""
        primary = MockProvider("primary", should_fail=True)
        secondary = MockProvider("secondary")
        registry.register("primary", primary)
        registry.register("secondary", secondary)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(max_retries=1, initial_delay=0.01),
            failover_config=FailoverConfig(
                primary_provider="primary",
                secondary_provider="secondary",
                enable_failover=False,
            ),
        )

        with pytest.raises(ProviderAPIError):
            await gateway.generate("Hello")

        assert secondary.call_count == 0

    @pytest.mark.asyncio
    async def test_all_providers_fail(self, registry):
        """Should raise error when all providers fail."""
        primary = MockProvider("primary", should_fail=True)
        secondary = MockProvider("secondary", should_fail=True)
        registry.register("primary", primary)
        registry.register("secondary", secondary)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(max_retries=1, initial_delay=0.01),
            failover_config=FailoverConfig(
                primary_provider="primary",
                secondary_provider="secondary",
                enable_failover=True,
            ),
        )

        with pytest.raises(ProviderAPIError):
            await gateway.generate("Hello")

    @pytest.mark.asyncio
    async def test_specific_provider_no_failover(self, registry):
        """Specifying provider should bypass failover."""
        primary = MockProvider("primary", should_fail=True)
        secondary = MockProvider("secondary")
        registry.register("primary", primary)
        registry.register("secondary", secondary)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(max_retries=1, initial_delay=0.01),
            failover_config=FailoverConfig(
                primary_provider="primary",
                secondary_provider="secondary",
                enable_failover=True,
            ),
        )

        # Explicitly request primary - should not failover
        with pytest.raises(ProviderAPIError):
            await gateway.generate("Hello", provider_name="primary")

        assert secondary.call_count == 0


class TestCircuitBreaker:
    """Tests for circuit breaker pattern."""

    @pytest.fixture
    def registry(self):
        """Create a test registry with mock providers."""
        registry = ProviderRegistry()
        return registry

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self, registry):
        """Circuit should open after consecutive failures."""
        provider = MockProvider("test", should_fail=True)
        registry.register("test", provider)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(max_retries=5, initial_delay=0.001),
            failover_config=FailoverConfig(
                primary_provider="test",
                enable_failover=False,
            ),
        )

        with pytest.raises(ProviderAPIError):
            await gateway.generate("Hello")

        status = gateway._get_provider_status("test")
        assert status.health == ProviderHealth.UNHEALTHY
        assert status.circuit_open_until is not None

    @pytest.mark.asyncio
    async def test_circuit_blocks_requests(self, registry):
        """Open circuit should block requests immediately."""
        provider = MockProvider("test")
        registry.register("test", provider)

        gateway = ResilientAIGateway(
            registry=registry,
            retry_config=RetryConfig(max_retries=1, initial_delay=0.01),
            failover_config=FailoverConfig(
                primary_provider="test",
                enable_failover=False,
            ),
        )

        # Manually open circuit
        status = gateway._get_provider_status("test")
        status.circuit_open_until = datetime.now() + timedelta(minutes=5)
        status.consecutive_failures = 5

        with pytest.raises(ProviderAPIError) as exc_info:
            await gateway.generate("Hello")

        assert "temporarily unavailable" in str(exc_info.value)
        assert provider.call_count == 0  # Should not call provider


class TestHealthTracking:
    """Tests for provider health tracking."""

    @pytest.fixture
    def registry(self):
        """Create a test registry with mock providers."""
        registry = ProviderRegistry()
        return registry

    @pytest.mark.asyncio
    async def test_get_provider_health(self, registry):
        """Should return health status for tracked providers."""
        provider = MockProvider("test")
        registry.register("test", provider)

        gateway = ResilientAIGateway(
            registry=registry,
            failover_config=FailoverConfig(
                primary_provider="test",
                enable_failover=False,
            ),
        )

        await gateway.generate("Hello")

        health = gateway.get_provider_health()
        assert "test" in health
        assert health["test"]["health"] == "healthy"
        assert health["test"]["total_successes"] == 1
        assert health["test"]["consecutive_failures"] == 0

    def test_reset_provider_status(self, registry):
        """Should reset provider status."""
        gateway = ResilientAIGateway(registry=registry)

        # Create status with failures
        status = gateway._get_provider_status("test")
        status.consecutive_failures = 5
        status.circuit_open_until = datetime.now() + timedelta(minutes=5)

        gateway.reset_provider_status("test")

        new_status = gateway._get_provider_status("test")
        assert new_status.consecutive_failures == 0
        assert new_status.circuit_open_until is None

    def test_reset_all_providers(self, registry):
        """Should reset all provider statuses."""
        gateway = ResilientAIGateway(registry=registry)

        # Create statuses for multiple providers
        gateway._get_provider_status("provider1").consecutive_failures = 3
        gateway._get_provider_status("provider2").consecutive_failures = 5

        gateway.reset_provider_status()

        assert len(gateway._provider_status) == 0
