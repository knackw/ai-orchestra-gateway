"""
Response Caching Service for AI Gateway.

Provides Redis-based caching for AI responses to reduce API costs
and improve latency for repeated queries.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Cached AI response data."""
    content: str
    tokens_used: int
    provider: str
    cached_at: str
    hit_count: int = 0


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    ttl_seconds: int = 3600  # 1 hour default
    max_prompt_length: int = 10000  # Don't cache very long prompts
    redis_url: str = "redis://localhost:6379/0"
    key_prefix: str = "ai_cache:"


class CacheService:
    """
    Redis-based caching service for AI responses.

    Features:
    - Hash-based cache keys for prompt deduplication
    - Configurable TTL per entry
    - Cache hit/miss statistics
    - Tenant-aware caching
    """

    def __init__(self, config: CacheConfig | None = None):
        """
        Initialize cache service.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self._redis: "Redis | None" = None
        self._stats = {"hits": 0, "misses": 0}

    async def _get_redis(self) -> "Redis":
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = await aioredis.from_url(
                    self.config.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                logger.info("Redis cache connection established")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                raise
        return self._redis

    def _generate_cache_key(
        self,
        prompt: str,
        provider: str,
        tenant_id: str | None = None,
    ) -> str:
        """
        Generate cache key from prompt and provider.

        Uses SHA-256 hash to handle long prompts and normalize keys.

        Args:
            prompt: User prompt
            provider: AI provider name
            tenant_id: Optional tenant ID for tenant-specific caching

        Returns:
            Cache key string
        """
        # Normalize prompt (lowercase, strip whitespace)
        normalized = prompt.strip().lower()

        # Create hash of prompt + provider + tenant
        key_data = f"{normalized}:{provider}:{tenant_id or 'global'}"
        hash_value = hashlib.sha256(key_data.encode()).hexdigest()[:16]

        return f"{self.config.key_prefix}{hash_value}"

    async def get(
        self,
        prompt: str,
        provider: str,
        tenant_id: str | None = None,
    ) -> CachedResponse | None:
        """
        Get cached response for a prompt.

        Args:
            prompt: User prompt
            provider: AI provider name
            tenant_id: Optional tenant ID

        Returns:
            CachedResponse if found, None otherwise
        """
        if not self.config.enabled:
            return None

        # Skip caching for very long prompts
        if len(prompt) > self.config.max_prompt_length:
            logger.debug("Prompt too long for caching")
            return None

        try:
            redis = await self._get_redis()
            key = self._generate_cache_key(prompt, provider, tenant_id)

            data = await redis.get(key)
            if data:
                self._stats["hits"] += 1
                cached = json.loads(data)

                # Increment hit count
                cached["hit_count"] = cached.get("hit_count", 0) + 1
                await redis.set(
                    key,
                    json.dumps(cached),
                    ex=self.config.ttl_seconds,
                )

                logger.info(f"Cache HIT for key {key[:20]}... (hits: {cached['hit_count']})")
                return CachedResponse(**cached)
            else:
                self._stats["misses"] += 1
                logger.debug(f"Cache MISS for key {key[:20]}...")
                return None

        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    async def set(
        self,
        prompt: str,
        provider: str,
        content: str,
        tokens_used: int,
        tenant_id: str | None = None,
        ttl: int | None = None,
    ) -> bool:
        """
        Cache an AI response.

        Args:
            prompt: User prompt
            provider: AI provider name
            content: AI response content
            tokens_used: Number of tokens used
            tenant_id: Optional tenant ID
            ttl: Custom TTL in seconds

        Returns:
            True if cached successfully
        """
        if not self.config.enabled:
            return False

        # Skip caching for very long prompts
        if len(prompt) > self.config.max_prompt_length:
            return False

        try:
            from datetime import datetime

            redis = await self._get_redis()
            key = self._generate_cache_key(prompt, provider, tenant_id)

            cached = CachedResponse(
                content=content,
                tokens_used=tokens_used,
                provider=provider,
                cached_at=datetime.now().isoformat(),
                hit_count=0,
            )

            await redis.set(
                key,
                json.dumps(cached.__dict__),
                ex=ttl or self.config.ttl_seconds,
            )

            logger.info(f"Cached response for key {key[:20]}...")
            return True

        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False

    async def invalidate(
        self,
        prompt: str,
        provider: str,
        tenant_id: str | None = None,
    ) -> bool:
        """
        Invalidate a cached response.

        Args:
            prompt: User prompt
            provider: AI provider name
            tenant_id: Optional tenant ID

        Returns:
            True if invalidated successfully
        """
        try:
            redis = await self._get_redis()
            key = self._generate_cache_key(prompt, provider, tenant_id)
            await redis.delete(key)
            logger.info(f"Invalidated cache key {key[:20]}...")
            return True
        except Exception as e:
            logger.warning(f"Cache invalidate failed: {e}")
            return False

    async def clear_all(self) -> int:
        """
        Clear all cached responses.

        Returns:
            Number of keys deleted
        """
        try:
            redis = await self._get_redis()
            pattern = f"{self.config.key_prefix}*"
            keys = []
            async for key in redis.scan_iter(pattern):
                keys.append(key)

            if keys:
                await redis.delete(*keys)

            logger.info(f"Cleared {len(keys)} cache entries")
            return len(keys)
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
            return 0

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with hit/miss stats
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "total": total,
            "hit_rate_percent": round(hit_rate, 2),
        }

    async def health_check(self) -> bool:
        """
        Check if cache is healthy.

        Returns:
            True if Redis is reachable
        """
        try:
            redis = await self._get_redis()
            await redis.ping()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis connection closed")


# Global cache instance
_cache_service: CacheService | None = None


def get_cache_service() -> CacheService:
    """
    Get the global cache service instance.

    Returns:
        Global CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def configure_cache(config: CacheConfig) -> CacheService:
    """
    Configure and return the global cache service.

    Args:
        config: Cache configuration

    Returns:
        Configured CacheService instance
    """
    global _cache_service
    _cache_service = CacheService(config=config)
    return _cache_service
