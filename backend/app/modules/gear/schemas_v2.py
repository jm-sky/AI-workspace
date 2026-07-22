"""Pydantic schemas for unified gear management (V2).

This module defines request and response models for the unified gear API (V2),
where containers are items with item_type='container'.

Architecture:
- Single schema for both containers and items
- Type discriminator: itemType ('container' | 'item')
- Unified nesting: parentItemId
- Type-specific field validation

Uses camelCase for JSON field names to match frontend conventions.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm.attributes import instance_state

# Type aliases matching frontend
GearItemType = Literal["container", "item"]
GearContainerType = str  # Allows custom types: 'backpack', 'bag', 'pouch', etc.
GearItemStatus = Literal["owned", "missing", "toBuy"]
GearItemPriority = Literal["critical", "high", "medium", "low"]
GearItemQuality = Literal["low", "medium", "high"]
GearWeightUnit = Literal["g", "kg", "oz", "lb"]
ContainerColor = Literal[
    # Current colors
    "default",
    "coyote",
    "khaki",
    "olive",
    "forestGreen",
    "tan",
    "brown",
    "black",
    "navy",
    "jeans",
    "gray",
    "orange",
    # Legacy colors (for backward compatibility)
    "blue",
    "yellow",
    "green",
    "indigo",
    "pink",
    "purple",
    "red",
    "teal",
]
GearItemCategory = str  # Allows custom categories: 'water', 'food', 'shelter', etc.


# Unified Schemas


class GearItemCreateV2(BaseModel):
    """Unified schema for creating a gear item or container.

    Field requirements depend on itemType:
    - itemType='container': containerType required, category/quantity must be None
    - itemType='item': category required, containerType must be None

    Examples:
        # Create container
        {
            "itemType": "container",
            "name": "Bug-out Bag",
            "containerType": "backpack",
            "parentItemId": null
        }

        # Create item
        {
            "itemType": "item",
            "name": "Water Bottle",
            "category": "water",
            "quantity": 1,
            "parentItemId": "container-id"
        }
    """

    # Core fields
    id: str | None = Field(
        None,
        description="Optional UUID for import/update workflow",
    )
    itemType: Literal["container", "item"] = Field(..., alias="itemType")
    name: str = Field(..., min_length=1, max_length=255)
    parentItemId: str | None = Field(None, alias="parentItemId")

    # Common fields
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    url: str | None = None
    color: ContainerColor | str | None = None
    notes: str | None = None

    # Container-specific fields (required if itemType='container')
    containerType: GearContainerType | None = Field(None, alias="containerType")
    maxWeight: float | None = Field(None, ge=0, alias="maxWeight")
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    hideWhenNested: bool | None = Field(default=None, alias="hideWhenNested")
    isPublic: bool | None = Field(default=None, alias="isPublic")
    isHiddenByReports: bool | None = Field(default=None, alias="isHiddenByReports")
    favorite: bool | None = Field(default=None)
    showItemImages: bool | None = Field(default=None, alias="showItemImages")

    # Item-specific fields (required if itemType='item')
    category: GearItemCategory | None = None
    quantity: int | None = Field(None, ge=1)
    status: GearItemStatus | None = None
    priority: GearItemPriority | None = None
    expirationDate: datetime | None = Field(None, alias="expirationDate")
    shelfLife: dict[str, Any] | None = Field(None, alias="shelfLife")
    quality: GearItemQuality | None = None
    wearable: bool | None = None
    consumable: bool | None = None
    orderIndex: int | None = Field(None, alias="orderIndex")
    showOnContainer: bool | None = Field(None, alias="showOnContainer")
    promoteCount: int | None = Field(None, ge=0, alias="promoteCount")

    # Linking fields
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_type_specific_fields(self) -> "GearItemCreateV2":
        """Validate that required fields are present based on itemType."""
        if self.itemType == "container":
            # Container must have containerType
            if not self.containerType:
                raise ValueError("containerType is required when itemType='container'")
            # Container cannot have item-specific fields
            if self.category is not None:
                raise ValueError("category must be None when itemType='container'")
            if self.quantity is not None:
                raise ValueError("quantity must be None when itemType='container'")

        elif self.itemType == "item":
            # Item must have category
            if not self.category:
                raise ValueError("category is required when itemType='item'")
            # Item cannot have container-specific fields
            if self.containerType is not None:
                raise ValueError("containerType must be None when itemType='item'")

        return self


class GearItemUpdateV2(BaseModel):
    """Unified schema for updating a gear item or container.

    All fields are optional. Type-specific field validation applies:
    - If itemType='container': category/quantity must be None
    - If itemType='item': containerType must be None
    """

    # Core fields (itemType cannot be changed after creation)
    name: str | None = Field(None, min_length=1, max_length=255)
    parentItemId: str | None = Field(None, alias="parentItemId")

    # Common fields
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    url: str | None = None
    color: ContainerColor | str | None = None
    notes: str | None = None

    # Container-specific fields
    containerType: GearContainerType | None = Field(None, alias="containerType")
    maxWeight: float | None = Field(None, ge=0, alias="maxWeight")
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    hideWhenNested: bool | None = Field(None, alias="hideWhenNested")
    isPublic: bool | None = Field(None, alias="isPublic")
    isHiddenByReports: bool | None = Field(None, alias="isHiddenByReports")
    favorite: bool | None = None
    showItemImages: bool | None = Field(None, alias="showItemImages")

    # Item-specific fields
    category: GearItemCategory | None = None
    quantity: int | None = Field(None, ge=1)
    status: GearItemStatus | None = None
    priority: GearItemPriority | None = None
    expirationDate: datetime | None = Field(None, alias="expirationDate")
    shelfLife: dict[str, Any] | None = Field(None, alias="shelfLife")
    quality: GearItemQuality | None = None
    wearable: bool | None = None
    consumable: bool | None = None
    orderIndex: int | None = Field(None, alias="orderIndex")
    showOnContainer: bool | None = Field(None, alias="showOnContainer")
    promoteCount: int | None = Field(None, ge=0, alias="promoteCount")

    # Linking fields
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")

    model_config = {"populate_by_name": True}


class GearItemResponseV2(BaseModel):
    """Unified schema for gear item/container responses.

    This is the response model returned by the API. It includes all fields
    from both containers and items. Clients should check itemType to determine
    which fields are populated.
    """

    # Core fields (field names match DB, aliases for JSON output)
    id: str
    user_id: str = Field(..., serialization_alias="userId")
    item_type: str = Field(..., serialization_alias="itemType")
    parent_item_id: str | None = Field(None, serialization_alias="parentItemId")

    # Common fields
    name: str
    description: str | None = None
    brand: str | None = None
    price: float | None = None
    currency: str | None = None
    weight: float | None = None
    weight_unit: str | None = Field(None, serialization_alias="weightUnit")
    url: str | None = None
    color: str | None = None
    notes: str | None = None

    # Container-specific fields (None if item_type='item')
    container_type: str | None = Field(None, serialization_alias="containerType")
    max_weight: float | None = Field(None, serialization_alias="maxWeight")
    max_weight_unit: str | None = Field(None, serialization_alias="maxWeightUnit")
    hide_when_nested: bool | None = Field(None, serialization_alias="hideWhenNested")
    is_public: bool | None = Field(None, serialization_alias="isPublic")
    is_hidden_by_reports: bool | None = Field(None, serialization_alias="isHiddenByReports")
    favorite: bool | None = None
    show_item_images: bool | None = Field(None, serialization_alias="showItemImages")

    # Item-specific fields (None if item_type='container')
    category: str | None = None
    quantity: int | None = None
    status: str | None = None
    priority: str | None = None
    expiration_date: datetime | None = Field(None, serialization_alias="expirationDate")
    shelf_life: dict[str, Any] | None = Field(None, serialization_alias="shelfLife")
    quality: str | None = None
    wearable: bool | None = None
    consumable: bool | None = None
    order_index: int | None = Field(None, serialization_alias="orderIndex")
    show_on_container: bool | None = Field(None, serialization_alias="showOnContainer")
    promote_count: int | None = Field(None, ge=0, serialization_alias="promoteCount")

    # Linking fields
    linked_item_id: str | None = Field(None, serialization_alias="linkedItemId")
    catalogue_item_id: str | None = Field(None, serialization_alias="catalogueItemId")

    # Metadata
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")

    # Optional: nested children (for tree structure responses)
    children: list["GearItemResponseV2"] | None = None

    @model_validator(mode="before")
    @classmethod
    def handle_lazy_loaded_children(cls, data: Any) -> Any:
        """Handle lazy-loaded children relationship to avoid MissingGreenlet error.

        If data is an ORM object and children are not loaded, set children to None
        to prevent Pydantic from trying to access the lazy-loaded relationship.
        """
        if hasattr(data, "__dict__"):
            # Check if this is an ORM object with unloaded children
            state = instance_state(data)
            if state and "children" in state.unloaded:
                # Children are not loaded, explicitly set to None
                if isinstance(data, dict):
                    data["children"] = None
                else:
                    # For ORM objects, we need to convert to dict to avoid lazy loading
                    data_dict = {
                        key: getattr(data, key)
                        for key in [
                            "id",
                            "user_id",
                            "item_type",
                            "parent_item_id",
                            "name",
                            "description",
                            "brand",
                            "price",
                            "currency",
                            "weight",
                            "weight_unit",
                            "url",
                            "color",
                            "notes",
                            "container_type",
                            "max_weight",
                            "max_weight_unit",
                            "hide_when_nested",
                            "is_public",
                            "is_hidden_by_reports",
                            "favorite",
                            "show_item_images",
                            "category",
                            "quantity",
                            "status",
                            "priority",
                            "expiration_date",
                            "shelf_life",
                            "quality",
                            "wearable",
                            "consumable",
                            "order_index",
                            "show_on_container",
                            "promote_count",
                            "linked_item_id",
                            "catalogue_item_id",
                            "created_at",
                            "updated_at",
                        ]
                        if hasattr(data, key)
                    }
                    data_dict["children"] = None
                    return data_dict
        return data

    model_config = {"populate_by_name": True, "from_attributes": True}


# Batch update schema for order/sorting


class GearItemBatchUpdateOrderV2(BaseModel):
    """Schema for batch updating item order (sorting).

    Used for updating orderIndex on multiple items at once.
    """

    items: list[dict[str, Any]] = Field(
        ...,
        description="List of items with id and orderIndex",
        examples=[
            [
                {"id": "item-1", "orderIndex": 0},
                {"id": "item-2", "orderIndex": 1},
            ]
        ],
    )

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate that each item has required fields."""
        for item in v:
            if "id" not in item:
                raise ValueError("Each item must have an 'id' field")
            if "orderIndex" not in item:
                raise ValueError("Each item must have an 'orderIndex' field")
        return v


