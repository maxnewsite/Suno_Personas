"""
Caching service for reducing API costs.

Implements Redis-based caching for:
- Audio analysis results (same file = same features)
- Persona evaluations (same characteristics = similar responses)
"""

import hashlib
import json
from typing import Optional, Any
from redis import asyncio as aioredis
from app.config import settings


class CacheService:
    """Redis-based caching for expensive operations."""

    def __init__(self):
        self.enabled = settings.enable_caching
        self.ttl = settings.cache_ttl_seconds
        self.redis = None

    async def connect(self):
        """Connect to Redis."""
        if self.enabled:
            try:
                self.redis = await aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}")
                self.enabled = False

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    def _generate_key(self, prefix: str, data: dict) -> str:
        """Generate cache key from data."""
        # Sort dict for consistent hashing
        json_str = json.dumps(data, sort_keys=True)
        hash_value = hashlib.md5(json_str.encode()).hexdigest()
        return f"{prefix}:{hash_value}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.redis:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        if not self.enabled or not self.redis:
            return

        try:
            json_value = json.dumps(value)
            await self.redis.setex(
                key,
                ttl or self.ttl,
                json_value
            )
        except Exception as e:
            print(f"Cache set error: {e}")

    async def get_audio_features(self, file_hash: str) -> Optional[dict]:
        """Get cached audio features."""
        key = f"audio_features:{file_hash}"
        return await self.get(key)

    async def set_audio_features(self, file_hash: str, features: dict):
        """Cache audio features."""
        key = f"audio_features:{file_hash}"
        await self.set(key, features)

    async def get_persona_evaluation(
        self,
        persona_id: str,
        track_characteristics: dict
    ) -> Optional[dict]:
        """Get cached persona evaluation."""
        key = self._generate_key(
            f"persona:{persona_id}",
            track_characteristics
        )
        return await self.get(key)

    async def set_persona_evaluation(
        self,
        persona_id: str,
        track_characteristics: dict,
        evaluation: dict
    ):
        """Cache persona evaluation."""
        key = self._generate_key(
            f"persona:{persona_id}",
            track_characteristics
        )
        await self.set(key, evaluation)

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        if not self.enabled or not self.redis:
            return

        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(
                    cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            print(f"Cache invalidation error: {e}")


# Global cache instance
cache_service = CacheService()
