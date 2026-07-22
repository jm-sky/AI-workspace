"""Database models for hierarchical workspace configuration."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkspaceConfigEntryDB(Base):
    """Config entry at app, tenant, team, or user scope."""

    __tablename__ = "workspace_config_entries"
    __table_args__ = (
        UniqueConstraint(
            "scope",
            "scope_id",
            "tenant_id",
            "config_key",
            name="uq_workspace_config_scope_key",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    scope_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    config_key: Mapped[str] = mapped_column(String(100), nullable=False)
    config_value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
