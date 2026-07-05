"""Repository for AI user settings."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.db_models import AIUserSettingsDB


class SettingsRepository:
    """Repository for AI user settings operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    async def get_by_user_id(self, user_id: str) -> AIUserSettingsDB | None:
        """Get settings by user ID.

        Args:
            user_id: User ID

        Returns:
            Settings or None if not found
        """
        result = await self.db.execute(
            select(AIUserSettingsDB).where(AIUserSettingsDB.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: str, **kwargs: Any) -> AIUserSettingsDB:
        """Create new settings.

        Args:
            user_id: User ID
            **kwargs: Additional settings fields

        Returns:
            Created settings
        """
        settings = AIUserSettingsDB(user_id=user_id, **kwargs)
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def update(
        self, settings: AIUserSettingsDB, **kwargs: Any
    ) -> AIUserSettingsDB:
        """Update existing settings.

        Args:
            settings: Settings to update
            **kwargs: Fields to update

        Returns:
            Updated settings
        """
        # Fields that can be explicitly set to None
        nullable_fields = {"encrypted_api_token"}

        for key, value in kwargs.items():
            if hasattr(settings, key):
                # Allow None for nullable fields, otherwise skip None values
                if value is not None or key in nullable_fields:
                    setattr(settings, key, value)

        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def get_or_create(self, user_id: str) -> AIUserSettingsDB:
        """Get existing settings or create new ones.

        Args:
            user_id: User ID

        Returns:
            User settings
        """
        settings = await self.get_by_user_id(user_id)
        if not settings:
            settings = await self.create(user_id=user_id)
        return settings
