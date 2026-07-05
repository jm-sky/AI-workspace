"""FastAPI dependencies for billing module."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from ...core.config import settings
from .repository import BillingRepository
from .service import BillingService
from .stripe_client import StripeClient


def get_billing_repository(db: AsyncSession = Depends(get_db)) -> BillingRepository:
    """
    Get billing repository instance.

    Args:
        db: Database session

    Returns:
        BillingRepository instance
    """
    return BillingRepository(db)


def get_stripe_client() -> StripeClient:
    """
    Get Stripe client instance.

    Returns:
        StripeClient instance
    """
    return StripeClient(
        api_key=settings.stripe.secret_key,
        webhook_secret=settings.stripe.webhook_secret,
    )


def get_billing_service(
    repository: Annotated[BillingRepository, Depends(get_billing_repository)],
    stripe_client: Annotated[StripeClient, Depends(get_stripe_client)],
) -> BillingService:
    """
    Get billing service instance.

    Args:
        repository: Billing repository
        stripe_client: Stripe client

    Returns:
        BillingService instance
    """
    return BillingService(repository=repository, stripe_client=stripe_client)


# Type aliases for dependency injection
BillingServiceDep = Annotated[BillingService, Depends(get_billing_service)]
BillingRepositoryDep = Annotated[BillingRepository, Depends(get_billing_repository)]
StripeClientDep = Annotated[StripeClient, Depends(get_stripe_client)]
