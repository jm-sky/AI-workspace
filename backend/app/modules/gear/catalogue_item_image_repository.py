"""Database repository for catalogue item images."""

from typing import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.modules.gear.db_models import CatalogueItemImageDB


class CatalogueItemImageRepository:
    """Repository for catalogue item image operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def create(self, data: dict) -> CatalogueItemImageDB:
        """
        Create a new catalogue item image.

        Args:
            data: Image data dictionary

        Returns:
            Created image record
        """
        image = CatalogueItemImageDB(id=generate_id(), **data)
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def get_by_id(self, image_id: str) -> CatalogueItemImageDB | None:
        """
        Get image by ID.

        Args:
            image_id: Image ID

        Returns:
            Image record if found, None otherwise
        """
        stmt = select(CatalogueItemImageDB).where(CatalogueItemImageDB.id == image_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_catalogue_item(
        self, catalogue_item_id: str
    ) -> Sequence[CatalogueItemImageDB]:
        """
        Get all images for a catalogue item, ordered by order field.

        Args:
            catalogue_item_id: Catalogue item ID

        Returns:
            List of images
        """
        stmt = (
            select(CatalogueItemImageDB)
            .where(CatalogueItemImageDB.catalogue_item_id == catalogue_item_id)
            .order_by(CatalogueItemImageDB.order)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_by_catalogue_item(self, catalogue_item_id: str) -> int:
        """
        Count images for a catalogue item.

        Args:
            catalogue_item_id: Catalogue item ID

        Returns:
            Number of images
        """
        stmt = (
            select(func.count())
            .select_from(CatalogueItemImageDB)
            .where(CatalogueItemImageDB.catalogue_item_id == catalogue_item_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def update(self, image_id: str, data: dict) -> CatalogueItemImageDB | None:
        """
        Update image record.

        Args:
            image_id: Image ID
            data: Update data dictionary

        Returns:
            Updated image record if found, None otherwise
        """
        stmt = (
            update(CatalogueItemImageDB)
            .where(CatalogueItemImageDB.id == image_id)
            .values(**data)
            .returning(CatalogueItemImageDB)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, image_id: str) -> bool:
        """
        Delete image record.

        Args:
            image_id: Image ID

        Returns:
            True if deleted, False if not found
        """
        image = await self.get_by_id(image_id)
        if image:
            await self.db.delete(image)
            await self.db.commit()
            return True
        return False

    async def get_next_order(self, catalogue_item_id: str) -> int:
        """
        Get next order value for catalogue item images.

        Args:
            catalogue_item_id: Catalogue item ID

        Returns:
            Next order value
        """
        stmt = select(func.max(CatalogueItemImageDB.order)).where(
            CatalogueItemImageDB.catalogue_item_id == catalogue_item_id
        )
        result = await self.db.execute(stmt)
        max_order = result.scalar()
        return (max_order or -1) + 1

    async def unset_primary_for_catalogue_item(self, catalogue_item_id: str) -> None:
        """
        Unset primary flag for all images of a catalogue item.

        Args:
            catalogue_item_id: Catalogue item ID
        """
        stmt = (
            update(CatalogueItemImageDB)
            .where(CatalogueItemImageDB.catalogue_item_id == catalogue_item_id)
            .values(is_primary=False)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_primary_image(
        self, catalogue_item_id: str
    ) -> CatalogueItemImageDB | None:
        """
        Get primary image for a catalogue item.

        Args:
            catalogue_item_id: Catalogue item ID

        Returns:
            Primary image if found, None otherwise
        """
        stmt = select(CatalogueItemImageDB).where(
            CatalogueItemImageDB.catalogue_item_id == catalogue_item_id,
            CatalogueItemImageDB.is_primary == True,
        )  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_primary_images_by_catalogue_items(
        self, catalogue_item_ids: list[str]
    ) -> dict[str, CatalogueItemImageDB]:
        """
        Get primary images for multiple catalogue items in a single query.

        Args:
            catalogue_item_ids: List of catalogue item IDs

        Returns:
            Dictionary mapping catalogue_item_id to primary image (only items with primary images are included)
        """
        if not catalogue_item_ids:
            return {}
        stmt = select(CatalogueItemImageDB).where(
            CatalogueItemImageDB.catalogue_item_id.in_(catalogue_item_ids),
            CatalogueItemImageDB.is_primary == True,
        )  # noqa: E712
        result = await self.db.execute(stmt)
        images = result.scalars().all()
        return {img.catalogue_item_id: img for img in images}

    async def get_user_storage_usage(self, user_id: str) -> int:
        """
        Get total storage usage in bytes for a user's catalogue images.

        Args:
            user_id: User ID

        Returns:
            Total storage usage in bytes
        """
        stmt = select(func.sum(CatalogueItemImageDB.file_size)).where(
            CatalogueItemImageDB.user_id == user_id
        )
        result = await self.db.execute(stmt)
        total = result.scalar()
        return total or 0