# Query filters


class GearItemFiltersV2(BaseModel):
    """Query filters for fetching gear items."""

    itemType: Literal["container", "item", "all"] | None = Field("all", alias="itemType")
    parentItemId: str | None = Field(None, alias="parentItemId")
    isPublic: bool | None = Field(None, alias="isPublic")
    favorite: bool | None = None
    status: GearItemStatus | None = None
    priority: GearItemPriority | None = None
    category: GearItemCategory | None = None

    model_config = {"populate_by_name": True}


# Backward compatibility: Type conversions


def convert_container_v1_to_v2(container_v1: dict[str, Any]) -> dict[str, Any]:
    """Convert V1 container to V2 item format.

    Helper function for backward compatibility endpoints.
    """
    v2_item = {
        "id": container_v1.get("id"),
        "userId": container_v1.get("userId"),
        "itemType": "container",
        "parentItemId": container_v1.get("parentContainerId"),
        "name": container_v1.get("name"),
        "description": container_v1.get("description"),
        "brand": container_v1.get("brand"),
        "price": container_v1.get("price"),
        "weight": container_v1.get("weight"),
        "weightUnit": container_v1.get("weightUnit"),
        "url": container_v1.get("url"),
        "color": container_v1.get("color"),
        "containerType": container_v1.get("type"),
        "maxWeight": container_v1.get("maxWeight"),
        "maxWeightUnit": container_v1.get("maxWeightUnit"),
        "hideWhenNested": container_v1.get("hideWhenNested"),
        "isPublic": container_v1.get("isPublic"),
        "favorite": container_v1.get("favorite"),
        "showItemImages": container_v1.get("showItemImages"),
        "createdAt": container_v1.get("createdAt"),
        "updatedAt": container_v1.get("updatedAt"),
    }
    return {k: v for k, v in v2_item.items() if v is not None}


