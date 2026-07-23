"""SQLAlchemy database models for AI module."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AIUserSettingsDB(Base):
    """User AI settings and preferences.

    Stores user-specific AI configuration including optional personal API tokens.
    """

    __tablename__ = "ai_user_settings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Token Management
    use_own_token: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    encrypted_api_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Model Configuration
    selected_model: Mapped[str] = mapped_column(String(255), default="openai/gpt-4o-mini", nullable=False)
    max_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Context Configuration
    context_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Monthly Usage Tracking
    monthly_token_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_cost_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_cost_used: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class AIHistoryDB(Base):
    """AI interaction history with full audit trail.

    Tracks all AI requests, responses, token usage, and costs.
    """

    __tablename__ = "ai_history"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Operation Details
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(255), nullable=False)

    # Token Usage
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Data
    input_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    output_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    container_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )


class AICacheDB(Base):
    """PostgreSQL-based cache for AI responses.

    Caches AI responses with TTL to reduce costs and improve performance.
    """

    __tablename__ = "ai_cache"

    cache_key: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Cache Details
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(255), nullable=False)

    # Cached Data
    cached_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Cache Statistics
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
