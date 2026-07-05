"""Pydantic schemas for gear management endpoints.

This module defines request and response models for the gear API,
using camelCase for JSON field names to match frontend conventions.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from .validators import MAX_MARKDOWN_LENGTH, sanitize_markdown_content


# Type aliases matching frontend
GearContainerType = str  # Allows custom types: 'backpack', 'bag', 'pouch', etc.
GearItemStatus = Literal["owned", "missing", "toBuy"]
GearItemPriority = Literal["critical", "high", "medium", "low"]
GearItemQuality = Literal["low", "medium", "high"]
GearWeightUnit = Literal["g", "kg", "oz", "lb", "auto-g-kg", "auto-oz-lb"]
RatingType = Literal["owner", "user"]
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
    # Legacy colors (for backward compatibility - may exist in older data)
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


# Container Schemas
class ContainerCreate(BaseModel):
    """Schema for creating a new gear container."""

    id: str | None = Field(
        None,
        description="Optional UUID for import/update workflow (when UUID is provided in markdown export)",
    )
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=MAX_MARKDOWN_LENGTH)
    type: GearContainerType

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Sanitize markdown description content."""
        if v is None:
            return None
        return sanitize_markdown_content(v)

    color: ContainerColor | None = "default"
    parentContainerId: str | None = Field(None, alias="parentContainerId")
    brand: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)
    hideWhenNested: bool | None = Field(default=None, alias="hideWhenNested")
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    maxWeight: float | None = Field(None, ge=0, alias="maxWeight")
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    url: str | None = None
    isPublic: bool | None = Field(default=None, alias="isPublic")
    favorite: bool | None = Field(default=None)
    showItemImages: bool | None = Field(default=None, alias="showItemImages")

    model_config = {"populate_by_name": True}


class ContainerUpdate(BaseModel):
    """Schema for updating a gear container."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=MAX_MARKDOWN_LENGTH)
    type: GearContainerType | None = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Sanitize markdown description content."""
        if v is None:
            return None
        return sanitize_markdown_content(v)

    color: ContainerColor | None = None
    parentContainerId: str | None = Field(None, alias="parentContainerId")
    brand: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)
    hideWhenNested: bool | None = Field(None, alias="hideWhenNested")
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    maxWeight: float | None = Field(None, ge=0, alias="maxWeight")
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    url: str | None = None
    isPublic: bool | None = Field(default=None, alias="isPublic")
    favorite: bool | None = Field(default=None)
    showItemImages: bool | None = Field(default=None, alias="showItemImages")

    model_config = {"populate_by_name": True}


