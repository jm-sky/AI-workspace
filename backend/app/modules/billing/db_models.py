"""Database models for billing module."""

from datetime import UTC, datetime
from uuid import UUID as PyUUID
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SubscriptionDB(Base):
    """SQLAlchemy model for user subscriptions."""

    __tablename__ = "subscriptions"

    # Primary Key
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )

    # Stripe IDs
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Subscription Details
    plan_tier: Mapped[str] = mapped_column(
        String(20), nullable=False, default="free", index=True
    )
    billing_interval: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", index=True
    )

    # Billing Period
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Cancellation
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Grandfathered (lifetime Pro for existing premium users)
    is_grandfathered: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "plan_tier IN ('free', 'pro', 'pro_plus')", name="valid_plan_tier"
        ),
        CheckConstraint(
            "billing_interval IN ('month', 'year')", name="valid_billing_interval"
        ),
        CheckConstraint(
            "status IN ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing')",
            name="valid_status",
        ),
    )


class StripeWebhookEventDB(Base):
    """SQLAlchemy model for Stripe webhook events audit log."""

    __tablename__ = "stripe_webhook_events"

    # Primary Key
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Stripe Event Details
    stripe_event_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Processing Status
    processed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class SubscriptionHistoryDB(Base):
    """SQLAlchemy model for subscription change history (audit trail)."""

    __tablename__ = "subscription_history"

    # Primary Key
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Foreign Keys
    subscription_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )  # Nullable because subscription might be deleted
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Event Details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    old_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    old_plan_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_plan_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    event_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Note: No constraints on event_type to allow dynamic event types like:
    # - 'subscription_activated', 'subscription_updated', 'subscription_cancelled'
    # - 'payment_succeeded', 'payment_failed'
    # - 'admin_update_*', 'admin_cancel_*' (dynamic admin actions)
    # - 'cancellation_scheduled'
