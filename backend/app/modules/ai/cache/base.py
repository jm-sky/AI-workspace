"""Abstract cache interface."""

from abc import ABC, abstractmethod
from typing import Any


class CacheService(ABC):
    """Abstract cache service interface."""

    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None:
        """Get cached value by key.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: dict[str, Any], ttl_days: int) -> None:
        """Set cached value with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_days: Time to live in days
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete cached value.

        Args:
            key: Cache key
        """
        pass

    @abstractmethod
    async def clear_expired(self) -> int:
        """Clear expired cache entries.

        Returns:
            Number of entries cleared
        """
        pass
