"""Database repository implementation for unified gear management (V2).

This module provides async repository for managing the unified gear model
where containers are items with item_type='container'.
"""

import logging
from collections.abc import Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.id_utils import generate_id
from app.common.search import SearchMixin

from .db_models_v2 import GearItemDBV2
from .schemas_v2 import GearItemCreateV2, GearItemUpdateV2

logger = logging.getLogger(__name__)


class GearRepositoryV2(SearchMixin):
    """Repository for unified gear items (V2).

    Provides async database operations for the unified model where containers
    are items with item_type='container'.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
        # Configure SearchMixin for gear search
        self._search_columns = [GearItemDBV2.name]
        self._case_sensitive = False

    # Create operations

    async def create_item(self, user_id: str, data: GearItemCreateV2) -> GearItemDBV2:
        """Create a new gear item (container or regular item).

        Args:
            user_id: Owner user ID
            data: Item creation data

        Returns:
            Created item
        """
        is_container = data.itemType == "container"

        item = GearItemDBV2(
            id=(data.id if data.id else generate_id()),
            user_id=user_id,
            item_type=data.itemType,
            parent_item_id=data.parentItemId,
            # Common fields
            name=data.name,
            description=data.description,
            brand=data.brand,
            price=data.price,
            currency=data.currency,
            weight=data.weight,
            weight_unit=data.weightUnit,
            url=data.url,
            color=data.color,
            notes=data.notes,
            # Container-specific — must be NULL for items (check_item_fields constraint)
            container_type=data.containerType if is_container else None,
            max_weight=data.maxWeight if is_container else None,
            max_weight_unit=data.maxWeightUnit if is_container else None,
            hide_when_nested=data.hideWhenNested if is_container else None,
            is_public=((data.isPublic if data.isPublic is not None else False) if is_container else None),
            is_hidden_by_reports=((data.isHiddenByReports if data.isHiddenByReports is not None else False) if is_container else None),
            favorite=((data.favorite if data.favorite is not None else False) if is_container else None),
            show_item_images=((data.showItemImages if data.showItemImages is not None else False) if is_container else None),
            # Item-specific — must be NULL for containers (check_container_fields constraint)
            category=data.category if not is_container else None,
            quantity=((data.quantity if data.quantity is not None else 1) if not is_container else None),
            status=((data.status if data.status is not None else "owned") if not is_container else None),
            priority=((data.priority if data.priority is not None else "medium") if not is_container else None),
            expiration_date=data.expirationDate if not is_container else None,
            shelf_life=data.shelfLife if not is_container else None,
            quality=data.quality if not is_container else None,
            wearable=((data.wearable if data.wearable is not None else False) if not is_container else None),
            consumable=((data.consumable if data.consumable is not None else False) if not is_container else None),
            order_index=data.orderIndex if not is_container else None,
            show_on_container=((data.showOnContainer if data.showOnContainer is not None else False) if not is_container else None),
            promote_count=((data.promoteCount if data.promoteCount is not None else 0) if not is_container else None),
            # Linking
            linked_item_id=data.linkedItemId,
            catalogue_item_id=data.catalogueItemId,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    # Read operations

    async def get_item(self, item_id: str, user_id: str) -> GearItemDBV2 | None:
        """Get a gear item by ID.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            Item if found and owned by user, None otherwise
        """
        stmt = select(GearItemDBV2).where(
            and_(
                GearItemDBV2.id == item_id,
                GearItemDBV2.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_items(
        self,
        user_id: str,
        item_type: str | None = None,
        parent_item_id: str | None = None,
        is_public: bool | None = None,
        favorite: bool | None = None,
        filter_for_null_parent: bool = False,
    ) -> Sequence[GearItemDBV2]:
        """Get gear items with optional filters.

        Args:
            user_id: Owner user ID
            item_type: Filter by item type ('container', 'item', or None for all)
            parent_item_id: Filter by parent item ID
            is_public: Filter by public visibility
            favorite: Filter by favorite status
            filter_for_null_parent: If True, filter for items with parent_item_id IS NULL

        Returns:
            List of items matching filters
        """
        conditions = [GearItemDBV2.user_id == user_id]

        if item_type and item_type != "all":
            conditions.append(GearItemDBV2.item_type == item_type)

        if parent_item_id is not None:
            conditions.append(GearItemDBV2.parent_item_id == parent_item_id)
        elif filter_for_null_parent:
            # Explicitly filter for items with no parent (root items)
            conditions.append(GearItemDBV2.parent_item_id.is_(None))

        if is_public is not None:
            conditions.append(GearItemDBV2.is_public == is_public)

        if favorite is not None:
            conditions.append(GearItemDBV2.favorite == favorite)

        stmt = select(GearItemDBV2).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_items_with_children(
        self,
        user_id: str,
        item_type: str | None = None,
        parent_item_id: str | None = None,
        filter_for_null_parent: bool = False,
    ) -> Sequence[GearItemDBV2]:
        """Get gear items with children eagerly loaded.

        Args:
            user_id: Owner user ID
            item_type: Filter by item type
            parent_item_id: Filter by parent item ID
            filter_for_null_parent: If True, filter for items with parent_item_id IS NULL

        Returns:
            List of items with children loaded
        """
        conditions = [GearItemDBV2.user_id == user_id]

        if item_type and item_type != "all":
            conditions.append(GearItemDBV2.item_type == item_type)

        if parent_item_id is not None:
            conditions.append(GearItemDBV2.parent_item_id == parent_item_id)
        elif filter_for_null_parent:
            # Explicitly filter for items with no parent (root items)
            conditions.append(GearItemDBV2.parent_item_id.is_(None))

        stmt = select(GearItemDBV2).where(and_(*conditions)).options(selectinload(GearItemDBV2.children))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_children(self, parent_item_id: str, user_id: str) -> Sequence[GearItemDBV2]:
        """Get all children of a parent item.

        Args:
            parent_item_id: Parent item ID
            user_id: Owner user ID

        Returns:
            List of child items
        """
        stmt = select(GearItemDBV2).where(
            and_(
                GearItemDBV2.parent_item_id == parent_item_id,
                GearItemDBV2.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # Update operations

    async def update_item(self, item_id: str, user_id: str, data: GearItemUpdateV2) -> GearItemDBV2 | None:
        """Update a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated item if found and owned by user, None otherwise
        """
        item = await self.get_item(item_id, user_id)
        if not item:
            return None

        # Update fields if provided
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            # Convert camelCase to snake_case for DB fields
            db_field = self._camel_to_snake(field)
            if hasattr(item, db_field):
                setattr(item, db_field, value)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def batch_update_order(self, items: list[dict], user_id: str) -> Sequence[GearItemDBV2]:
        """Batch update order_index for multiple items.

        Args:
            items: List of dicts with 'id' and 'orderIndex'
            user_id: Owner user ID

        Returns:
            List of updated items
        """
        updated_items = []
        for item_data in items:
            item = await self.get_item(item_data["id"], user_id)
            if item:
                item.order_index = item_data["orderIndex"]
                updated_items.append(item)

        await self.db.commit()
        for item in updated_items:
            await self.db.refresh(item)

        return updated_items

    # Delete operations

    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found or not owned
        """
        item = await self.get_item(item_id, user_id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True

    # Move operation

    async def move_item(self, item_id: str, user_id: str, target_parent_id: str | None) -> GearItemDBV2 | None:
        """Move an item to a different parent.

        Args:
            item_id: Item ID to move
            user_id: Owner user ID
            target_parent_id: Target parent item ID (None for root)

        Returns:
            Updated item if successful, None if not found or invalid target
        """
        item = await self.get_item(item_id, user_id)
        if not item:
            return None

        # Verify target parent exists and is owned by user (if not None)
        if target_parent_id is not None:
            target = await self.get_item(target_parent_id, user_id)
            if not target:
                raise ValueError("Target parent not found or access denied")
            # Verify target is a container
            if target.item_type != "container":
                raise ValueError("Target must be a container")

        item.parent_item_id = target_parent_id
        await self.db.commit()
        await self.db.refresh(item)
        return item

    # Public containers operations

    async def get_public_containers(self, user_id: str | None = None, exclude_hidden: bool = True) -> Sequence[GearItemDBV2]:
        """Get public containers, optionally excluding hidden ones.

        Args:
            user_id: Optional user ID (for filtering user's own containers)
            exclude_hidden: If True, exclude containers with is_hidden_by_reports=True

        Returns:
            List of public containers
        """
        conditions = [
            GearItemDBV2.item_type == "container",
            GearItemDBV2.is_public == True,  # noqa: E712
        ]

        if user_id is not None:
            conditions.append(GearItemDBV2.user_id == user_id)

        if exclude_hidden:
            conditions.append(
                or_(
                    GearItemDBV2.is_hidden_by_reports == False,  # noqa: E712
                    GearItemDBV2.is_hidden_by_reports.is_(None),
                )
            )

        stmt = select(GearItemDBV2).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # Helper methods

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert camelCase to snake_case.

        Args:
            name: camelCase string

        Returns:
            snake_case string
        """
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)
