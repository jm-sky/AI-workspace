"""Repository for billing operations."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID as PyUUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.billing.db_models import (
    StripeWebhookEventDB,
    SubscriptionDB,
    SubscriptionHistoryDB,
)


class BillingRepository:
    """Repository for billing database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    # ==================== Subscription Operations ====================

    async def get_subscription_by_user_id(self, user_id: str) -> SubscriptionDB | None:
        """Get subscription by user ID.

        Args:
            user_id: User ID (ULID)

        Returns:
            Subscription or None if not found
        """
        result = await self.db.execute(select(SubscriptionDB).where(SubscriptionDB.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_subscription_by_stripe_id(self, stripe_subscription_id: str) -> SubscriptionDB | None:
        """Get subscription by Stripe subscription ID.

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Subscription or None if not found
        """
        result = await self.db.execute(select(SubscriptionDB).where(SubscriptionDB.stripe_subscription_id == stripe_subscription_id))
        return result.scalar_one_or_none()

    async def get_subscription_by_customer_id(self, stripe_customer_id: str) -> SubscriptionDB | None:
        """Get subscription by Stripe customer ID.

        Args:
            stripe_customer_id: Stripe customer ID

        Returns:
            Subscription or None if not found
        """
        result = await self.db.execute(select(SubscriptionDB).where(SubscriptionDB.stripe_customer_id == stripe_customer_id))
        return result.scalar_one_or_none()

    async def get_subscription_by_id(self, subscription_id: PyUUID) -> SubscriptionDB | None:
        """Get subscription by subscription ID.

        Args:
            subscription_id: Subscription UUID

        Returns:
            Subscription or None if not found
        """
        return await self.db.get(SubscriptionDB, subscription_id)

    async def create_subscription(self, **kwargs: Any) -> SubscriptionDB:
        """Create new subscription.

        Args:
            **kwargs: Subscription fields

        Returns:
            Created subscription
        """
        subscription = SubscriptionDB(**kwargs)
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def update_subscription(self, subscription_id: PyUUID, **kwargs: Any) -> SubscriptionDB:
        """Update existing subscription.

        Args:
            subscription_id: Subscription ID to update
            **kwargs: Fields to update

        Returns:
            Updated subscription
        """
        result = await self.db.execute(select(SubscriptionDB).where(SubscriptionDB.id == subscription_id))
        subscription = result.scalar_one()

        for key, value in kwargs.items():
            if hasattr(subscription, key):
                setattr(subscription, key, value)

        subscription.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def delete_subscription(self, subscription: SubscriptionDB) -> None:
        """Delete subscription.

        Args:
            subscription: Subscription to delete
        """
        await self.db.delete(subscription)
        await self.db.commit()

    # ==================== Webhook Event Operations ====================

    async def get_webhook_event_by_stripe_id(self, stripe_event_id: str) -> StripeWebhookEventDB | None:
        """Get webhook event by Stripe event ID.

        Args:
            stripe_event_id: Stripe event ID

        Returns:
            Webhook event or None if not found
        """
        result = await self.db.execute(select(StripeWebhookEventDB).where(StripeWebhookEventDB.stripe_event_id == stripe_event_id))
        return result.scalar_one_or_none()

    async def create_webhook_event(self, stripe_event_id: str, event_type: str, payload: dict) -> StripeWebhookEventDB:
        """Create webhook event record.

        Args:
            stripe_event_id: Stripe event ID
            event_type: Event type
            payload: Event payload

        Returns:
            Created webhook event
        """
        event = StripeWebhookEventDB(
            stripe_event_id=stripe_event_id,
            event_type=event_type,
            payload=payload,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def mark_webhook_processed(self, event: StripeWebhookEventDB, error: str | None = None) -> StripeWebhookEventDB:
        """Mark webhook event as processed.

        Args:
            event: Webhook event to update
            error: Error message if processing failed

        Returns:
            Updated webhook event
        """
        event.processed = True
        event.processed_at = datetime.now(UTC)
        if error:
            event.error_message = error

        await self.db.commit()
        await self.db.refresh(event)
        return event

    # ==================== Subscription History Operations ====================

    async def create_history_entry(
        self,
        subscription_id: PyUUID | None,
        user_id: str,
        event_type: str,
        old_status: str | None,
        new_status: str,
        old_plan_tier: str | None,
        new_plan_tier: str,
        event_metadata: dict | None = None,
    ) -> SubscriptionHistoryDB:
        """Create subscription history entry.

        Args:
            subscription_id: Subscription ID
            user_id: User ID
            event_type: Event type
            old_status: Previous status
            new_status: New status
            old_plan_tier: Previous plan tier
            new_plan_tier: New plan tier
            event_metadata: Additional metadata

        Returns:
            Created history entry
        """
        history = SubscriptionHistoryDB(
            subscription_id=subscription_id,
            user_id=user_id,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            old_plan_tier=old_plan_tier,
            new_plan_tier=new_plan_tier,
            event_metadata=event_metadata,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_user_history(self, user_id: str, limit: int = 50) -> list[SubscriptionHistoryDB]:
        """Get subscription history for user.

        Args:
            user_id: User ID
            limit: Maximum number of entries

        Returns:
            List of history entries
        """
        result = await self.db.execute(select(SubscriptionHistoryDB).where(SubscriptionHistoryDB.user_id == user_id).order_by(SubscriptionHistoryDB.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    # ==================== Aliases for webhook_handler.py compatibility ====================

    async def get_subscription_by_stripe_customer_id(self, customer_id: str) -> SubscriptionDB | None:
        """Alias for get_subscription_by_customer_id."""
        return await self.get_subscription_by_customer_id(customer_id)

    async def get_subscription_by_stripe_subscription_id(self, subscription_id: str) -> SubscriptionDB | None:
        """Alias for get_subscription_by_stripe_id."""
        return await self.get_subscription_by_stripe_id(subscription_id)

    async def get_webhook_event_by_event_id(self, event_id: str) -> StripeWebhookEventDB | None:
        """Alias for get_webhook_event_by_stripe_id."""
        return await self.get_webhook_event_by_stripe_id(event_id)

    async def mark_webhook_event_processed(self, event_id: PyUUID) -> StripeWebhookEventDB:
        """Mark webhook event as processed.

        Args:
            event_id: Webhook event ID

        Returns:
            Updated webhook event
        """
        result = await self.db.execute(select(StripeWebhookEventDB).where(StripeWebhookEventDB.id == event_id))
        event = result.scalar_one()
        return await self.mark_webhook_processed(event)

    async def mark_webhook_event_failed(self, event_id: PyUUID, error: str) -> StripeWebhookEventDB:
        """Mark webhook event as failed.

        Args:
            event_id: Webhook event ID
            error: Error message

        Returns:
            Updated webhook event
        """
        result = await self.db.execute(select(StripeWebhookEventDB).where(StripeWebhookEventDB.id == event_id))
        event = result.scalar_one()
        return await self.mark_webhook_processed(event, error=error)

    async def create_subscription_history(
        self,
        subscription_id: PyUUID,
        change_type: str,
        old_value: str | None,
        new_value: str,
        reason: str | None = None,
    ) -> SubscriptionHistoryDB:
        """Create subscription history entry (simplified).

        For subscription_activated events, old_value and new_value are plan tiers.
        For other events, they are status values.

        Args:
            subscription_id: Subscription ID
            change_type: Type of change
            old_value: Old value (plan tier or status)
            new_value: New value (plan tier or status)
            reason: Reason for change

        Returns:
            Created history entry
        """
        # Get subscription to get user_id and current values
        result = await self.db.execute(select(SubscriptionDB).where(SubscriptionDB.id == subscription_id))
        subscription = result.scalar_one()

        # For subscription_activated, values are plan tiers
        if change_type == "subscription_activated":
            old_plan = old_value or "free"
            new_plan = new_value
            old_status = "active"
            new_status = "active"
        else:
            # For other events, values are statuses
            old_plan = subscription.plan_tier
            new_plan = subscription.plan_tier
            old_status = old_value or subscription.status
            new_status = new_value

        history = SubscriptionHistoryDB(
            subscription_id=subscription_id,
            user_id=subscription.user_id,
            event_type=change_type,
            old_status=old_status,
            new_status=new_status,
            old_plan_tier=old_plan,
            new_plan_tier=new_plan,
            event_metadata={"reason": reason} if reason else None,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history
