"""Unit tests for billing service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import stripe

from app.modules.billing.db_models import SubscriptionDB
from app.modules.billing.exceptions import (
    CannotDowngradeGrandfatheredError,
    InvalidBillingIntervalError,
    InvalidPlanTierError,
    StripeAPIError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from app.modules.billing.repository import BillingRepository
from app.modules.billing.service import BillingService
from app.modules.billing.stripe_client import StripeClient


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Create a mock billing repository."""
    return AsyncMock(spec=BillingRepository)


@pytest.fixture
def mock_stripe_client() -> AsyncMock:
    """Create a mock Stripe client."""
    return AsyncMock(spec=StripeClient)


@pytest.fixture
def sample_subscription() -> SubscriptionDB:
    """Create a sample subscription for testing."""
    return SubscriptionDB(
        id=uuid4(),
        user_id="user123",
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        plan_tier="pro",
        billing_interval="monthly",
        status="active",
        current_period_start=datetime.now(UTC),
        current_period_end=datetime.now(UTC),
        cancel_at_period_end=False,
        is_grandfathered=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def billing_service(
    mock_repository: AsyncMock, mock_stripe_client: AsyncMock
) -> BillingService:
    """Create BillingService instance with mocked dependencies."""
    return BillingService(repository=mock_repository, stripe_client=mock_stripe_client)


class TestGetSubscription:
    """Tests for getting subscription details."""

    @pytest.mark.asyncio
    async def test_get_subscription_success(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        sample_subscription: SubscriptionDB,
    ) -> None:
        """Test successful subscription retrieval."""
        mock_repository.get_subscription_by_user_id.return_value = sample_subscription

        response = await billing_service.get_subscription("user123")

        assert response.userId == "user123"
        assert response.planTier == "pro"
        assert response.status == "active"
        mock_repository.get_subscription_by_user_id.assert_called_once_with("user123")

    @pytest.mark.asyncio
    async def test_get_subscription_not_found(
        self, billing_service: BillingService, mock_repository: AsyncMock
    ) -> None:
        """Test subscription not found."""
        mock_repository.get_subscription_by_user_id.return_value = None

        with pytest.raises(SubscriptionNotFoundError):
            await billing_service.get_subscription("user123")


class TestCreateCheckoutSession:
    """Tests for creating checkout sessions."""

    @pytest.mark.asyncio
    async def test_create_checkout_session_success(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        mock_stripe_client: AsyncMock,
    ) -> None:
        """Test successful checkout session creation."""
        mock_repository.get_subscription_by_user_id.return_value = None

        # Mock Stripe customer creation
        mock_customer = MagicMock()
        mock_customer.id = "cus_new123"
        mock_stripe_client.create_customer.return_value = mock_customer

        # Mock subscription creation
        mock_subscription = MagicMock()
        mock_subscription.id = uuid4()
        mock_repository.create_subscription.return_value = mock_subscription

        # Mock checkout session creation
        mock_session = MagicMock()
        mock_session.id = "cs_test123"
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe_client.create_checkout_session.return_value = mock_session

        with patch("app.modules.billing.service.settings") as mock_settings:
            mock_settings.stripe.pro_monthly_price_id = "price_pro_monthly"

            response = await billing_service.create_checkout_session(
                user_id="user123",
                plan_tier="pro",
                billing_interval="monthly",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            assert response.sessionId == "cs_test123"
            assert response.sessionUrl == "https://checkout.stripe.com/test"

    @pytest.mark.asyncio
    async def test_create_checkout_session_invalid_plan(
        self, billing_service: BillingService, mock_repository: AsyncMock
    ) -> None:
        """Test checkout session with invalid plan tier."""
        with pytest.raises(InvalidPlanTierError):
            await billing_service.create_checkout_session(
                user_id="user123",
                plan_tier="invalid",
                billing_interval="monthly",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    @pytest.mark.asyncio
    async def test_create_checkout_session_invalid_interval(
        self, billing_service: BillingService, mock_repository: AsyncMock
    ) -> None:
        """Test checkout session with invalid billing interval."""
        with pytest.raises(InvalidBillingIntervalError):
            await billing_service.create_checkout_session(
                user_id="user123",
                plan_tier="pro",
                billing_interval="invalid",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    @pytest.mark.asyncio
    async def test_create_checkout_session_already_subscribed(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        sample_subscription: SubscriptionDB,
    ) -> None:
        """Test checkout session when user already has active subscription."""
        mock_repository.get_subscription_by_user_id.return_value = sample_subscription

        with pytest.raises(SubscriptionAlreadyExistsError):
            await billing_service.create_checkout_session(
                user_id="user123",
                plan_tier="business",
                billing_interval="monthly",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )


class TestCancelSubscription:
    """Tests for cancelling subscriptions."""

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        mock_stripe_client: AsyncMock,
        sample_subscription: SubscriptionDB,
    ) -> None:
        """Test successful subscription cancellation."""
        mock_repository.get_subscription_by_user_id.return_value = sample_subscription

        # Mock Stripe cancellation
        mock_stripe_sub = MagicMock()
        mock_stripe_sub.cancel_at_period_end = True
        mock_stripe_client.cancel_subscription.return_value = mock_stripe_sub

        # Mock database update
        cancelled_subscription = sample_subscription
        cancelled_subscription.cancel_at_period_end = True
        mock_repository.update_subscription.return_value = cancelled_subscription
        mock_repository.create_subscription_history.return_value = None

        response = await billing_service.cancel_subscription("user123")

        assert response.cancelAtPeriodEnd is True
        mock_stripe_client.cancel_subscription.assert_called_once_with("sub_test123")

    @pytest.mark.asyncio
    async def test_cancel_subscription_grandfathered(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        sample_subscription: SubscriptionDB,
    ) -> None:
        """Test cancellation of grandfathered subscription (should fail)."""
        sample_subscription.is_grandfathered = True
        mock_repository.get_subscription_by_user_id.return_value = sample_subscription

        with pytest.raises(CannotDowngradeGrandfatheredError):
            await billing_service.cancel_subscription("user123")


class TestGetSubscriptionLimits:
    """Tests for getting subscription limits."""

    @pytest.mark.asyncio
    async def test_get_limits_free_tier(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        sample_subscription: SubscriptionDB,
    ) -> None:
        """Test limits for free tier."""
        sample_subscription.plan_tier = "free"
        mock_repository.get_subscription_by_user_id.return_value = sample_subscription

        response = await billing_service.get_subscription_limits("user123")

        assert response.planTier == "free"
        assert response.aiMonthlyTokenLimit == 0
        assert response.requiresByok is True
        assert response.canUseAdvancedFeatures is False

    @pytest.mark.asyncio
    async def test_get_limits_pro_tier(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        sample_subscription: SubscriptionDB,
    ) -> None:
        """Test limits for pro tier."""
        sample_subscription.plan_tier = "pro"
        mock_repository.get_subscription_by_user_id.return_value = sample_subscription

        response = await billing_service.get_subscription_limits("user123")

        assert response.planTier == "pro"
        assert response.aiMonthlyTokenLimit == 1_000_000
        assert response.requiresByok is False
        assert response.canUseAdvancedFeatures is True

    @pytest.mark.asyncio
    async def test_get_limits_business_tier(
        self,
        billing_service: BillingService,
        mock_repository: AsyncMock,
        sample_subscription: SubscriptionDB,
    ) -> None:
        """Test limits for business tier."""
        sample_subscription.plan_tier = "business"
        mock_repository.get_subscription_by_user_id.return_value = sample_subscription

        response = await billing_service.get_subscription_limits("user123")

        assert response.planTier == "business"
        assert response.aiMonthlyTokenLimit == 10_000_000
        assert response.requiresByok is False
        assert response.canUseAdvancedFeatures is True
