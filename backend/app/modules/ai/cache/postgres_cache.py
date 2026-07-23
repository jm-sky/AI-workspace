"""PostgreSQL-based cache service for AI responses."""

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.ai.db_models import AICacheDB
from app.modules.ai.exceptions import CacheError


class PostgresCacheService:
    """PostgreSQL-based cache service.

    Provides caching for AI responses with TTL and hit counting.
    """

    def __init__(self, db: AsyncSession):
        """Initialize cache service.

        Args:
            db: Database session
        """
        self.db = db

    @staticmethod
    def generate_cache_key(operation_type: str, input_data: dict[str, Any], model: str) -> str:
        """Generate cache key from operation and input data.

        Args:
            operation_type: Type of operation ('chat', 'classify', etc.)
            input_data: Input data to hash
            model: Model identifier

        Returns:
            SHA-256 hash of the cache key (64 chars)
        """
        # Create deterministic string representation
        input_str = json.dumps(input_data, sort_keys=True)
        hash_input = f"{operation_type}:{input_str}:{model}"

        return hashlib.sha256(hash_input.encode()).hexdigest()

    async def get(self, key: str) -> dict[str, Any] | None:
        """Get cached data by key.

        Increments hit count and returns cached data if not expired.

        Args:
            key: Cache key

        Returns:
            Cached data dict or None if not found/expired
        """
        try:
            # Get cache entry
            result = await self.db.execute(select(AICacheDB).where(AICacheDB.cache_key == key))
            cache_entry = result.scalar_one_or_none()

            if not cache_entry:
                return None

            # Check expiration
            if cache_entry.expires_at < datetime.now(UTC):
                # Delete expired entry
                await self.db.delete(cache_entry)
                await self.db.commit()
                return None

            # Update hit count
            cache_entry.hit_count += 1
            await self.db.commit()

            return cache_entry.cached_data

        except Exception as e:
            raise CacheError(f"Cache get failed: {e}") from e

    async def set(self, key: str, value: dict[str, Any], ttl_days: int) -> None:
        """Set cached data with TTL.

        Uses upsert to handle key conflicts.

        Args:
            key: Cache key
            value: Data to cache
            ttl_days: Time to live in days
        """
        try:
            expires_at = datetime.now(UTC) + timedelta(days=ttl_days)

            # Upsert cache entry
            stmt = insert(AICacheDB).values(
                cache_key=key,
                operation_type=value.get("operation_type", "unknown"),
                model=value.get("model", "unknown"),
                cached_data=value,
                hit_count=0,
                created_at=datetime.now(UTC),
                expires_at=expires_at,
            )

            # On conflict, update cached_data and expires_at
            stmt = stmt.on_conflict_do_update(
                index_elements=["cache_key"],
                set_={"cached_data": value, "expires_at": expires_at, "hit_count": 0},
            )

            await self.db.execute(stmt)
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise CacheError(f"Cache set failed: {e}") from e

    async def delete(self, key: str) -> None:
        """Delete cached entry by key.

        Args:
            key: Cache key
        """
        try:
            await self.db.execute(delete(AICacheDB).where(AICacheDB.cache_key == key))
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise CacheError(f"Cache delete failed: {e}") from e

    async def clear_expired(self) -> int:
        """Clear all expired cache entries.

        Returns:
            Number of entries deleted
        """
        try:
            result = await self.db.execute(delete(AICacheDB).where(AICacheDB.expires_at < datetime.now(UTC)))
            await self.db.commit()
            return result.rowcount or 0  # type: ignore[attr-defined]

        except Exception as e:
            await self.db.rollback()
            raise CacheError(f"Clear expired failed: {e}") from e

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache statistics
        """
        try:
            # Total entries
            total_result = await self.db.execute(select(AICacheDB))
            total_entries = len(total_result.all())

            # Expired entries
            expired_result = await self.db.execute(select(AICacheDB).where(AICacheDB.expires_at < datetime.now(UTC)))
            expired_entries = len(expired_result.all())

            # Total hits
            from sqlalchemy import func

            hits_result = await self.db.execute(select(func.sum(AICacheDB.hit_count)))
            total_hits = hits_result.scalar() or 0

            return {
                "total_entries": total_entries,
                "active_entries": total_entries - expired_entries,
                "expired_entries": expired_entries,
                "total_hits": total_hits,
                "cache_enabled": settings.ai.cache_enabled,
            }

        except Exception as e:
            raise CacheError(f"Get cache stats failed: {e}") from e
