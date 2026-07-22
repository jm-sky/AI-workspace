"""Repository for feature limits operations."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.feature_limits.db_models import FeatureLimitDB


class FeatureLimitRepository:
    """Repository for feature limits operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    async def get_by_role(self, role: str) -> FeatureLimitDB | None:
        """Get limit by role.

        Args:
            role: User role

        Returns:
            Limit or None if not found
        """
        result = await self.db.execute(select(FeatureLimitDB).where(FeatureLimitDB.role == role))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[FeatureLimitDB]:
        """Get all limits.

        Returns:
            List of all limits
        """
        result = await self.db.execute(select(FeatureLimitDB).order_by(FeatureLimitDB.role))
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> FeatureLimitDB:
        """Create new limit.

        Args:
            **kwargs: Limit fields

        Returns:
            Created limit
        """
        limit = FeatureLimitDB(**kwargs)
        self.db.add(limit)
        await self.db.commit()
        await self.db.refresh(limit)
        return limit

    async def update(self, limit: FeatureLimitDB, **kwargs: Any) -> FeatureLimitDB:
        """Update existing limit.

        Args:
            limit: Limit to update
            **kwargs: Fields to update

        Returns:
            Updated limit
        """
        for key, value in kwargs.items():
            if hasattr(limit, key) and value is not None:
                setattr(limit, key, value)

        await self.db.commit()
        await self.db.refresh(limit)
        return limit

    async def delete(self, limit: FeatureLimitDB) -> None:
        """Delete limit.

        Args:
            limit: Limit to delete
        """
        await self.db.delete(limit)
        await self.db.commit()
