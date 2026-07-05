"""SQLAlchemy database models for gear settings.

This module provides SQLAlchemy ORM models for user-specific gear settings:
- Custom categories
- Custom container types
- Custom brands
- Preferred weight unit
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GearSettingsDB(Base):
    """SQLAlchemy model for gear settings.

    Stores user-specific gear settings including custom categories,
    container types, brands, preferred weight unit, and default currency.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        user_id: Owner of the settings
        custom_categories: JSON array of custom categories
        custom_container_types: JSON array of custom container types
        custom_brands: JSON array of custom brands
        preferred_weight_unit: Preferred weight unit (g, kg, oz, lb, auto-g-kg, auto-oz-lb)
        default_currency: Default currency (PLN, USD, EUR, GBP)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "gear_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, index=True
    )
    custom_categories: Mapped[list[dict]] = mapped_column(
        JSON, nullable=False, default=list
    )
    custom_container_types: Mapped[list[dict]] = mapped_column(
        JSON, nullable=False, default=list
    )
    custom_brands: Mapped[list[dict]] = mapped_column(
        JSON, nullable=False, default=list
    )
    preferred_weight_unit: Mapped[str | None] = mapped_column(String(10), nullable=True)
    default_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<GearSettingsDB(id={self.id}, user_id={self.user_id})>"
