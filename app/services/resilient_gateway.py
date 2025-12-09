"""
Resilient AI Gateway with Failover and Retry Logic.

Provides:
- Primary/Secondary provider failover
- Exponential backoff retry logic
- Circuit breaker pattern (optional)
- Provider health tracking
"""

import logging
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from app.services.ai_gateway import (
    AIProvider,
    ProviderRegistry,
    ProviderAPIError,
    ProviderNotFoundError,
    get_registry,
)

logger = logging.getLogger(__name__)


class ProviderHealth(Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ProviderStatus:
    """Tracks provider health and failure statistics."""
    name: str
    consecutive_failures: int = 0
    total_failures: int = 0
    total_successes: int = 0
    last_failure_time: datetime | None = None
    last_success_time: datetime | None = None
    circuit_open_until: datetime | None = None

    @property
    def health(self) -> ProviderHealth:
        """Determine provider health based on failure history."""
        if self.circuit_open_until and datetime.now() < self.circuit_open_until:
            return ProviderHealth.UNHEALTHY
        if self.consecutive_failures >= 5:
            return ProviderHealth.UNHEALTHY
        if self.consecutive_failures >= 2:
            return ProviderHealth.DEGRADED
        return ProviderHealth.HEALTHY

    def record_success(self) -> None:
        """Record a successful call."""
        self.consecutive_failures = 0
        self.total_successes += 1
        self.last_success_time = datetime.now()
        self.circuit_open_until = None

    def record_failure(self) -> None:
        """Record a failed call."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failure_time = datetime.now()

        # Open circuit breaker after 5 consecutive failures
        if self.consecutive_failures >= 5:
            self.circuit_open_until = datetime.now() + timedelta(minutes=5)
            logger.warning(
                f"Circuit breaker OPEN for provider '{self.name}' "
                f"until {self.circuit_open_until}"
            )


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 30.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class FailoverConfig:
    """Configuration for provider failover."""
    primary_provider: str = "anthropic"
    secondary_provider: str = "scaleway"
    enable_failover: bool = True
    retry_primary_first: bool = True


class ResilientAIGateway:
    """
    AI Gateway with built-in resilience features.

    Features:
    - Automatic retry with exponential backoff
    - Provider failover (primary → secondary)
    - Circuit breaker pattern
    - Health tracking per provider
    """

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        retry_config: RetryConfig | None = None,
        failover_config: FailoverConfig | None = None,
    ):
        """
        Initialize resilient gateway.

        Args:
            registry: Provider registry (uses global if not provided)
            retry_config: Retry behavior configuration
            failover_config: Failover behavior configuration
        """
        self.registry = registry or get_registry()
        self.retry_config = retry_config or RetryConfig()
        self.failover_config = failover_config or FailoverConfig()
        self._provider_status: dict[str, ProviderStatus] = {}

    def _get_provider_status(self, name: str) -> ProviderStatus:
        """Get or create provider status tracker."""
        if name not in self._provider_status:
            self._provider_status[name] = ProviderStatus(name=name)
        return self._provider_status[name]

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt using exponential backoff.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = self.retry_config.initial_delay * (
            self.retry_config.exponential_base ** attempt
        )
        delay = min(delay, self.retry_config.max_delay)

        if self.retry_config.jitter:
            # Add random jitter (0-25% of delay)
            import random
            jitter = delay * random.uniform(0, 0.25)
            delay += jitter

        return delay

    async def _call_with_retry(
        self,
        provider: AIProvider,
        prompt: str,
    ) -> tuple[str, int]:
        """
        Call provider with retry logic.

        Args:
            provider: AI provider instance
            prompt: User prompt

        Returns:
            Tuple of (response_text, token_count)

        Raises:
            ProviderAPIError: If all retries exhausted
        """
        provider_name = provider.provider_name
        status = self._get_provider_status(provider_name)
        last_error: Exception | None = None

        for attempt in range(self.retry_config.max_retries):
            try:
                # Check circuit breaker
                if status.health == ProviderHealth.UNHEALTHY:
                    logger.warning(
                        f"Provider '{provider_name}' circuit is open, skipping"
                    )
                    raise ProviderAPIError(
                        f"Provider '{provider_name}' is temporarily unavailable"
                    )

                logger.info(
                    f"Calling provider '{provider_name}' "
                    f"(attempt {attempt + 1}/{self.retry_config.max_retries})"
                )

                result = await provider.generate(prompt)
                status.record_success()

                logger.info(
                    f"Provider '{provider_name}' succeeded on attempt {attempt + 1}"
                )
                return result

            except ProviderAPIError as e:
                last_error = e
                status.record_failure()

                # Check if we should retry
                if attempt < self.retry_config.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Provider '{provider_name}' failed on attempt {attempt + 1}, "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Provider '{provider_name}' failed after "
                        f"{self.retry_config.max_retries} attempts: {e}"
                    )

        raise last_error or ProviderAPIError("All retry attempts failed")

    async def generate(
        self,
        prompt: str,
        provider_name: str | None = None,
    ) -> tuple[str, int, str]:
        """
        Generate AI response with failover support.

        Args:
            prompt: User input prompt
            provider_name: Specific provider to use (overrides failover)

        Returns:
            Tuple of (response_text, token_count, provider_used)

        Raises:
            ProviderAPIError: If all providers fail
            ProviderNotFoundError: If specified provider not found
        """
        # If specific provider requested, use only that provider
        if provider_name:
            provider = self.registry.get(provider_name)
            response, tokens = await self._call_with_retry(provider, prompt)
            return response, tokens, provider_name

        # Use failover logic
        providers_to_try = []

        # Add primary provider
        if self.registry.has_provider(self.failover_config.primary_provider):
            providers_to_try.append(self.failover_config.primary_provider)

        # Add secondary provider if failover enabled
        if (
            self.failover_config.enable_failover
            and self.registry.has_provider(self.failover_config.secondary_provider)
        ):
            providers_to_try.append(self.failover_config.secondary_provider)

        if not providers_to_try:
            raise ProviderNotFoundError(
                f"No providers available. "
                f"Requested: {self.failover_config.primary_provider}, "
                f"{self.failover_config.secondary_provider}"
            )

        last_error: Exception | None = None

        for provider_name in providers_to_try:
            try:
                provider = self.registry.get(provider_name)
                response, tokens = await self._call_with_retry(provider, prompt)

                # Log if we used failover
                if provider_name != self.failover_config.primary_provider:
                    logger.info(
                        f"FAILOVER: Used secondary provider '{provider_name}'"
                    )

                return response, tokens, provider_name

            except ProviderAPIError as e:
                last_error = e
                logger.warning(
                    f"Provider '{provider_name}' failed, "
                    f"trying next provider: {e}"
                )
                continue

        # All providers failed
        logger.error(
            f"All providers failed. Last error: {last_error}"
        )
        raise last_error or ProviderAPIError("All providers failed")

    def get_provider_health(self) -> dict[str, dict]:
        """
        Get health status of all tracked providers.

        Returns:
            Dictionary with provider health information
        """
        result = {}
        for name, status in self._provider_status.items():
            result[name] = {
                "health": status.health.value,
                "consecutive_failures": status.consecutive_failures,
                "total_failures": status.total_failures,
                "total_successes": status.total_successes,
                "last_failure_time": (
                    status.last_failure_time.isoformat()
                    if status.last_failure_time else None
                ),
                "last_success_time": (
                    status.last_success_time.isoformat()
                    if status.last_success_time else None
                ),
                "circuit_open_until": (
                    status.circuit_open_until.isoformat()
                    if status.circuit_open_until else None
                ),
            }
        return result

    def reset_provider_status(self, provider_name: str | None = None) -> None:
        """
        Reset provider status/circuit breaker.

        Args:
            provider_name: Specific provider to reset, or None for all
        """
        if provider_name:
            if provider_name in self._provider_status:
                self._provider_status[provider_name] = ProviderStatus(
                    name=provider_name
                )
                logger.info(f"Reset status for provider '{provider_name}'")
        else:
            self._provider_status.clear()
            logger.info("Reset status for all providers")


# Global resilient gateway instance
_resilient_gateway: ResilientAIGateway | None = None


def get_resilient_gateway() -> ResilientAIGateway:
    """
    Get the global resilient gateway instance.

    Returns:
        Global ResilientAIGateway instance
    """
    global _resilient_gateway
    if _resilient_gateway is None:
        _resilient_gateway = ResilientAIGateway()
    return _resilient_gateway


def configure_resilient_gateway(
    retry_config: RetryConfig | None = None,
    failover_config: FailoverConfig | None = None,
) -> ResilientAIGateway:
    """
    Configure and return the global resilient gateway.

    Args:
        retry_config: Retry behavior configuration
        failover_config: Failover behavior configuration

    Returns:
        Configured ResilientAIGateway instance
    """
    global _resilient_gateway
    _resilient_gateway = ResilientAIGateway(
        retry_config=retry_config,
        failover_config=failover_config,
    )
    return _resilient_gateway
