"""Database repository implementation for gear management.

This module provides async repository for managing gear containers and items
using SQLAlchemy 2.0+.
"""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypedDict

from sqlalchemy import and_, func, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.common.id_utils import generate_id
from app.common.search import SearchMixin

from .db_models import (
    ContainerRatingDB,
    ContainerShareTokenDB,
    ContentReportDB,
    GearContainerDB,
    GearItemDB,
    GlobalCatalogueItemDB,
    ItemPromotionDB,
)
from .schemas import (
    BatchOrderUpdateRequest,
    ContainerCreate,
    ContainerUpdate,
    GlobalCatalogueItemCreate,
    GlobalCatalogueItemUpdate,
    ItemCreate,
    ItemUpdate,
)

logger = logging.getLogger(__name__)


class GearRepository(SearchMixin):
    """Repository for gear containers and items.

    Provides async database operations for managing gear containers and items.
    Supports search across container names and item names.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
        # Configure SearchMixin for gear search
        self._search_columns = [GearContainerDB.name, GearItemDB.name]
        self._case_sensitive = False

    # Container operations
    async def create_container(self, user_id: str, data: ContainerCreate) -> GearContainerDB:
        """Create a new gear container.

        Args:
            user_id: Owner user ID
            data: Container creation data

        Returns:
            Created container
        """
        container = GearContainerDB(
            id=(data.id if data.id else generate_id()),  # Use provided UUID if available, otherwise generate new one
            user_id=user_id,
            name=data.name,
            description=data.description,
            type=data.type,
            color=data.color,
            parent_container_id=data.parentContainerId,
            brand=data.brand,
            price=data.price,
            hide_when_nested=data.hideWhenNested,
            weight=data.weight,
            weight_unit=data.weightUnit,
            max_weight=data.maxWeight,
            max_weight_unit=data.maxWeightUnit,
            url=data.url,
            is_public=data.isPublic if data.isPublic is not None else False,
            favorite=data.favorite if data.favorite is not None else False,
            show_item_images=(data.showItemImages if data.showItemImages is not None else False),
        )
        self.db.add(container)
        await self.db.commit()
        await self.db.refresh(container)
        # Reload container with items relationship to avoid lazy loading issues
        # For a newly created container, items will be empty, but we need to load the relationship
        stmt = select(GearContainerDB).where(GearContainerDB.id == container.id).options(selectinload(GearContainerDB.items))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        container = result.scalar_one()
        return container

    async def get_container(self, container_id: str, user_id: str) -> GearContainerDB | None:
        """Get a container by ID for a specific user.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            Container if found, None otherwise
        """
        stmt = (
            select(GearContainerDB)
            .where(
                and_(
                    GearContainerDB.id == container_id,
                    GearContainerDB.user_id == user_id,
                )
            )
            .options(selectinload(GearContainerDB.items))  # type: ignore[attr-defined]
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_containers(self, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[GearContainerDB]:
        """Get all containers for a user.

        Args:
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of containers
        """
        stmt = (
            select(GearContainerDB).where(GearContainerDB.user_id == user_id).options(selectinload(GearContainerDB.items)).offset(skip).limit(limit).order_by(GearContainerDB.favorite.desc(), GearContainerDB.created_at.desc())  # type: ignore[attr-defined]
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_user_containers(self, user_id: str) -> int:
        """Count all containers for a user.

        Args:
            user_id: Owner user ID

        Returns:
            Number of containers
        """
        stmt = select(func.count(GearContainerDB.id)).where(GearContainerDB.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def count_user_items(self, user_id: str) -> int:
        """Count all items for a user (across all containers).

        Args:
            user_id: Owner user ID

        Returns:
            Number of items
        """
        stmt = select(func.count(GearItemDB.id)).join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id).where(GearContainerDB.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def get_public_containers(self, skip: int = 0, limit: int = 100) -> Sequence[GearContainerDB]:
        """Get all public containers from all users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of public containers with user relationship loaded
        """
        stmt = (
            select(GearContainerDB)
            .where(
                and_(
                    GearContainerDB.is_public == True,  # noqa: E712
                    GearContainerDB.is_hidden_by_reports == False,  # noqa: E712
                )
            )
            .options(
                selectinload(GearContainerDB.items),  # type: ignore[attr-defined]
                joinedload(GearContainerDB.user),  # type: ignore[attr-defined]
            )
            .offset(skip)
            .limit(limit)
            .order_by(GearContainerDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_public_container(self, container_id: str) -> GearContainerDB | None:
        """Get a public container by ID.

        Args:
            container_id: Container ID

        Returns:
            Container if found and public, None otherwise (with user relationship loaded)
        """
        stmt = (
            select(GearContainerDB)
            .where(
                and_(
                    GearContainerDB.id == container_id,
                    GearContainerDB.is_public == True,  # noqa: E712
                    GearContainerDB.is_hidden_by_reports == False,  # noqa: E712
                )
            )
            .options(
                selectinload(GearContainerDB.items),  # type: ignore[attr-defined]
                joinedload(GearContainerDB.user),  # type: ignore[attr-defined]
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_public_container_for_reporting(self, container_id: str) -> GearContainerDB | None:
        """Get a public container by ID for reporting purposes.

        This method does NOT filter by is_hidden_by_reports, allowing reports
        even on containers that are already hidden.

        Args:
            container_id: Container ID

        Returns:
            Container if found and public, None otherwise
        """
        stmt = (
            select(GearContainerDB)
            .where(
                and_(
                    GearContainerDB.id == container_id,
                    GearContainerDB.is_public == True,  # noqa: E712
                )
            )
            .options(
                selectinload(GearContainerDB.items),  # type: ignore[attr-defined]
                joinedload(GearContainerDB.user),  # type: ignore[attr-defined]
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_container(self, container_id: str, user_id: str, data: ContainerUpdate) -> GearContainerDB | None:
        """Update a container.

        Args:
            container_id: Container ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated container if found, None otherwise
        """
        container = await self.get_container(container_id, user_id)
        if not container:
            return None

        update_data = data.model_dump(exclude_unset=True)
        # Map camelCase to snake_case
        field_mapping = {
            "parentContainerId": "parent_container_id",
            "hideWhenNested": "hide_when_nested",
            "weightUnit": "weight_unit",
            "maxWeight": "max_weight",
            "maxWeightUnit": "max_weight_unit",
            "isPublic": "is_public",
            "favorite": "favorite",
            "showItemImages": "show_item_images",
        }

        for key, value in update_data.items():
            db_key = field_mapping.get(key, key)
            if hasattr(container, db_key):
                setattr(container, db_key, value)

        await self.db.commit()
        await self.db.refresh(container)
        # Reload container with items relationship to avoid lazy loading issues
        stmt = select(GearContainerDB).where(GearContainerDB.id == container.id).options(selectinload(GearContainerDB.items))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        container = result.scalar_one()
        return container

    async def delete_container(self, container_id: str, user_id: str) -> bool:
        """Delete a container and all its items.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        container = await self.get_container(container_id, user_id)
        if not container:
            return False

        await self.db.delete(container)
        await self.db.commit()
        return True

    async def delete_all_containers(self, user_id: str) -> int:
        """Delete all containers for a user.

        Args:
            user_id: Owner user ID

        Returns:
            Number of deleted containers
        """
        stmt = select(GearContainerDB).where(GearContainerDB.user_id == user_id)
        result = await self.db.execute(stmt)
        containers = result.scalars().all()

        for container in containers:
            await self.db.delete(container)

        await self.db.commit()
        return len(containers)

    # Item operations
    async def create_item(self, container_id: str, user_id: str, data: ItemCreate) -> GearItemDB | None:
        """Create a new gear item in a container.

        Args:
            container_id: Parent container ID
            user_id: Owner user ID
            data: Item creation data

        Returns:
            Created item if container exists, None otherwise
        """
        # Verify container exists and belongs to user
        container = await self.get_container(container_id, user_id)
        if not container:
            return None

        # Calculate order if not provided
        order = data.order
        if order is None:
            # Get max order in container
            stmt = select(func.max(GearItemDB.order)).where(GearItemDB.container_id == container_id)
            result = await self.db.execute(stmt)
            max_order = result.scalar()
            order = (max_order + 1) if max_order is not None else 0

        item = GearItemDB(
            id=(data.id if data.id else generate_id()),  # Use provided UUID if available, otherwise generate new one
            container_id=container_id,
            name=data.name,
            category=data.category,
            quantity=data.quantity,
            weight=data.weight,
            weight_unit=data.weightUnit,
            notes=data.notes,
            expiration_date=data.expirationDate,
            shelf_life=data.shelfLife,
            priority=data.priority,
            status=data.status,
            nested_container_id=data.containerId,
            price=data.price,
            currency=data.currency,
            url=data.url,
            brand=data.brand,
            color=data.color,
            quality=data.quality,
            linked_item_id=data.linkedItemId,
            catalogue_item_id=data.catalogueItemId,
            wearable=data.wearable,
            consumable=data.consumable,
            order=order,
            show_on_container=data.showOnContainer,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        # Reload container relationship after refresh
        reload_stmt = select(GearItemDB).where(GearItemDB.id == item.id).options(joinedload(GearItemDB.container))
        reload_result = await self.db.execute(reload_stmt)
        return reload_result.unique().scalar_one()

    async def get_item(self, item_id: str, user_id: str) -> GearItemDB | None:
        """Get an item by ID for a specific user.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            Item if found, None otherwise (with container relationship loaded)
        """
        stmt = select(GearItemDB).join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id).where(and_(GearItemDB.id == item_id, GearContainerDB.user_id == user_id)).options(joinedload(GearItemDB.container))
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_items(self, container_id: str, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[GearItemDB]:
        """Get all items in a container.

        Args:
            container_id: Parent container ID
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of items (with container relationship loaded)
        """
        # Verify container belongs to user
        container = await self.get_container(container_id, user_id)
        if not container:
            return []

        # Sort by order (nulls last), then by created_at
        # Load container relationship for each item
        stmt = select(GearItemDB).where(GearItemDB.container_id == container_id).options(joinedload(GearItemDB.container)).offset(skip).limit(limit).order_by(GearItemDB.order.asc().nulls_last(), GearItemDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_items(self, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[GearItemDB]:
        """Get all items for a user across all containers.

        Args:
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of items (with container relationship loaded)
        """
        # Join with containers to filter by user_id
        # Load container relationship for each item
        stmt = (
            select(GearItemDB)
            .join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id)
            .where(GearContainerDB.user_id == user_id)
            .options(joinedload(GearItemDB.container))
            .offset(skip)
            .limit(limit)
            .order_by(GearItemDB.order.asc().nulls_last(), GearItemDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def update_item(self, item_id: str, user_id: str, data: ItemUpdate) -> GearItemDB | None:
        """Update a gear item and propagate changes to all linked items.

        When updating an item, if it's part of a linked group (via linked_item_id),
        all items in that group will be updated with the same changes.

        Args:
            item_id: Item ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated item if found, None otherwise
        """
        item = await self.get_item(item_id, user_id)
        if not item:
            return None

        # Determine master item ID: if item has linked_item_id, use that; otherwise use item.id
        master_item_id = item.linked_item_id if item.linked_item_id else item.id

        # Find all items that belong to the same linked group:
        # - The master item itself (id == master_item_id)
        # - All items that link to it (linked_item_id == master_item_id)
        # All must belong to the user (via container.user_id)
        stmt = (
            select(GearItemDB)
            .join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id)
            .where(
                and_(
                    GearContainerDB.user_id == user_id,
                    or_(
                        GearItemDB.id == master_item_id,
                        GearItemDB.linked_item_id == master_item_id,
                    ),
                ),
            )
        )
        result = await self.db.execute(stmt)
        linked_items = result.scalars().all()

        # Prepare update data
        update_data = data.model_dump(exclude_unset=True)
        # Map camelCase to snake_case
        field_mapping = {
            "weightUnit": "weight_unit",
            "expirationDate": "expiration_date",
            "shelfLife": "shelf_life",
            "containerId": "nested_container_id",
            "linkedItemId": "linked_item_id",
            "catalogueItemId": "catalogue_item_id",
            "showOnContainer": "show_on_container",
        }

        # Update all linked items with the same data
        # Note: We don't update linked_item_id itself (it should remain unchanged)
        updated_item = None
        for linked_item in linked_items:
            for key, value in update_data.items():
                # Skip linkedItemId - don't change the linking relationship
                if key == "linkedItemId":
                    continue
                db_key = field_mapping.get(key, key)
                if hasattr(linked_item, db_key):
                    setattr(linked_item, db_key, value)

            # Track the originally requested item for return
            if linked_item.id == item_id:
                updated_item = linked_item

        await self.db.commit()
        if updated_item:
            await self.db.refresh(updated_item)
            # Reload container relationship after refresh
            reload_stmt = select(GearItemDB).where(GearItemDB.id == updated_item.id).options(joinedload(GearItemDB.container))
            reload_result = await self.db.execute(reload_stmt)
            updated_item = reload_result.unique().scalar_one()
        return updated_item

    async def move_item(self, item_id: str, user_id: str, target_container_id: str) -> GearItemDB | None:
        """Move a gear item to a different container.

        Only moves the single specified item, not linked items.
        The item's linked_item_id relationship is preserved.

        Args:
            item_id: Item ID to move
            user_id: Owner user ID
            target_container_id: Target container ID

        Returns:
            Updated item if found and moved, None if item not found

        Raises:
            ValueError: If target container not found or doesn't belong to user
        """
        # Get and verify item ownership
        item = await self.get_item(item_id, user_id)
        if not item:
            return None

        # Verify target container exists and belongs to user
        target_container = await self.get_container(target_container_id, user_id)
        if not target_container:
            raise ValueError("Target container not found or access denied")

        # Update container_id
        item.container_id = target_container_id

        await self.db.commit()
        await self.db.refresh(item)

        # Reload with container relationship
        reload_stmt = select(GearItemDB).where(GearItemDB.id == item.id).options(joinedload(GearItemDB.container))
        reload_result = await self.db.execute(reload_stmt)
        updated_item = reload_result.unique().scalar_one()

        return updated_item

    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        item = await self.get_item(item_id, user_id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True

    async def batch_update_item_order(self, user_id: str, data: BatchOrderUpdateRequest) -> list[GearItemDB]:
        """Batch update items' order values.

        Args:
            user_id: Owner user ID
            data: Batch order update request with list of item IDs and their new order values

        Returns:
            List of updated items

        Raises:
            ValueError: If any item ID is not found or doesn't belong to the user
        """
        # Get all item IDs from the request
        item_ids = [item_order.id for item_order in data.items]

        # Fetch all items and verify they belong to the user
        stmt = (
            select(GearItemDB)
            .join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id)
            .where(
                and_(
                    GearItemDB.id.in_(item_ids),
                    GearContainerDB.user_id == user_id,
                )
            )
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()

        # Verify all items were found
        found_item_ids = {item.id for item in items}
        missing_item_ids = set(item_ids) - found_item_ids
        if missing_item_ids:
            raise ValueError(f"Items not found or access denied: {missing_item_ids}")

        # Create a map of item_id -> new order
        order_map = {item_order.id: item_order.order for item_order in data.items}

        # Update order for each item
        for item in items:
            item.order = order_map[item.id]

        await self.db.commit()

        # Refresh all items
        for item in items:
            await self.db.refresh(item)

        return list(items)

    # Item promotion operations
    async def get_promotion_by_item_and_user(self, item_id: str, user_id: str) -> ItemPromotionDB | None:
        """Get promotion record by item and user.

        Args:
            item_id: Item ID
            user_id: User ID

        Returns:
            Promotion record if found, None otherwise
        """
        stmt = select(ItemPromotionDB).where(
            and_(
                ItemPromotionDB.item_id == item_id,
                ItemPromotionDB.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_promotion(self, item_id: str, user_id: str) -> ItemPromotionDB:
        """Create a new promotion record.

        Args:
            item_id: Item ID to promote
            user_id: User ID who is promoting

        Returns:
            Created promotion record
        """
        promotion = ItemPromotionDB(
            id=generate_id(),
            item_id=item_id,
            user_id=user_id,
        )
        self.db.add(promotion)
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def get_promotions_by_item(self, item_id: str) -> Sequence[ItemPromotionDB]:
        """Get all promotions for an item.

        Args:
            item_id: Item ID

        Returns:
            List of promotion records
        """
        stmt = select(ItemPromotionDB).where(ItemPromotionDB.item_id == item_id).order_by(ItemPromotionDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # Share token operations
    async def create_share_token(
        self,
        container_id: str,
        user_id: str,
        token: str,
        expires_at: datetime | None = None,
    ) -> ContainerShareTokenDB:
        """Create a share token for a container.

        Args:
            container_id: Container ID to share
            user_id: Owner user ID
            token: Unique share token
            expires_at: Optional expiration timestamp

        Returns:
            Created share token
        """
        share_token = ContainerShareTokenDB(
            token=token,
            container_id=container_id,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.db.add(share_token)
        await self.db.commit()
        await self.db.refresh(share_token)
        return share_token

    async def get_container_by_token(self, token: str) -> GearContainerDB | None:
        """Get a container by share token.

        Args:
            token: Share token

        Returns:
            Container if token is valid and not expired, None otherwise (with user relationship loaded)
        """
        # Check if token exists and is not expired
        token_stmt = (
            select(ContainerShareTokenDB)
            .where(ContainerShareTokenDB.token == token)
            .where(
                or_(
                    ContainerShareTokenDB.expires_at.is_(None),
                    ContainerShareTokenDB.expires_at > datetime.now(UTC),
                )
            )
        )
        token_result = await self.db.execute(token_stmt)
        share_token = token_result.scalar_one_or_none()

        if not share_token:
            return None

        # Get container with items and user relationship
        stmt = (
            select(GearContainerDB)
            .where(GearContainerDB.id == share_token.container_id)
            .options(
                selectinload(GearContainerDB.items),  # type: ignore[attr-defined]
                joinedload(GearContainerDB.user),  # type: ignore[attr-defined]
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_share_tokens_by_container(self, container_id: str, user_id: str) -> Sequence[ContainerShareTokenDB]:
        """Get all share tokens for a container (only for owner).

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            List of share tokens for the container
        """
        # Verify container ownership
        container = await self.get_container(container_id, user_id)
        if not container:
            return []

        stmt = select(ContainerShareTokenDB).where(ContainerShareTokenDB.container_id == container_id).order_by(ContainerShareTokenDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def revoke_share_token(self, token: str, user_id: str) -> bool:
        """Revoke a share token (only by owner).

        Args:
            token: Share token to revoke
            user_id: Owner user ID

        Returns:
            True if token was revoked, False otherwise
        """
        token_stmt = select(ContainerShareTokenDB).where(ContainerShareTokenDB.token == token)
        token_result = await self.db.execute(token_stmt)
        share_token = token_result.scalar_one_or_none()

        if not share_token or share_token.user_id != user_id:
            return False

        await self.db.delete(share_token)
        await self.db.commit()
        return True

    # Rating operations
    async def get_container_rating(self, container_id: str, user_id: str, rating_type: str = "user") -> ContainerRatingDB | None:
        """Get user's rating for a container by type.

        Args:
            container_id: Container ID
            user_id: User ID
            rating_type: Rating type ('owner' or 'user')

        Returns:
            Rating if found, None otherwise
        """
        result = await self.db.execute(select(ContainerRatingDB).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.user_id == user_id).where(ContainerRatingDB.rating_type == rating_type))
        return result.scalar_one_or_none()

    async def upsert_container_rating(self, container_id: str, user_id: str, rating: int, rating_type: str = "user") -> ContainerRatingDB:
        """Create or update user's rating for a container.

        Args:
            container_id: Container ID
            user_id: User ID
            rating: Rating value (1-5)
            rating_type: Rating type ('owner' or 'user')

        Returns:
            Created or updated rating
        """
        existing = await self.get_container_rating(container_id, user_id, rating_type)

        if existing:
            existing.rating = rating
            existing.updated_at = datetime.now(UTC)
            await self.db.flush()
            return existing

        new_rating = ContainerRatingDB(
            id=generate_id(),
            container_id=container_id,
            user_id=user_id,
            rating=rating,
            rating_type=rating_type,
        )
        self.db.add(new_rating)
        await self.db.flush()
        return new_rating

    async def delete_container_rating(self, container_id: str, user_id: str, rating_type: str = "user") -> bool:
        """Delete user's rating for a container.

        Args:
            container_id: Container ID
            user_id: User ID
            rating_type: Rating type ('owner' or 'user')

        Returns:
            True if deleted, False if not found
        """
        rating = await self.get_container_rating(container_id, user_id, rating_type)
        if rating:
            await self.db.delete(rating)
            await self.db.flush()
            return True
        return False

    async def get_container_average_user_rating(self, container_id: str) -> float | None:
        """Calculate average user rating for a container (excluding owner ratings).

        Args:
            container_id: Container ID

        Returns:
            Average rating or None if no ratings
        """
        result = await self.db.execute(select(func.avg(ContainerRatingDB.rating)).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.rating_type == "user"))
        avg = result.scalar()
        return float(avg) if avg is not None else None

    async def get_container_user_rating_count(self, container_id: str) -> int:
        """Get number of user ratings for a container (excluding owner ratings).

        Args:
            container_id: Container ID

        Returns:
            Number of user ratings
        """
        result = await self.db.execute(select(func.count(ContainerRatingDB.id)).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.rating_type == "user"))
        return result.scalar() or 0

    async def get_container_owner_rating(self, container_id: str) -> int | None:
        """Get owner's rating for a container.

        Args:
            container_id: Container ID

        Returns:
            Owner rating (1-5) or None if not set
        """
        result = await self.db.execute(select(ContainerRatingDB.rating).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.rating_type == "owner").limit(1))
        rating = result.scalar_one_or_none()
        return rating if rating else None

    class ContainerRatingsData(TypedDict):
        """Type for container ratings aggregated data."""

        owner_rating: int | None
        user_rating: int | None
        average_user_rating: float | None
        user_rating_count: int

    async def get_container_ratings_data(
        self,
        container_id: str,
        requesting_user_id: str | None = None,
        is_owner: bool = False,
    ) -> ContainerRatingsData:
        """Get all ratings data for a container.

        Args:
            container_id: Container ID
            requesting_user_id: ID of user requesting the data (for user_rating)
            is_owner: Whether requesting user is the owner

        Returns:
            Dictionary with all rating fields
        """
        # Load owner rating
        owner_rating = await self.get_container_owner_rating(container_id)

        # Load user rating (only if not owner and user_id provided)
        user_rating = None
        if requesting_user_id and not is_owner:
            user_rating_obj = await self.get_container_rating(container_id, requesting_user_id, rating_type="user")
            user_rating = user_rating_obj.rating if user_rating_obj else None

        # Calculate average user rating and count
        avg_user_rating = await self.get_container_average_user_rating(container_id)
        user_rating_count = await self.get_container_user_rating_count(container_id)

        return {
            "owner_rating": owner_rating,
            "user_rating": user_rating,
            "average_user_rating": avg_user_rating,
            "user_rating_count": user_rating_count,
        }

    # Global Catalogue Methods
    async def get_catalogue_items(
        self,
        query: str | None = None,
        category: str | None = None,
        brand: str | None = None,
        price_tier: str | None = None,
        quality: str | None = None,
        is_active: bool | None = True,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[GlobalCatalogueItemDB]:
        """Get global catalogue items with filtering and search.

        Args:
            query: Search query (searches in name, description, brand, model)
            category: Filter by category
            brand: Filter by brand
            price_tier: Filter by price tier
            quality: Filter by quality
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of catalogue items
        """
        stmt = select(GlobalCatalogueItemDB)

        # Build filters
        conditions = []
        if is_active is not None:
            conditions.append(GlobalCatalogueItemDB.is_active == is_active)
        if category:
            conditions.append(GlobalCatalogueItemDB.category == category)
        if brand:
            conditions.append(GlobalCatalogueItemDB.brand == brand)
        if price_tier:
            conditions.append(GlobalCatalogueItemDB.price_tier == price_tier)
        if quality:
            conditions.append(GlobalCatalogueItemDB.quality == quality)

        # Full Text Search using PostgreSQL to_tsvector and to_tsquery
        if query:
            from sqlalchemy import func, text

            # Escape special characters in query for tsquery
            # Replace spaces with & (AND operator) and escape special characters
            query_escaped = query.replace("'", "''").replace("&", " ").replace("|", " ").replace("!", " ").replace("(", " ").replace(")", " ")
            # Split by spaces and join with & (AND) operator
            query_terms = " & ".join([term.strip() for term in query_escaped.split() if term.strip()])

            # Build tsvector from multiple columns (name, description, brand, model)
            # Use 'simple' dictionary for better matching (no language-specific stemming)
            # Concatenate columns with space separator using || operator
            tsvector_expr = func.to_tsvector(
                "simple",
                func.coalesce(GlobalCatalogueItemDB.name, "") + " " + func.coalesce(GlobalCatalogueItemDB.description, "") + " " + func.coalesce(GlobalCatalogueItemDB.brand, "") + " " + func.coalesce(GlobalCatalogueItemDB.model, ""),
            )
            tsquery_expr = func.to_tsquery("simple", query_terms)

            # Full text search condition using @@ operator (PostgreSQL full-text search)
            # Use text() with proper parameter binding for safety
            # Apply search condition directly to statement (not via conditions list)
            search_condition = text(
                "to_tsvector('simple', "
                "coalesce(global_catalogue_items.name, '') || ' ' || "
                "coalesce(global_catalogue_items.description, '') || ' ' || "
                "coalesce(global_catalogue_items.brand, '') || ' ' || "
                "coalesce(global_catalogue_items.model, '')) "
                "@@ to_tsquery('simple', :query_terms)"
            ).bindparams(query_terms=query_terms)
            stmt = stmt.where(search_condition)

            # Order by relevance (ts_rank) when searching
            rank_expr = func.ts_rank(tsvector_expr, tsquery_expr)
            stmt = stmt.order_by(rank_expr.desc(), GlobalCatalogueItemDB.name.asc())
        else:
            # Order by name when not searching
            stmt = stmt.order_by(GlobalCatalogueItemDB.name.asc())

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Load creator relationship
        stmt = stmt.options(joinedload(GlobalCatalogueItemDB.creator))

        # Pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_catalogue_item(self, item_id: str) -> GlobalCatalogueItemDB | None:
        """Get a single catalogue item by ID.

        Args:
            item_id: Catalogue item ID

        Returns:
            Catalogue item if found, None otherwise (with creator relationship loaded)
        """
        stmt = select(GlobalCatalogueItemDB).where(GlobalCatalogueItemDB.id == item_id).options(joinedload(GlobalCatalogueItemDB.creator))
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_catalogue_item(
        self,
        user_id: str,
        data: GlobalCatalogueItemCreate,
    ) -> GlobalCatalogueItemDB:
        """Create a new catalogue item.

        Args:
            user_id: User ID creating the item
            data: Item creation data

        Returns:
            Created catalogue item
        """
        item_id = generate_id()
        item = GlobalCatalogueItemDB(
            id=item_id,
            version=1,
            name=data.name,
            category=data.category,
            weight=data.weight,
            weight_unit=data.weightUnit,
            description=data.description,
            brand=data.brand,
            model=data.model,
            price_tier=data.priceTier,
            price=data.price,
            currency=data.currency,
            quality=data.quality,
            url=data.url,
            color=data.color,
            is_active=True,
            created_by=user_id,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update_catalogue_item(
        self,
        item_id: str,
        user_id: str,
        data: GlobalCatalogueItemUpdate,
        is_admin: bool = False,
    ) -> GlobalCatalogueItemDB | None:
        """Update a catalogue item.

        Only the creator or admin can update items.

        Args:
            item_id: Catalogue item ID
            user_id: User ID updating the item
            data: Update data
            is_admin: Whether user is admin

        Returns:
            Updated item if found and user has permission, None otherwise
        """
        item = await self.get_catalogue_item(item_id)
        if not item:
            return None

        # Check permissions: creator or admin
        if not is_admin and item.created_by != user_id:
            return None

        # Update fields
        update_dict = data.model_dump(exclude_unset=True, by_alias=False)
        for key, value in update_dict.items():
            # Handle camelCase to snake_case conversion
            if key == "weightUnit":
                item.weight_unit = value
            elif key == "priceTier":
                item.price_tier = value
            elif key == "isActive":
                item.is_active = value
            else:
                setattr(item, key, value)

        # Increment version on update
        item.version += 1
        item.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_catalogue_item(
        self,
        item_id: str,
        user_id: str,
        is_admin: bool = False,
    ) -> bool:
        """Delete a catalogue item (soft delete by setting is_active=False).

        Only the creator or admin can delete items.

        Args:
            item_id: Catalogue item ID
            user_id: User ID deleting the item
            is_admin: Whether user is admin

        Returns:
            True if deleted, False otherwise
        """
        item = await self.get_catalogue_item(item_id)
        if not item:
            return False

        # Check permissions: creator or admin
        if not is_admin and item.created_by != user_id:
            return False

        # Soft delete
        item.is_active = False
        item.updated_at = datetime.now(UTC)
        await self.db.commit()
        return True

    # Content report operations
    async def create_container_report(
        self,
        container_id: str,
        reporter_user_id: str,
        reason: str,
        additional_info: str | None = None,
    ) -> ContentReportDB:
        """Create a new content report for a container.

        Args:
            container_id: Container ID being reported
            reporter_user_id: User ID reporting the container
            reason: Reason for report (spam_fraud, violence, sexual_content, profanity, other)
            additional_info: Optional additional information

        Returns:
            Created report

        Raises:
            IntegrityError: If report already exists (unique constraint violation)
        """
        report = ContentReportDB(
            id=generate_id(),
            container_id=container_id,
            reporter_user_id=reporter_user_id,
            reason=reason,
            additional_info=additional_info,
            status="pending",
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

        # Reload with relationships
        stmt = (
            select(ContentReportDB)
            .options(
                joinedload(ContentReportDB.container),
                joinedload(ContentReportDB.reporter),
            )
            .where(ContentReportDB.id == report.id)
        )
        result = await self.db.execute(stmt)
        report_with_relations = result.unique().scalar_one()

        return report_with_relations

    async def get_reports_for_container(self, container_id: str) -> Sequence[ContentReportDB]:
        """Get all reports for a container.

        Args:
            container_id: Container ID

        Returns:
            List of reports for the container
        """
        stmt = select(ContentReportDB).where(ContentReportDB.container_id == container_id).order_by(ContentReportDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_active_reports_for_container(self, container_id: str) -> int:
        """Count active reports (pending + action_taken) for a container.

        Args:
            container_id: Container ID

        Returns:
            Number of active reports
        """
        stmt = select(func.count(ContentReportDB.id)).where(
            and_(
                ContentReportDB.container_id == container_id,
                or_(
                    ContentReportDB.status == "pending",
                    ContentReportDB.status == "action_taken",
                ),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_all_reports(
        self,
        status: str | None = None,
        container_id: str | None = None,
        reporter_user_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ContentReportDB], int]:
        """Get all reports with optional filters.

        Args:
            status: Filter by status (pending, reviewed, dismissed, action_taken)
            container_id: Filter by container ID
            reporter_user_id: Filter by reporter user ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Tuple of (reports list, total count)
        """
        conditions = []
        if status:
            conditions.append(ContentReportDB.status == status)
        if container_id:
            conditions.append(ContentReportDB.container_id == container_id)
        if reporter_user_id:
            conditions.append(ContentReportDB.reporter_user_id == reporter_user_id)

        where_clause = and_(*conditions) if conditions else true()

        # Get total count
        count_stmt = select(func.count(ContentReportDB.id)).where(where_clause)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get reports with eager loading of relationships
        stmt = (
            select(ContentReportDB)
            .options(
                joinedload(ContentReportDB.container),
                joinedload(ContentReportDB.reporter),
            )
            .where(where_clause)
            .order_by(ContentReportDB.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        reports = result.unique().scalars().all()

        return reports, total

    async def update_report_status(
        self,
        report_id: str,
        status: str,
        reviewed_by: str | None = None,
    ) -> ContentReportDB | None:
        """Update report status.

        Args:
            report_id: Report ID
            status: New status (pending, reviewed, dismissed, action_taken)
            reviewed_by: User ID who reviewed the report (for reviewed/action_taken statuses)

        Returns:
            Updated report if found, None otherwise
        """
        stmt = (
            select(ContentReportDB)
            .options(
                joinedload(ContentReportDB.container),
                joinedload(ContentReportDB.reporter),
            )
            .where(ContentReportDB.id == report_id)
        )
        result = await self.db.execute(stmt)
        report = result.unique().scalar_one_or_none()

        if not report:
            return None

        report.status = status
        if reviewed_by:
            report.reviewed_by = reviewed_by
        if status in ("reviewed", "dismissed", "action_taken"):
            report.reviewed_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def set_container_hidden_by_reports(self, container_id: str, is_hidden: bool) -> GearContainerDB | None:
        """Set is_hidden_by_reports flag for a container.

        Args:
            container_id: Container ID
            is_hidden: Whether container should be hidden

        Returns:
            Updated container if found, None otherwise
        """
        stmt = select(GearContainerDB).where(GearContainerDB.id == container_id)
        result = await self.db.execute(stmt)
        container = result.scalar_one_or_none()

        if not container:
            return None

        container.is_hidden_by_reports = is_hidden
        container.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(container)
        return container

    async def get_report_by_container_and_user(
        self,
        container_id: str,
        user_id: str,
    ) -> ContentReportDB | None:
        """Get report by container ID and user ID.

        Args:
            container_id: Container ID
            user_id: Reporter user ID

        Returns:
            Report if found, None otherwise
        """
        stmt = select(ContentReportDB).where(
            and_(
                ContentReportDB.container_id == container_id,
                ContentReportDB.reporter_user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_report(self, report_id: str) -> bool:
        """Delete a report.

        Args:
            report_id: Report ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(ContentReportDB).where(ContentReportDB.id == report_id)
        result = await self.db.execute(stmt)
        report = result.scalar_one_or_none()

        if not report:
            return False

        await self.db.delete(report)
        await self.db.commit()
        return True
