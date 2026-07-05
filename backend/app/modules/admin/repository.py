"""Database repository implementation for admin operations.

This module provides async repository for admin-level data access
to users, containers, and items across all users.
"""

import logging
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models import GearContainerDB, GearItemDB

logger = logging.getLogger(__name__)


class AdminRepository:
    """Repository for admin-level data access.

    Provides async database operations for admin users to access
    all users, containers, and items across the platform.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    # User operations
    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> list[tuple[UserDB, UserDB | None]]:
        """Get all users with their auth data.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tuples (UserDB, UserDB) - both refer to same user for consistency
        """
        stmt = (
            select(UserDB)
            .where(UserDB.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .order_by(UserDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        # Return tuple format for consistency with service expectations
        users_with_auth: list[tuple[UserDB, UserDB | None]] = [
            (user, user) for user in users
        ]

        return users_with_auth

    async def get_user_by_id(self, user_id: str) -> tuple[UserDB | None, UserDB | None]:
        """Get user by ID with auth data.

        Args:
            user_id: User ID

        Returns:
            Tuple of (UserDB, UserDB) or (None, None) if not found
        """
        # Get user
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return (None, None)

        return (user, user)

    # Container operations
    async def get_all_containers(
        self, skip: int = 0, limit: int = 100
    ) -> list[tuple[GearContainerDB, int]]:
        """Get all containers with item counts.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tuples (GearContainerDB, item_count)
        """
        stmt = (
            select(GearContainerDB, func.count(GearItemDB.id).label("item_count"))
            .outerjoin(GearItemDB, GearContainerDB.id == GearItemDB.container_id)
            .options(selectinload(GearContainerDB.user))  # type: ignore[attr-defined]
            .group_by(GearContainerDB.id)
            .offset(skip)
            .limit(limit)
            .order_by(GearContainerDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        rows = result.unique().all()
        # Convert to list for type checker
        return [(row[0], row[1]) for row in rows]

    async def get_container_by_id(self, container_id: str) -> GearContainerDB | None:
        """Get container by ID with items and user.

        Args:
            container_id: Container ID

        Returns:
            Container if found, None otherwise
        """
        stmt = select(GearContainerDB).where(GearContainerDB.id == container_id).options(selectinload(GearContainerDB.items), joinedload(GearContainerDB.user))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_container(
        self, container_id: str, data: dict
    ) -> GearContainerDB | None:
        """Update container by ID (admin only).

        Args:
            container_id: Container ID
            data: Update data dictionary

        Returns:
            Updated container if found, None otherwise
        """
        stmt = select(GearContainerDB).where(GearContainerDB.id == container_id).options(selectinload(GearContainerDB.items), joinedload(GearContainerDB.user))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        container_db = result.unique().scalar_one_or_none()

        if not container_db:
            return None

        # Update fields
        for key, value in data.items():
            if hasattr(container_db, key):
                setattr(container_db, key, value)

        await self.db.commit()
        await self.db.refresh(container_db)
        return container_db

    async def delete_container(self, container_id: str) -> bool:
        """Delete container by ID.

        Args:
            container_id: Container ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(GearContainerDB).where(GearContainerDB.id == container_id)
        result = await self.db.execute(stmt)
        container_db = result.scalar_one_or_none()

        if not container_db:
            return False

        await self.db.delete(container_db)
        await self.db.commit()
        return True

    # Item operations
    async def get_all_items(
        self, skip: int = 0, limit: int = 100
    ) -> list[tuple[GearItemDB, GearContainerDB, UserDB]]:
        """Get all items with container and user data.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tuples (GearItemDB, GearContainerDB, UserDB)
        """
        stmt = (
            select(GearItemDB, GearContainerDB, UserDB)
            .join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id)
            .join(UserDB, GearContainerDB.user_id == UserDB.id)
            .offset(skip)
            .limit(limit)
            .order_by(GearItemDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        # Convert rows to typed tuples
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def get_item_by_id(
        self, item_id: str
    ) -> tuple[GearItemDB | None, GearContainerDB | None, UserDB | None]:
        """Get item by ID with container and user data.

        Args:
            item_id: Item ID

        Returns:
            Tuple of (GearItemDB, GearContainerDB, UserDB) or (None, None, None)
        """
        stmt = (
            select(GearItemDB, GearContainerDB, UserDB)
            .join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id)
            .join(UserDB, GearContainerDB.user_id == UserDB.id)
            .where(GearItemDB.id == item_id)
        )
        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return (None, None, None)

        return tuple(row)

    async def delete_item(self, item_id: str) -> bool:
        """Delete item by ID.

        Args:
            item_id: Item ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(GearItemDB).where(GearItemDB.id == item_id)
        result = await self.db.execute(stmt)
        item_db = result.scalar_one_or_none()

        if not item_db:
            return False

        await self.db.delete(item_db)
        await self.db.commit()
        return True
