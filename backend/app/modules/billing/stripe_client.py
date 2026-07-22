"""Stripe SDK wrapper for billing operations."""

import logging
from typing import Any, cast

import stripe

logger = logging.getLogger(__name__)


class StripeClient:
    """Wrapper for Stripe SDK operations."""

    def __init__(self, api_key: str, webhook_secret: str):
        """Initialize Stripe client.

        Args:
            api_key: Stripe secret API key
            webhook_secret: Stripe webhook signing secret
        """
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret

    # ==================== Customer Operations ====================

    async def create_customer(self, email: str, name: str, user_id: str) -> stripe.Customer:
        """Create Stripe customer.

        Args:
            email: Customer email
            name: Customer name
            user_id: Internal user ID for metadata

        Returns:
            Stripe Customer object
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id},
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    async def get_customer(self, customer_id: str) -> stripe.Customer:
        """Get Stripe customer by ID.

        Args:
            customer_id: Stripe customer ID

        Returns:
            Stripe Customer object
        """
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            raise

    async def update_customer(self, customer_id: str, **kwargs: Any) -> stripe.Customer:
        """Update Stripe customer.

        Args:
            customer_id: Stripe customer ID
            **kwargs: Fields to update

        Returns:
            Updated Stripe Customer object
        """
        try:
            return stripe.Customer.modify(customer_id, **kwargs)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update customer {customer_id}: {e}")
            raise

    # ==================== Checkout Session Operations ====================

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict | None = None,
    ) -> stripe.checkout.Session:
        """Create Stripe Checkout session.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            metadata: Additional metadata

        Returns:
            Stripe Checkout Session object
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                mode="subscription",
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                allow_promotion_codes=True,
                billing_address_collection="auto",
                metadata=metadata or {},
            )
            logger.info(f"Created checkout session {session.id} for customer {customer_id}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    # ==================== Billing Portal Operations ====================

    async def create_portal_session(self, customer_id: str, return_url: str) -> stripe.billing_portal.Session:
        """Create Stripe Billing Portal session.

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal

        Returns:
            Stripe Billing Portal Session object
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            logger.info(f"Created portal session for customer {customer_id}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session: {e}")
            raise

    # ==================== Subscription Operations ====================

    async def get_subscription(self, subscription_id: str) -> stripe.Subscription:
        """Get Stripe subscription by ID.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Stripe Subscription object
        """
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
            raise

    async def cancel_subscription(self, subscription_id: str, cancel_at_period_end: bool = True) -> stripe.Subscription:
        """Cancel Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID
            cancel_at_period_end: If True, cancel at period end. If False, cancel immediately.

        Returns:
            Updated Stripe Subscription object
        """
        try:
            if cancel_at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
                logger.info(f"Scheduled subscription {subscription_id} for cancellation at period end")
            else:
                subscription = stripe.Subscription.cancel(subscription_id)
                logger.info(f"Immediately canceled subscription {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            raise

    async def update_subscription(self, subscription_id: str, **kwargs: Any) -> stripe.Subscription:
        """Update Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID
            **kwargs: Fields to update

        Returns:
            Updated Stripe Subscription object
        """
        try:
            return stripe.Subscription.modify(subscription_id, **kwargs)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription {subscription_id}: {e}")
            raise

    # ==================== Webhook Operations ====================

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> stripe.Event:
        """Verify and construct webhook event.

        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header value

        Returns:
            Verified Stripe Event object

        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        try:
            # Stripe SDK expects the raw bytes exactly as received
            event = stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
            logger.info(f"Webhook signature verified: {event.type} ({event.id})")
            return cast(stripe.Event, event)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise

    async def verify_webhook_signature(self, payload: str, signature: str) -> stripe.Event:
        """Verify webhook signature and construct event (async alias).

        Args:
            payload: Raw request body as string
            signature: Stripe-Signature header value

        Returns:
            Verified Stripe Event object

        Raises:
            stripe.error.SignatureVerificationError: If signature is invalid
        """
        return self.construct_webhook_event(payload.encode(), signature)

    # ==================== Price Operations ====================

    async def get_price(self, price_id: str) -> stripe.Price:
        """Get Stripe price by ID.

        Args:
            price_id: Stripe price ID

        Returns:
            Stripe Price object
        """
        try:
            return stripe.Price.retrieve(price_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve price {price_id}: {e}")
            raise
