"""SQLAlchemy database models for feature limits."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FeatureLimitDB(Base):
    """SQLAlchemy model for feature limits.

    Stores limits for AI and storage features per user role.
    Each role has one limit configuration.

    Attributes:
        id: Unique identifier (UUID)
        role: User role (user, premium, admin, owner)
        ai_limit: AI usage limit in USD (NULL = unlimited)
        storage_limit_bytes: Storage limit in bytes
        description: Optional description of the limit
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "feature_limits"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ai_limit: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    storage_limit_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (CheckConstraint("role IN ('user', 'premium', 'admin', 'owner')", name="valid_role"),)
