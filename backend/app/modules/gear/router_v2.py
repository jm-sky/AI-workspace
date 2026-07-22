"""FastAPI router for unified gear management (V2).

This module provides REST API endpoints for the unified gear model where
containers are items with item_type='container'.

All endpoints require authentication.
"""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser

from .repository_v2 import GearRepositoryV2
from .schemas_v2 import (
    GearItemBatchUpdateOrderV2,
    GearItemCreateV2,
    GearItemResponseV2,
    GearItemUpdateV2,
)
from .service_v2 import GearServiceV2

router = APIRouter(prefix="/gear/v2", tags=["gear-v2"])

logger = logging.getLogger(__name__)


def get_gear_repository_v2(db: AsyncSession = Depends(get_db)) -> GearRepositoryV2:
    """Dependency to get gear repository V2 instance.

    Args:
        db: Database session

    Returns:
        Gear repository V2 instance
    """
    return GearRepositoryV2(db)


def get_gear_service_v2(
    repository: GearRepositoryV2 = Depends(get_gear_repository_v2),
) -> GearServiceV2:
    """Dependency to get gear service V2 instance.

    Args:
        repository: Gear repository V2 instance

    Returns:
        Gear service V2 instance
    """
    return GearServiceV2(repository)


GearServiceV2Dep = Annotated[GearServiceV2, Depends(get_gear_service_v2)]


# ===== Create Operations =====


@router.post("/items", response_model=GearItemResponseV2, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: GearItemCreateV2,
    current_user: CurrentUser,
    service: GearServiceV2Dep,
) -> GearItemResponseV2:
    """Create a new gear item (container or regular item).

    Examples:
        # Create container
        POST /gear/v2/items
        {
            "itemType": "container",
            "name": "Bug-out Bag",
            "containerType": "backpack",
            "isPublic": false
        }

        # Create item
        POST /gear/v2/items
        {
            "itemType": "item",
            "name": "Water Bottle",
            "category": "water",
            "quantity": 1,
            "parentItemId": "container-id"
        }
    """
    try:
        item = await service.create_item(current_user.id, data)
        return GearItemResponseV2.model_validate(item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ===== Read Operations =====


@router.get("/items", response_model=list[GearItemResponseV2])
async def get_items(
    current_user: CurrentUser,
    service: GearServiceV2Dep,
    item_type: Literal["container", "item", "all"] = Query("all", alias="itemType", description="Filter by item type"),
    parent_item_id: str | None = Query(None, alias="parentItemId", description="Filter by parent item ID"),
    is_public: bool | None = Query(None, alias="isPublic", description="Filter by public visibility"),
    favorite: bool | None = Query(None, description="Filter by favorite status"),
    include_children: bool = Query(False, alias="includeChildren", description="Eagerly load children"),
) -> list[GearItemResponseV2]:
    """Get gear items with optional filters.

    Query Parameters:
        itemType: Filter by type ('container', 'item', or 'all')
        parentItemId: Filter by parent (null for root items)
        isPublic: Filter by public visibility
        favorite: Filter by favorite status
        includeChildren: Load children relationships

    Examples:
        # Get all items
        GET /gear/v2/items

        # Get containers only
        GET /gear/v2/items?itemType=container

        # Get root containers
        GET /gear/v2/items?itemType=container&parentItemId=null

        # Get items in a container
        GET /gear/v2/items?itemType=item&parentItemId=container-id

        # Get favorite containers
        GET /gear/v2/items?itemType=container&favorite=true
    """
    # Convert 'null' string or empty string to None (for IS NULL filter)
    # This allows frontend to explicitly filter for root items (no parent)
    filter_for_null_parent = parent_item_id in ("null", "")
    if filter_for_null_parent:
        parent_item_id = None

    if include_children:
        items = await service.get_items_with_children(current_user.id, item_type, parent_item_id, filter_for_null_parent)
    else:
        items = await service.get_items(
            current_user.id,
            item_type,
            parent_item_id,
            is_public,
            favorite,
            filter_for_null_parent,
        )
    return [GearItemResponseV2.model_validate(item) for item in items]


@router.get("/items/{item_id}", response_model=GearItemResponseV2)
async def get_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceV2Dep,
) -> GearItemResponseV2:
    """Get a single gear item by ID.

    Args:
        item_id: Item ID

    Returns:
        Item details

    Raises:
        404: Item not found or access denied
    """
    item = await service.get_item(item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return GearItemResponseV2.model_validate(item)


@router.get("/items/{item_id}/children", response_model=list[GearItemResponseV2])
async def get_item_children(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceV2Dep,
) -> list[GearItemResponseV2]:
    """Get all children of a parent item.

    Args:
        item_id: Parent item ID

    Returns:
        List of child items
    """
    children = await service.get_children(item_id, current_user.id)
    return [GearItemResponseV2.model_validate(child) for child in children]


# ===== Update Operations =====


@router.patch("/items/{item_id}", response_model=GearItemResponseV2)
async def update_item(
    item_id: str,
    data: GearItemUpdateV2,
    current_user: CurrentUser,
    service: GearServiceV2Dep,
) -> GearItemResponseV2:
    """Update a gear item.

    Args:
        item_id: Item ID
        data: Update data

    Returns:
        Updated item

    Raises:
        404: Item not found or access denied
        400: Validation error
    """
    try:
        item = await service.update_item(item_id, current_user.id, data)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return GearItemResponseV2.model_validate(item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.patch("/items/batch/order", response_model=list[GearItemResponseV2])
async def batch_update_order(
    data: GearItemBatchUpdateOrderV2,
    current_user: CurrentUser,
    service: GearServiceV2Dep,
) -> list[GearItemResponseV2]:
    """Batch update order_index for multiple items.

    Used for drag-and-drop reordering.

    Example:
        PATCH /gear/v2/items/batch/order
        {
            "items": [
                {"id": "item-1", "orderIndex": 0},
                {"id": "item-2", "orderIndex": 1},
                {"id": "item-3", "orderIndex": 2}
            ]
        }
    """
    items = await service.batch_update_order(data.items, current_user.id)
    return [GearItemResponseV2.model_validate(item) for item in items]


@router.patch("/items/{item_id}/move", response_model=GearItemResponseV2)
async def move_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceV2Dep,
    target_parent_id: str | None = Query(None, alias="targetParentId"),
) -> GearItemResponseV2:
    """Move an item to a different parent.

    Args:
        item_id: Item ID to move
        targetParentId: Target parent item ID (null for root)

    Returns:
        Updated item

    Raises:
        404: Item not found
        400: Invalid target parent

    Example:
        # Move item to container
        PATCH /gear/v2/items/item-id/move?targetParentId=container-id

        # Move item to root
        PATCH /gear/v2/items/item-id/move?targetParentId=null
    """
    try:
        item = await service.move_item(item_id, current_user.id, target_parent_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return GearItemResponseV2.model_validate(item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ===== Delete Operations =====


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceV2Dep,
) -> None:
    """Delete a gear item.

    Cascade deletes all children due to foreign key constraints.

    Args:
        item_id: Item ID

    Raises:
        404: Item not found or access denied
    """
    deleted = await service.delete_item(item_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
