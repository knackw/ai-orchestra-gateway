"""
Unit tests for Response Caching Service.

Tests:
- Cache key generation
- Get/Set operations
- TTL handling
- Cache statistics
- Error handling
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.cache import (
    CacheService,
    CacheConfig,
    CachedResponse,
)


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_same_prompt_same_key(self):
        """Same prompt should generate same key."""
        cache = CacheService()
        key1 = cache._generate_cache_key("Hello world", "anthropic")
        key2 = cache._generate_cache_key("Hello world", "anthropic")
        assert key1 == key2

    def test_different_prompts_different_keys(self):
        """Different prompts should generate different keys."""
        cache = CacheService()
        key1 = cache._generate_cache_key("Hello world", "anthropic")
        key2 = cache._generate_cache_key("Goodbye world", "anthropic")
        assert key1 != key2

    def test_different_providers_different_keys(self):
        """Different providers should generate different keys."""
        cache = CacheService()
        key1 = cache._generate_cache_key("Hello", "anthropic")
        key2 = cache._generate_cache_key("Hello", "scaleway")
        assert key1 != key2

    def test_different_tenants_different_keys(self):
        """Different tenants should generate different keys."""
        cache = CacheService()
        key1 = cache._generate_cache_key("Hello", "anthropic", "tenant1")
        key2 = cache._generate_cache_key("Hello", "anthropic", "tenant2")
        assert key1 != key2

    def test_normalized_prompts(self):
        """Prompts should be normalized (case-insensitive, trimmed)."""
        cache = CacheService()
        key1 = cache._generate_cache_key("Hello World", "anthropic")
        key2 = cache._generate_cache_key("  hello world  ", "anthropic")
        assert key1 == key2

    def test_key_has_prefix(self):
        """Key should have configured prefix."""
        cache = CacheService(CacheConfig(key_prefix="test_cache:"))
        key = cache._generate_cache_key("Hello", "anthropic")
        assert key.startswith("test_cache:")


class TestCacheOperations:
    """Tests for cache get/set operations."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        redis = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        redis.set = AsyncMock(return_value=True)
        redis.delete = AsyncMock(return_value=1)
        redis.ping = AsyncMock(return_value=True)
        return redis

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, mock_redis):
        """Should return None on cache miss."""
        cache = CacheService()
        cache._redis = mock_redis
        mock_redis.get.return_value = None

        result = await cache.get("Hello", "anthropic")

        assert result is None
        assert cache._stats["misses"] == 1

    @pytest.mark.asyncio
    async def test_get_cache_hit(self, mock_redis):
        """Should return cached data on hit."""
        cache = CacheService()
        cache._redis = mock_redis

        cached_data = {
            "content": "Cached response",
            "tokens_used": 10,
            "provider": "anthropic",
            "cached_at": "2025-01-01T00:00:00",
            "hit_count": 5,
        }
        mock_redis.get.return_value = json.dumps(cached_data)

        result = await cache.get("Hello", "anthropic")

        assert result is not None
        assert result.content == "Cached response"
        assert result.tokens_used == 10
        assert cache._stats["hits"] == 1

    @pytest.mark.asyncio
    async def test_set_cache_entry(self, mock_redis):
        """Should store cache entry."""
        cache = CacheService()
        cache._redis = mock_redis

        result = await cache.set(
            prompt="Hello",
            provider="anthropic",
            content="Response",
            tokens_used=15,
        )

        assert result is True
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, mock_redis):
        """Should use custom TTL when provided."""
        cache = CacheService()
        cache._redis = mock_redis

        await cache.set(
            prompt="Hello",
            provider="anthropic",
            content="Response",
            tokens_used=15,
            ttl=7200,  # 2 hours
        )

        # Check that set was called with custom TTL
        call_args = mock_redis.set.call_args
        assert call_args.kwargs.get("ex") == 7200

    @pytest.mark.asyncio
    async def test_skip_long_prompts(self, mock_redis):
        """Should skip caching for very long prompts."""
        cache = CacheService(CacheConfig(max_prompt_length=100))
        cache._redis = mock_redis

        long_prompt = "x" * 200  # Exceeds max length

        # Get should return None
        result = await cache.get(long_prompt, "anthropic")
        assert result is None

        # Set should return False
        result = await cache.set(
            prompt=long_prompt,
            provider="anthropic",
            content="Response",
            tokens_used=10,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_cache_disabled(self):
        """Should skip operations when disabled."""
        cache = CacheService(CacheConfig(enabled=False))

        result = await cache.get("Hello", "anthropic")
        assert result is None

        result = await cache.set(
            prompt="Hello",
            provider="anthropic",
            content="Response",
            tokens_used=10,
        )
        assert result is False


class TestCacheInvalidation:
    """Tests for cache invalidation."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        redis = AsyncMock()
        redis.delete = AsyncMock(return_value=1)
        return redis

    @pytest.mark.asyncio
    async def test_invalidate_entry(self, mock_redis):
        """Should delete cache entry."""
        cache = CacheService()
        cache._redis = mock_redis

        result = await cache.invalidate("Hello", "anthropic")

        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_all(self, mock_redis):
        """Should clear all cache entries."""
        cache = CacheService()
        cache._redis = mock_redis

        # Mock scan_iter to return some keys
        async def mock_scan_iter(pattern):
            for key in ["ai_cache:abc", "ai_cache:def", "ai_cache:ghi"]:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete = AsyncMock(return_value=3)

        result = await cache.clear_all()

        assert result == 3


class TestCacheStatistics:
    """Tests for cache statistics."""

    def test_initial_stats(self):
        """Initial stats should be zero."""
        cache = CacheService()
        stats = cache.get_stats()

        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["total"] == 0
        assert stats["hit_rate_percent"] == 0

    @pytest.mark.asyncio
    async def test_hit_rate_calculation(self):
        """Hit rate should be calculated correctly."""
        cache = CacheService()
        cache._stats = {"hits": 75, "misses": 25}

        stats = cache.get_stats()

        assert stats["total"] == 100
        assert stats["hit_rate_percent"] == 75.0


class TestCacheHealthCheck:
    """Tests for cache health check."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Health check should return True when Redis is reachable."""
        cache = CacheService()
        cache._redis = AsyncMock()
        cache._redis.ping = AsyncMock(return_value=True)

        result = await cache.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Health check should return False when Redis is unreachable."""
        cache = CacheService()
        cache._redis = AsyncMock()
        cache._redis.ping = AsyncMock(side_effect=Exception("Connection refused"))

        result = await cache.health_check()
        assert result is False


class TestCacheErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_get_handles_redis_error(self):
        """Get should handle Redis errors gracefully."""
        cache = CacheService()
        cache._redis = AsyncMock()
        cache._redis.get = AsyncMock(side_effect=Exception("Redis error"))

        result = await cache.get("Hello", "anthropic")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_handles_redis_error(self):
        """Set should handle Redis errors gracefully."""
        cache = CacheService()
        cache._redis = AsyncMock()
        cache._redis.set = AsyncMock(side_effect=Exception("Redis error"))

        result = await cache.set(
            prompt="Hello",
            provider="anthropic",
            content="Response",
            tokens_used=10,
        )
        assert result is False


class TestCachedResponse:
    """Tests for CachedResponse dataclass."""

    def test_create_cached_response(self):
        """Should create CachedResponse with all fields."""
        response = CachedResponse(
            content="Test response",
            tokens_used=15,
            provider="anthropic",
            cached_at="2025-01-01T00:00:00",
            hit_count=3,
        )

        assert response.content == "Test response"
        assert response.tokens_used == 15
        assert response.provider == "anthropic"
        assert response.hit_count == 3

    def test_default_hit_count(self):
        """Default hit count should be 0."""
        response = CachedResponse(
            content="Test",
            tokens_used=10,
            provider="test",
            cached_at="2025-01-01",
        )
        assert response.hit_count == 0
