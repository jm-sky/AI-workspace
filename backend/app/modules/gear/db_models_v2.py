"""SQLAlchemy database models for unified gear management (V2).

This module provides the unified SQLAlchemy ORM model where containers are items
with item_type='container'. This replaces the dual-model approach (GearContainerDB + GearItemDB)
with a single unified model.

Architecture:
- Single table: gear_items_v2
- Type discriminator: item_type ('container' | 'item')
- Unified nesting: parent_item_id (self-referential FK)
- Polymorphic inheritance for type-specific behavior

Benefits:
- O(1) lookups (no nested iterations)
- Arbitrary nesting depth
- Simpler schema and reduced joins
- Foundation for future features (tags, custom fields)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GearItemDBV2(Base):
    """Unified SQLAlchemy model for gear items and containers.

    This model replaces both GearContainerDB and GearItemDB with a single unified model.
    Containers are now items with item_type='container'.

    Type Discriminator:
        item_type: 'container' | 'item'

    Nesting:
        - parent_item_id: Parent item/container ID (replaces parent_container_id + container_id)
        - Self-referential relationship for arbitrary depth nesting

    Field Mapping from old models:
        GearContainerDB.id → id (preserved)
        GearContainerDB.parent_container_id → parent_item_id
        GearContainerDB.type → container_type
        GearItemDB.id → id (preserved)
        GearItemDB.container_id → parent_item_id
        GearItemDB.order → order_index (renamed, SQL keyword)
        GearItemDB.nested_container_id → REMOVED (legacy, unused)

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        user_id: Owner of the item/container
        item_type: Type discriminator ('container' | 'item')
        parent_item_id: Parent item ID (for nesting)

        # Common fields (from both old models)
        name: Item/container name
        description: Optional description
        brand: Manufacturer/brand
        price: Price value
        currency: Currency code (PLN, USD, EUR, etc.)
        weight: Weight value
        weight_unit: Weight unit (g, kg, oz, lb)
        url: Product URL
        color: Color theme
        notes: Optional notes

        # Container-specific fields (nullable for items)
        container_type: Container type (backpack, bag, pouch, etc.)
        max_weight: Maximum weight capacity
        max_weight_unit: Max weight unit
        hide_when_nested: Hide container when nested
        is_public: Public visibility flag
        is_hidden_by_reports: Hidden due to content reports (3+ reports)
        favorite: Favorite flag
        show_item_images: Show item images in gallery

        # Item-specific fields (nullable for containers)
        category: Item category (water, food, shelter, etc.)
        quantity: Item quantity
        status: Item status (owned, missing, toBuy)
        priority: Item priority (critical, high, medium, low)
        expiration_date: Optional expiration date
        shelf_life: Shelf life before purchase (e.g., {"value": 12, "unit": "months"})
        quality: Quality tier (low, medium, high)
        wearable: Whether item is worn on person
        consumable: Whether item is consumed
        order_index: Manual order (renamed from 'order')
        show_on_container: Show in container gallery
        promote_count: Number of promotions to catalogue

        # Linking fields
        linked_item_id: Link to another item (for duplicates)
        catalogue_item_id: Link to global catalogue item

        # Metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp

        # Relationships
        parent: Parent item (self-referential)
        children: Child items (self-referential)
    """

    __tablename__ = "gear_items_v2"

    # Identity
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # TYPE DISCRIMINATOR
    item_type: Mapped[str] = mapped_column(String(20), default="item", nullable=False, index=True)

    # UNIFIED NESTING (self-referential FK)
    parent_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("gear_items_v2.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Common fields (from both old models)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_unit: Mapped[str | None] = mapped_column(String(5), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Container-specific fields (nullable for items)
    container_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    max_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_weight_unit: Mapped[str | None] = mapped_column(String(5), nullable=True)
    # No column defaults — repository sets values for containers; items must stay NULL
    # (see check_item_fields / check_container_fields DB constraints).
    hide_when_nested: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_public: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)
    is_hidden_by_reports: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)
    favorite: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)
    show_item_images: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Item-specific fields (nullable for containers)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    shelf_life: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    wearable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    consumable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    order_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    show_on_container: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    promote_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Linking fields
    linked_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("gear_items_v2.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    catalogue_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("global_catalogue_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Self-referential relationships
    parent: Mapped[GearItemDBV2 | None] = relationship(
        "GearItemDBV2",
        remote_side=[id],
        foreign_keys=[parent_item_id],
        back_populates="children",
    )
    children: Mapped[list[GearItemDBV2]] = relationship(
        "GearItemDBV2",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_item_id],
    )

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_on": item_type,
        "polymorphic_identity": "item",
    }

    def __repr__(self) -> str:
        return f"<GearItemDBV2(id={self.id}, name={self.name}, type={self.item_type})>"


# Type-specific subclasses for better type hints and behavior


class GearContainerDBV2(GearItemDBV2):
    """Container-specific subclass (item_type='container').

    This subclass provides type-specific behavior for containers.
    It's optional but useful for polymorphic queries and type hints.
    """

    __mapper_args__ = {
        "polymorphic_identity": "container",
    }

    def __repr__(self) -> str:
        return f"<GearContainerDBV2(id={self.id}, name={self.name}, type={self.container_type})>"
