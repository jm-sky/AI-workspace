"""Database repository for gear settings."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id

from .db_models import GearSettingsDB


class GearSettingsRepository:
    """Repository for gear settings operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def get_by_user_id(self, user_id: str) -> GearSettingsDB | None:
        """Get gear settings by user ID.

        Args:
            user_id: User ID

        Returns:
            Gear settings or None if not found
        """
        result = await self.db.execute(select(GearSettingsDB).where(GearSettingsDB.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: str) -> GearSettingsDB:
        """Get or create gear settings for user.

        Args:
            user_id: User ID

        Returns:
            Gear settings (existing or newly created)
        """
        settings = await self.get_by_user_id(user_id)
        if settings is None:
            settings = GearSettingsDB(
                id=generate_id(),
                user_id=user_id,
                custom_categories=[],
                custom_container_types=[],
                custom_brands=[],
            )
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        return settings

    async def update(self, settings: GearSettingsDB) -> GearSettingsDB:
        """Update gear settings.

        Args:
            settings: Settings to update

        Returns:
            Updated settings
        """
        await self.db.commit()
        await self.db.refresh(settings)
        return settings