class ContainerInfo(BaseModel):
    """Minimal container information included in item responses."""

    id: str
    name: str
    type: GearContainerType
    color: ContainerColor | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class ItemResponse(BaseModel):
    """Schema for gear item response."""

    id: str
    name: str
    category: GearItemCategory
    quantity: int
    weight: float
    weightUnit: GearWeightUnit
    notes: str | None = None
    expirationDate: datetime | None = None
    shelfLife: dict[str, Any] | None = Field(
        None,
        alias="shelfLife",
        description="Shelf life period: {value: int, unit: 'days'|'months'|'years'}",
    )
    priority: GearItemPriority
    status: GearItemStatus
    containerId: str | None = Field(None, alias="containerId")
    container: ContainerInfo | None = (
        None  # Container information (id, name, type, color)
    )
    price: float | None = None
    currency: str | None = None
    url: str | None = None
    brand: str | None = None
    color: str | None = None
    quality: GearItemQuality | None = None
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")
    wearable: bool | None = None
    consumable: bool | None = None
    order: int | None = Field(None, ge=0)
    showOnContainer: bool | None = Field(None, alias="showOnContainer")
    primaryImageUrl: str | None = Field(None, alias="primaryImageUrl")
    promoteCount: int = Field(
        0, alias="promote_count", serialization_alias="promoteCount"
    )
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ContainerResponse(BaseModel):
    """Schema for gear container response."""

    id: str
    name: str
    description: str | None = None
    type: GearContainerType
    color: ContainerColor | None = "default"
    parentContainerId: str | None = Field(None, alias="parentContainerId")
    brand: str | None = None
    price: float | None = None
    hideWhenNested: bool | None = None
    weight: float | None = None
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    maxWeight: float | None = None
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    url: str | None = None
    isPublic: bool
    favorite: bool
    showItemImages: bool | None = Field(None, alias="showItemImages")
    authorName: str | None = None  # Only populated for public containers
    authorId: str | None = Field(
        None, alias="authorId"
    )  # Author user ID (only for public containers)
    items: list[ItemResponse] = []
    # Rating fields
    ownerRating: int | None = Field(None, alias="ownerRating")  # Owner's rating (1-5)
    userRating: int | None = Field(
        None, alias="userRating"
    )  # Current user's rating (if logged in)
    averageUserRating: float | None = Field(
        None, alias="averageUserRating"
    )  # Average of all user ratings
    userRatingCount: int = Field(
        default=0, alias="userRatingCount"
    )  # Number of user ratings
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# Item Schemas
class ItemCreate(BaseModel):
    """Schema for creating a new gear item."""

    id: str | None = Field(
        None,
        description="Optional UUID for import/update workflow (when UUID is provided in markdown export)",
    )
    name: str = Field(..., min_length=1, max_length=255)
    category: GearItemCategory
    quantity: int = Field(default=1, ge=1)
    weight: float = Field(..., ge=0)
    weightUnit: GearWeightUnit = Field(default="g")
    notes: str | None = Field(None, max_length=MAX_MARKDOWN_LENGTH)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        """Sanitize markdown notes content."""
        if v is None:
            return None
        return sanitize_markdown_content(v)

    expirationDate: datetime | None = Field(None, alias="expirationDate")
    shelfLife: dict[str, Any] | None = Field(
        None,
        alias="shelfLife",
        description="Shelf life period: {value: int, unit: 'days'|'months'|'years'}",
    )
    priority: GearItemPriority = Field(default="medium")
    status: GearItemStatus = Field(default="owned")
    containerId: str | None = Field(None, alias="containerId")
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    url: str | None = None
    brand: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    quality: GearItemQuality | None = None
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")
    wearable: bool | None = Field(default=None)
    consumable: bool | None = Field(default=None)
    order: int | None = Field(None, ge=0)
    showOnContainer: bool | None = Field(default=None, alias="showOnContainer")

    model_config = {"populate_by_name": True}


class ItemUpdate(BaseModel):
    """Schema for updating a gear item."""

    name: str | None = Field(None, min_length=1, max_length=255)
    category: GearItemCategory | None = None
    quantity: int | None = Field(None, ge=1)
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = None
    notes: str | None = Field(None, max_length=MAX_MARKDOWN_LENGTH)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        """Sanitize markdown notes content."""
        if v is None:
            return None
        return sanitize_markdown_content(v)

    expirationDate: datetime | None = Field(None, alias="expirationDate")
    shelfLife: dict[str, Any] | None = Field(
        None,
        alias="shelfLife",
        description="Shelf life period: {value: int, unit: 'days'|'months'|'years'}",
    )
    priority: GearItemPriority | None = None
    status: GearItemStatus | None = None
    containerId: str | None = Field(None, alias="containerId")
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    url: str | None = None
    brand: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    quality: GearItemQuality | None = None
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")
    wearable: bool | None = None
    consumable: bool | None = None
    order: int | None = Field(None, ge=0)
    showOnContainer: bool | None = Field(None, alias="showOnContainer")

    model_config = {"populate_by_name": True}


class ItemMoveRequest(BaseModel):
    """Schema for moving an item to a different container."""

    targetContainerId: str = Field(
        ...,
        alias="targetContainerId",
        description="Target container ID to move the item to",
    )

    model_config = {"populate_by_name": True}


class ItemOrderUpdate(BaseModel):
    """Schema for updating a single item's order."""

    id: str = Field(..., description="Item ID")
    order: int = Field(..., ge=0, description="New order value")


class BatchOrderUpdateRequest(BaseModel):
    """Schema for batch updating items' order."""

    items: list[ItemOrderUpdate] = Field(
        ..., min_length=1, description="List of items with their new order values"
    )

    model_config = {"populate_by_name": True}


# Share token schemas
class ShareTokenCreate(BaseModel):
    """Schema for creating a share token."""

    expiresAt: datetime | None = Field(
        None, alias="expiresAt", description="Optional expiration timestamp"
    )

    model_config = {"populate_by_name": True}


class ShareTokenResponse(BaseModel):
    """Schema for share token response."""

    token: str = Field(..., description="Share token")
    containerId: str = Field(..., alias="containerId", description="Container ID")
    expiresAt: datetime | None = Field(
        None, alias="expiresAt", description="Expiration timestamp if set"
    )
    createdAt: datetime = Field(
        ..., alias="createdAt", description="Token creation timestamp"
    )
    shareUrl: str = Field(..., alias="shareUrl", description="Full share URL")

    model_config = {"populate_by_name": True}