def convert_item_v1_to_v2(item_v1: dict[str, Any]) -> dict[str, Any]:
    """Convert V1 item to V2 item format.

    Helper function for backward compatibility endpoints.
    """
    v2_item = {
        "id": item_v1.get("id"),
        "userId": item_v1.get("userId"),
        "itemType": "item",
        "parentItemId": item_v1.get("containerId"),
        "name": item_v1.get("name"),
        "brand": item_v1.get("brand"),
        "price": item_v1.get("price"),
        "currency": item_v1.get("currency"),
        "weight": item_v1.get("weight"),
        "weightUnit": item_v1.get("weightUnit"),
        "url": item_v1.get("url"),
        "color": item_v1.get("color"),
        "notes": item_v1.get("notes"),
        "category": item_v1.get("category"),
        "quantity": item_v1.get("quantity"),
        "status": item_v1.get("status"),
        "priority": item_v1.get("priority"),
        "expirationDate": item_v1.get("expirationDate"),
        "quality": item_v1.get("quality"),
        "wearable": item_v1.get("wearable"),
        "consumable": item_v1.get("consumable"),
        "orderIndex": item_v1.get("order"),
        "showOnContainer": item_v1.get("showOnContainer"),
        "linkedItemId": item_v1.get("linkedItemId"),
        "catalogueItemId": item_v1.get("catalogueItemId"),
        "createdAt": item_v1.get("createdAt"),
        "updatedAt": item_v1.get("updatedAt"),
    }
    return {k: v for k, v in v2_item.items() if v is not None}
