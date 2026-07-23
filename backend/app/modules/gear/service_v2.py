"""Service layer for unified gear management (V2).

This module provides business logic for the unified gear model.
"""

import logging
from collections.abc import Sequence

from .db_models_v2 import GearItemDBV2
from .repository_v2 import GearRepositoryV2
from .schemas_v2 import GearItemCreateV2, GearItemUpdateV2

logger = logging.getLogger(__name__)


class GearServiceV2:
    """Service for unified gear operations (V2).

    Provides business logic layer on top of repository operations.
    """

    def __init__(self, repository: GearRepositoryV2):
        """Initialize service with repository.

        Args:
            repository: Gear repository instance
        """
        self.repository = repository

    # Create operations

    async def create_item(self, user_id: str, data: GearItemCreateV2) -> GearItemDBV2:
        """Create a new gear item (container or regular item).

        Args:
            user_id: Owner user ID
            data: Item creation data

        Returns:
            Created item

        Raises:
            ValueError: If validation fails
        """
        # Validate parent item exists if provided
        if data.parentItemId:
            parent = await self.repository.get_item(data.parentItemId, user_id)
            if not parent:
                raise ValueError("Parent item not found or access denied")
            # Verify parent is a container
            if parent.item_type != "container":
                raise ValueError("Parent must be a container")

        return await self.repository.create_item(user_id, data)

    # Read operations

    async def get_item(self, item_id: str, user_id: str) -> GearItemDBV2 | None:
        """Get a gear item by ID.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            Item if found and owned by user, None otherwise
        """
        return await self.repository.get_item(item_id, user_id)

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
            item_type: Filter by item type ('container', 'item', or 'all')
            parent_item_id: Filter by parent item ID
            is_public: Filter by public visibility
            favorite: Filter by favorite status
            filter_for_null_parent: If True, filter for items with parent_item_id IS NULL

        Returns:
            List of items matching filters
        """
        return await self.repository.get_items(
            user_id,
            item_type,
            parent_item_id,
            is_public,
            favorite,
            filter_for_null_parent,
        )

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
        return await self.repository.get_items_with_children(user_id, item_type, parent_item_id, filter_for_null_parent)

    async def get_children(self, parent_item_id: str, user_id: str) -> Sequence[GearItemDBV2]:
        """Get all children of a parent item.

        Args:
            parent_item_id: Parent item ID
            user_id: Owner user ID

        Returns:
            List of child items
        """
        return await self.repository.get_children(parent_item_id, user_id)

    # Update operations

    async def update_item(self, item_id: str, user_id: str, data: GearItemUpdateV2) -> GearItemDBV2 | None:
        """Update a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated item if found and owned by user, None otherwise

        Raises:
            ValueError: If validation fails
        """
        # Validate parent item exists if being updated
        if data.parentItemId:
            parent = await self.repository.get_item(data.parentItemId, user_id)
            if not parent:
                raise ValueError("Parent item not found or access denied")
            # Verify parent is a container
            if parent.item_type != "container":
                raise ValueError("Parent must be a container")

        return await self.repository.update_item(item_id, user_id, data)

    async def batch_update_order(self, items: list[dict], user_id: str) -> Sequence[GearItemDBV2]:
        """Batch update order_index for multiple items.

        Args:
            items: List of dicts with 'id' and 'orderIndex'
            user_id: Owner user ID

        Returns:
            List of updated items
        """
        return await self.repository.batch_update_order(items, user_id)

    # Delete operations

    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete a gear item.

        Cascade deletes all children due to foreign key constraints.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found or not owned
        """
        return await self.repository.delete_item(item_id, user_id)

    # Move operation

    async def is_descendant(self, potential_descendant_id: str, ancestor_id: str, user_id: str) -> bool:
        """Check if an item is a descendant of another item (recursive).

        Args:
            potential_descendant_id: ID of item that might be a descendant
            ancestor_id: ID of potential ancestor item
            user_id: Owner user ID

        Returns:
            True if potential_descendant is a descendant of ancestor, False otherwise
        """
        # Get all children of ancestor
        children = await self.repository.get_children(ancestor_id, user_id)

        for child in children:
            # Direct child match
            if child.id == potential_descendant_id:
                return True
            # Recursive check for indirect descendants
            if await self.is_descendant(potential_descendant_id, child.id, user_id):
                return True

        return False

    async def move_item(self, item_id: str, user_id: str, target_parent_id: str | None) -> GearItemDBV2 | None:
        """Move an item to a different parent.

        Args:
            item_id: Item ID to move
            user_id: Owner user ID
            target_parent_id: Target parent item ID (None for root)

        Returns:
            Updated item if successful, None if not found

        Raises:
            ValueError: If target is invalid or would create circular reference
        """
        # Check for circular reference: prevent moving item to its own descendant
        if target_parent_id is not None:
            if target_parent_id == item_id:
                raise ValueError("Cannot move item to itself")
            if await self.is_descendant(target_parent_id, item_id, user_id):
                raise ValueError("Cannot move item: would create circular reference")

        return await self.repository.move_item(item_id, user_id, target_parent_id)

    # Content Reporting operations

    async def hide_container_by_reports(self, item_id: str, user_id: str) -> GearItemDBV2 | None:
        """Hide a container due to content reports.

        Sets is_hidden_by_reports=True. Only applicable to containers.

        Args:
            item_id: Container ID
            user_id: Owner user ID

        Returns:
            Updated container if found, None otherwise

        Raises:
            ValueError: If item is not a container
        """
        item = await self.repository.get_item(item_id, user_id)
        if not item:
            return None

        if item.item_type != "container":
            raise ValueError("Only containers can be hidden by reports")

        update_data = GearItemUpdateV2.model_construct(isHiddenByReports=True)
        return await self.repository.update_item(item_id, user_id, update_data)

    async def unhide_container_by_reports(self, item_id: str, user_id: str) -> GearItemDBV2 | None:
        """Unhide a container (clear report flag).

        Sets is_hidden_by_reports=False.

        Args:
            item_id: Container ID
            user_id: Owner user ID

        Returns:
            Updated container if found, None otherwise
        """
        update_data = GearItemUpdateV2.model_construct(isHiddenByReports=False)
        return await self.repository.update_item(item_id, user_id, update_data)

    async def get_public_containers(self, user_id: str | None = None, exclude_hidden: bool = True) -> Sequence[GearItemDBV2]:
        """Get public containers, optionally excluding hidden ones.

        Args:
            user_id: Optional user ID (for filtering user's own containers)
            exclude_hidden: If True, exclude containers with is_hidden_by_reports=True

        Returns:
            List of public containers
        """
        return await self.repository.get_public_containers(user_id, exclude_hidden)

    # Item Promotion operations

    async def increment_promotion_count(self, item_id: str, user_id: str) -> GearItemDBV2 | None:
        """Increment promotion count for an item.

        Only applicable to items (not containers).

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            Updated item if found, None otherwise

        Raises:
            ValueError: If item is a container
        """
        item = await self.repository.get_item(item_id, user_id)
        if not item:
            return None

        if item.item_type != "item":
            raise ValueError("Only items can be promoted to catalogue")

        # Increment promote_count
        current_count = item.promote_count or 0
        update_data = GearItemUpdateV2.model_construct(promoteCount=current_count + 1)
        return await self.repository.update_item(item_id, user_id, update_data)

    async def get_promotable_items(self, user_id: str, min_count: int = 10) -> Sequence[GearItemDBV2]:
        """Get items that have reached the promotion threshold.

        Args:
            user_id: Owner user ID
            min_count: Minimum promotion count threshold

        Returns:
            List of items with promote_count >= min_count
        """
        all_items = await self.repository.get_items(user_id, item_type="item")
        return [item for item in all_items if (item.promote_count or 0) >= min_count]
