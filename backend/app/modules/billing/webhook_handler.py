"""Stripe webhook event handlers."""

import logging
from datetime import UTC, datetime
from typing import Any, cast

import stripe

from .exceptions import SubscriptionNotFoundError, WebhookProcessingError
from .repository import BillingRepository

logger = logging.getLogger(__name__)


async def handle_checkout_session_completed(
    event: stripe.Event,
    repository: BillingRepository,
) -> None:
    """
    Handle checkout.session.completed event.

    Activated when user completes payment for a new subscription.

    Args:
        event: Stripe event object
        repository: Billing repository

    Raises:
        WebhookProcessingError: If processing fails
    """
    try:
        session = cast(Any, event.data.object)
        customer_id = session.customer
        subscription_id = session.subscription

        if not customer_id or not subscription_id:
            raise WebhookProcessingError(
                "Missing customer_id or subscription_id in checkout session"
            )

        # Get subscription from database by customer ID
        subscription = await repository.get_subscription_by_stripe_customer_id(
            customer_id
        )
        if not subscription:
            raise SubscriptionNotFoundError(
                f"Subscription not found for customer {customer_id}"
            )

        # Get subscription details from Stripe
        stripe_sub = stripe.Subscription.retrieve(subscription_id)

        # Handle both dict and object access
        if hasattr(stripe_sub, "items") and hasattr(stripe_sub.items, "data"):
            price_obj = stripe_sub.items.data[0].price
            price_id = price_obj.id
            billing_interval = (
                price_obj.recurring.interval if price_obj.recurring else "month"
            )
        else:
            price_id = stripe_sub["items"]["data"][0]["price"]["id"]
            billing_interval = stripe_sub["items"]["data"][0]["price"]["recurring"][
                "interval"
            ]

        # Map price_id to plan_tier
        plan_tier = _get_plan_tier_from_price_id(price_id)

        # Get period dates from Stripe Subscription
        # Native Stripe objects use current_period_start/end
        period_start = getattr(stripe_sub, "current_period_start", None)
        period_end = getattr(stripe_sub, "current_period_end", None)

        # Fallback: calculate if not available
        if not period_start:
            period_start = getattr(stripe_sub, "billing_cycle_anchor", None) or getattr(
                stripe_sub, "start_date", None
            )

        if not period_end and period_start:
            if billing_interval == "year":
                period_end = period_start + (365 * 24 * 60 * 60)  # +1 year in seconds
            else:  # month
                period_end = period_start + (30 * 24 * 60 * 60)  # +30 days in seconds

        # Final fallback
        if not period_start:
            logger.warning(f"No period start found in subscription, using current time")
            now = int(datetime.now(UTC).timestamp())
            period_start = now
            period_end = (
                now + (30 * 24 * 60 * 60)
                if billing_interval == "month"
                else now + (365 * 24 * 60 * 60)
            )

        # Update subscription in database
        updated_subscription = await repository.update_subscription(
            subscription.id,
            stripe_subscription_id=subscription_id,
            plan_tier=plan_tier,
            billing_interval="year" if billing_interval == "year" else "month",
            status="active",
            current_period_start=(
                datetime.fromtimestamp(period_start, UTC)
                if period_start
                else datetime.now(UTC)
            ),
            current_period_end=(
                datetime.fromtimestamp(period_end, UTC)
                if period_end
                else datetime.now(UTC)
            ),
            cancel_at_period_end=False,
            updated_at=datetime.now(UTC),
        )

        # Log history
        await repository.create_subscription_history(
            subscription_id=subscription.id,
            change_type="subscription_activated",
            old_value="free",
            new_value=plan_tier,
            reason=f"Checkout session {session.id} completed",
        )

        logger.info(
            f"Activated subscription {subscription_id} for customer {customer_id}"
        )
    except Exception as e:
        logger.error(f"Failed to process checkout.session.completed: {e}")
        raise WebhookProcessingError(
            f"Failed to process checkout.session.completed: {e}"
        )