# Rating schemas
class ContainerRatingCreate(BaseModel):
    """Schema for creating/updating container rating."""

    rating: int = Field(..., ge=1, le=5, description="Rating value from 1 to 5")
    ratingType: RatingType = Field(
        default="user",
        alias="ratingType",
        description="Type of rating: 'owner' for owner rating, 'user' for user rating",
    )

    model_config = {"populate_by_name": True}


class ContainerRatingResponse(BaseModel):
    """Schema for container rating response."""

    id: str
    containerId: str = Field(alias="containerId")
    userId: str = Field(alias="userId")
    rating: int
    ratingType: RatingType = Field(alias="ratingType")
    createdAt: datetime = Field(alias="createdAt")
    updatedAt: datetime = Field(alias="updatedAt")

    model_config = {"from_attributes": True, "populate_by_name": True}


# Global Catalogue Schemas
class CatalogueShop(BaseModel):
    """Schema for a shop link in catalogue items."""

    url: str
    name: str | None = None
    variant: str | None = None
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    updatedAt: str | None = Field(
        None, alias="updated_at", serialization_alias="updatedAt"
    )

    model_config = {"populate_by_name": True}


class GlobalCatalogueItemBase(BaseModel):
    """Base schema for global catalogue items."""

    name: str = Field(..., min_length=1, max_length=255)
    category: GearItemCategory
    weight: float = Field(..., ge=0)
    weightUnit: GearWeightUnit = Field(
        default="g", alias="weight_unit", serialization_alias="weightUnit"
    )
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    model: str | None = Field(None, max_length=255)
    priceTier: Literal["low", "medium", "high"] | None = Field(
        None, alias="price_tier", serialization_alias="priceTier"
    )
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    quality: GearItemQuality | None = None
    url: str | None = None
    color: str | None = Field(None, max_length=50)
    shops: list[CatalogueShop] = Field(
        default_factory=list, alias="shops", serialization_alias="shops"
    )

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def validate_price_tier_before(cls, data: Any) -> Any:
        """Convert invalid price tier values to None before validation."""
        if isinstance(data, dict):
            # Handle both alias and field name
            price_tier_value = data.get("price_tier") or data.get("priceTier")
            if price_tier_value is not None:
                if isinstance(price_tier_value, str):
                    price_tier_lower = price_tier_value.lower()
                    if price_tier_lower not in ("low", "medium", "high"):
                        # Set invalid values to None
                        if "price_tier" in data:
                            data["price_tier"] = None
                        if "priceTier" in data:
                            data["priceTier"] = None
                    elif "price_tier" in data and price_tier_lower != price_tier_value:
                        # Normalize to lowercase
                        data["price_tier"] = price_tier_lower
        return data


class GlobalCatalogueItemCreate(GlobalCatalogueItemBase):
    """Schema for creating a global catalogue item."""

    pass