async def handle_customer_subscription_updated(
    event: stripe.Event,
    repository: BillingRepository,
) -> None:
    """
    Handle customer.subscription.updated event.

    Triggered when subscription details change (plan, status, billing cycle, etc).

    Args:
        event: Stripe event object
        repository: Billing repository

    Raises:
        WebhookProcessingError: If processing fails
    """
    try:
        stripe_sub = cast(Any, event.data.object)
        subscription_id = stripe_sub.id
        customer_id = stripe_sub.customer

        # Get subscription from database
        subscription = await repository.get_subscription_by_stripe_subscription_id(
            subscription_id
        )
        if not subscription:
            logger.warning(f"Subscription {subscription_id} not found in database")
            return

        # Extract subscription details - handle both dict and object access
        if hasattr(stripe_sub, "items") and hasattr(stripe_sub.items, "data"):
            # Object/attribute access (from webhook event)
            price_obj = stripe_sub.items.data[0].price
            price_id = price_obj.id
            billing_interval = (
                price_obj.recurring.interval if price_obj.recurring else "month"
            )
        else:
            # Dict access (from Stripe API)
            price_id = stripe_sub["items"]["data"][0]["price"]["id"]
            billing_interval = stripe_sub["items"]["data"][0]["price"]["recurring"][
                "interval"
            ]

        plan_tier = _get_plan_tier_from_price_id(price_id)

        old_plan = subscription.plan_tier
        old_status = subscription.status

        # Get period dates from Stripe Subscription
        period_start = getattr(stripe_sub, "current_period_start", None)
        period_end = getattr(stripe_sub, "current_period_end", None)

        # Fallback: calculate if not available
        if not period_start:
            period_start = getattr(stripe_sub, "billing_cycle_anchor", None) or getattr(
                stripe_sub, "start_date", None
            )

        if not period_end and period_start:
            if billing_interval == "year":
                period_end = period_start + (365 * 24 * 60 * 60)
            else:
                period_end = period_start + (30 * 24 * 60 * 60)

        # Final fallback
        if not period_start:
            now = int(datetime.now(UTC).timestamp())
            period_start = now
            period_end = (
                now + (30 * 24 * 60 * 60)
                if billing_interval == "month"
                else now + (365 * 24 * 60 * 60)
            )

        sub_status = getattr(stripe_sub, "status", "active")
        cancel_at_end = getattr(stripe_sub, "cancel_at_period_end", False)

        # Update subscription
        updated_subscription = await repository.update_subscription(
            subscription.id,
            plan_tier=plan_tier,
            billing_interval="year" if billing_interval == "year" else "month",
            status=sub_status,
            current_period_start=(
                datetime.fromtimestamp(period_start, UTC)
                if period_start
                else datetime.now(UTC)
            ),
            current_period_end=(
                datetime.fromtimestamp(period_end, UTC)
                if period_end
                else datetime.now(UTC)
            ),
            cancel_at_period_end=cancel_at_end,
            updated_at=datetime.now(UTC),
        )

        # Log history
        change_details = (
            f"plan: {old_plan} -> {plan_tier}, status: {old_status} -> {sub_status}"
        )
        await repository.create_subscription_history(
            subscription_id=subscription.id,
            change_type="subscription_updated",
            old_value=f"{old_plan}/{old_status}",
            new_value=f"{plan_tier}/{stripe_sub.status}",
            reason=f"Stripe event: {event.type}",
        )

        logger.info(f"Updated subscription {subscription_id}: {change_details}")
    except Exception as e:
        logger.error(f"Failed to process customer.subscription.updated: {e}")
        raise WebhookProcessingError(
            f"Failed to process customer.subscription.updated: {e}"
        )


async def handle_customer_subscription_deleted(
    event: stripe.Event,
    repository: BillingRepository,
) -> None:
    """
    Handle customer.subscription.deleted event.

    Triggered when subscription is cancelled and access period ends.

    Args:
        event: Stripe event object
        repository: Billing repository

    Raises:
        WebhookProcessingError: If processing fails
    """
    try:
        stripe_sub = cast(Any, event.data.object)
        subscription_id = stripe_sub.id

        # Get subscription from database
        subscription = await repository.get_subscription_by_stripe_subscription_id(
            subscription_id
        )
        if not subscription:
            logger.warning(f"Subscription {subscription_id} not found in database")
            return

        old_plan = subscription.plan_tier

        # Downgrade to free tier
        updated_subscription = await repository.update_subscription(
            subscription.id,
            plan_tier="free",
            billing_interval=None,
            status="canceled",
            cancel_at_period_end=False,
            updated_at=datetime.now(UTC),
        )

        # Log history
        await repository.create_subscription_history(
            subscription_id=subscription.id,
            change_type="subscription_cancelled",
            old_value=old_plan,
            new_value="free",
            reason=f"Subscription {subscription_id} deleted",
        )

        logger.info(f"Cancelled subscription {subscription_id}, downgraded to free")
    except Exception as e:
        logger.error(f"Failed to process customer.subscription.deleted: {e}")
        raise WebhookProcessingError(
            f"Failed to process customer.subscription.deleted: {e}"
        )


async def handle_invoice_payment_succeeded(
    event: stripe.Event,
    repository: BillingRepository,
) -> None:
    """
    Handle invoice.payment_succeeded event.

    Triggered when payment for subscription invoice succeeds.

    Args:
        event: Stripe event object
        repository: Billing repository

    Raises:
        WebhookProcessingError: If processing fails
    """
    try:
        invoice = cast(Any, event.data.object)

        # Handle both dict and object access for subscription field
        if hasattr(invoice, "subscription"):
            subscription_id = invoice.subscription
            # If it's an object, get the ID
            if hasattr(subscription_id, "id"):
                subscription_id = subscription_id.id
        else:
            subscription_id = (
                invoice.get("subscription") if isinstance(invoice, dict) else None
            )

        if not subscription_id:
            # Not a subscription invoice
            return

        # Get subscription from database
        subscription = await repository.get_subscription_by_stripe_subscription_id(
            subscription_id
        )
        if not subscription:
            logger.warning(f"Subscription {subscription_id} not found in database")
            return

        # Update status to active if it was past_due or unpaid
        if subscription.status in ["past_due", "unpaid"]:
            await repository.update_subscription(
                subscription.id,
                status="active",
                updated_at=datetime.now(UTC),
            )

            await repository.create_subscription_history(
                subscription_id=subscription.id,
                change_type="payment_succeeded",
                old_value=subscription.status,
                new_value="active",
                reason=f"Invoice {invoice.id} payment succeeded",
            )

            logger.info(f"Payment succeeded for subscription {subscription_id}")
    except Exception as e:
        logger.error(f"Failed to process invoice.payment_succeeded: {e}")
        raise WebhookProcessingError(
            f"Failed to process invoice.payment_succeeded: {e}"
        )


async def handle_invoice_payment_failed(
    event: stripe.Event,
    repository: BillingRepository,
) -> None:
    """
    Handle invoice.payment_failed event.

    Triggered when payment for subscription invoice fails.

    Args:
        event: Stripe event object
        repository: Billing repository

    Raises:
        WebhookProcessingError: If processing fails
    """
    try:
        invoice = cast(Any, event.data.object)

        # Handle both dict and object access for subscription field
        if hasattr(invoice, "subscription"):
            subscription_id = invoice.subscription
            # If it's an object, get the ID
            if hasattr(subscription_id, "id"):
                subscription_id = subscription_id.id
        else:
            subscription_id = (
                invoice.get("subscription") if isinstance(invoice, dict) else None
            )

        if not subscription_id:
            # Not a subscription invoice
            return

        # Get subscription from database
        subscription = await repository.get_subscription_by_stripe_subscription_id(
            subscription_id
        )
        if not subscription:
            logger.warning(f"Subscription {subscription_id} not found in database")
            return

        # Update status to past_due
        await repository.update_subscription(
            subscription.id,
            status="past_due",
            updated_at=datetime.now(UTC),
        )

        await repository.create_subscription_history(
            subscription_id=subscription.id,
            change_type="payment_failed",
            old_value=subscription.status,
            new_value="past_due",
            reason=f"Invoice {invoice.id} payment failed",
        )

        logger.warning(f"Payment failed for subscription {subscription_id}")
    except Exception as e:
        logger.error(f"Failed to process invoice.payment_failed: {e}")
        raise WebhookProcessingError(f"Failed to process invoice.payment_failed: {e}")


def _get_plan_tier_from_price_id(price_id: str) -> str:
    """
    Map Stripe price ID to plan tier.

    Args:
        price_id: Stripe price ID

    Returns:
        Plan tier (pro or business)

    Raises:
        WebhookProcessingError: If price_id doesn't match any known plan
    """
    from ...core.config import settings

    price_map = {
        settings.stripe.pro_monthly_price_id: "pro",
        settings.stripe.pro_annual_price_id: "pro",
        settings.stripe.pro_plus_monthly_price_id: "pro_plus",
        settings.stripe.pro_plus_annual_price_id: "pro_plus",
    }

    plan_tier = price_map.get(price_id)
    if not plan_tier:
        raise WebhookProcessingError(f"Unknown price_id: {price_id}")

    return plan_tier


# Event handler mapping
WEBHOOK_HANDLERS: dict[str, Any] = {
    "checkout.session.completed": handle_checkout_session_completed,
    "customer.subscription.updated": handle_customer_subscription_updated,
    "customer.subscription.deleted": handle_customer_subscription_deleted,
    "invoice.payment_succeeded": handle_invoice_payment_succeeded,
    "invoice.payment_failed": handle_invoice_payment_failed,
}