class GlobalCatalogueItemUpdate(BaseModel):
    """Schema for updating a global catalogue item."""

    name: str | None = Field(None, min_length=1, max_length=255)
    category: GearItemCategory | None = None
    weight: float | None = Field(None, gt=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weight_unit")
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    model: str | None = Field(None, max_length=255)
    priceTier: Literal["low", "medium", "high"] | None = Field(None, alias="price_tier")
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    quality: GearItemQuality | None = None
    url: str | None = None
    color: str | None = Field(None, max_length=50)
    shops: list[CatalogueShop] | None = Field(
        None, alias="shops", serialization_alias="shops"
    )
    isActive: bool | None = Field(None, alias="isActive")

    model_config = {"populate_by_name": True}


class GlobalCatalogueItemResponse(GlobalCatalogueItemBase):
    """Schema for global catalogue item response."""

    id: str
    version: int
    isActive: bool = Field(alias="is_active", serialization_alias="isActive")
    createdBy: str | None = Field(
        None, alias="created_by", serialization_alias="createdBy"
    )
    creatorName: str | None = Field(
        None,
        description="Creator name if profile is public, otherwise None",
        serialization_alias="creatorName",
    )
    createdAt: datetime = Field(alias="created_at", serialization_alias="createdAt")
    updatedAt: datetime = Field(alias="updated_at", serialization_alias="updatedAt")
    primaryImageUrl: str | None = Field(
        None, alias="primaryImageUrl", serialization_alias="primaryImageUrl"
    )

    model_config = {"from_attributes": True, "populate_by_name": True}


class GlobalCatalogueItemSearchParams(BaseModel):
    """Schema for catalogue item search parameters."""

    query: str | None = None
    category: GearItemCategory | None = None
    brand: str | None = None
    priceTier: Literal["low", "medium", "high"] | None = Field(None, alias="priceTier")
    quality: GearItemQuality | None = None
    isActive: bool | None = Field(True, alias="isActive")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    model_config = {"populate_by_name": True}


# Item promotion schemas
class ItemPromotionStatus(BaseModel):
    """Schema for item promotion status response."""

    promote_count: int = Field(
        ...,
        description="Current number of promotions",
        alias="promoteCount",
        serialization_alias="promoteCount",
    )
    threshold: int = Field(
        ..., description="Required number of promotions to add to catalogue"
    )
    remaining: int = Field(..., description="Remaining promotions needed")
    percentage: float = Field(..., description="Percentage progress (0-100)")
    in_catalogue: bool = Field(
        ...,
        description="Whether item is already in catalogue",
        alias="inCatalogue",
        serialization_alias="inCatalogue",
    )
    user_promoted: bool = Field(
        ...,
        description="Whether current user has already promoted this item",
        alias="userPromoted",
        serialization_alias="userPromoted",
    )
    can_promote: bool = Field(
        ...,
        description="Whether current user can promote this item",
        alias="canPromote",
        serialization_alias="canPromote",
    )

    model_config = {"populate_by_name": True}


class PromoteItemResponse(BaseModel):
    """Schema for promote item response."""

    success: bool = Field(..., description="Whether promotion was successful")
    promote_count: int = Field(..., description="Updated promotion count")
    message: str = Field(..., description="Response message")

    model_config = {"populate_by_name": True}


# Content report schemas
ReportReason = Literal["spam_fraud", "violence", "sexual_content", "profanity", "other"]
ReportStatus = Literal["pending", "reviewed", "dismissed", "action_taken"]


class ContentReportCreate(BaseModel):
    """Schema for creating a content report."""

    reason: ReportReason = Field(..., description="Reason for reporting the container")
    additionalInfo: str | None = Field(
        None,
        max_length=1000,
        alias="additionalInfo",
        serialization_alias="additionalInfo",
        description="Optional additional information",
    )

    model_config = {"populate_by_name": True}


class ContentReportResponse(BaseModel):
    """Schema for content report response."""

    id: str
    containerId: str = Field(
        ..., alias="container_id", serialization_alias="containerId"
    )
    containerName: str | None = Field(None, serialization_alias="containerName")
    reporterUserId: str = Field(
        ..., alias="reporter_user_id", serialization_alias="reporterUserId"
    )
    reporterName: str | None = Field(None, serialization_alias="reporterName")
    reason: ReportReason
    additionalInfo: str | None = Field(
        None, alias="additional_info", serialization_alias="additionalInfo"
    )
    status: ReportStatus
    createdAt: datetime = Field(
        ..., alias="created_at", serialization_alias="createdAt"
    )
    reviewedAt: datetime | None = Field(
        None, alias="reviewed_at", serialization_alias="reviewedAt"
    )
    reviewedBy: str | None = Field(
        None, alias="reviewed_by", serialization_alias="reviewedBy"
    )

    model_config = {"from_attributes": True, "populate_by_name": True}


class ContentReportUpdate(BaseModel):
    """Schema for updating a content report status."""

    status: ReportStatus = Field(..., description="New status for the report")

    model_config = {"populate_by_name": True}


class ContentReportListResponse(BaseModel):
    """Schema for list of content reports with pagination."""

    reports: list[ContentReportResponse] = Field(..., description="List of reports")
    total: int = Field(..., description="Total number of reports matching filters")
    limit: int = Field(..., description="Limit used for pagination")
    offset: int = Field(..., description="Offset used for pagination")

    model_config = {"populate_by_name": True}


class UserLimitsResponse(BaseModel):
    """Response schema for user account limits and usage."""

    tier: Literal["free", "pro", "pro_plus"]
    limits: dict[str, int] = Field(
        ..., description="Account limits (items, containers)"
    )
    usage: dict[str, int] = Field(..., description="Current usage (items, containers)")
    percentage: dict[str, float] = Field(
        ..., description="Usage percentage (items, containers)"
    )
