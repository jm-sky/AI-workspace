"""Custom exceptions for billing module."""


class BillingException(Exception):
    """Base exception for billing errors."""

    pass


class SubscriptionNotFoundError(BillingException):
    """Raised when subscription is not found."""

    pass


class StripeCustomerNotFoundError(BillingException):
    """Raised when Stripe customer is not found."""

    pass


class StripeSubscriptionNotFoundError(BillingException):
    """Raised when Stripe subscription is not found."""

    pass


class InvalidPlanTierError(BillingException):
    """Raised when plan tier is invalid."""

    pass


class InvalidBillingIntervalError(BillingException):
    """Raised when billing interval is invalid."""

    pass


class SubscriptionAlreadyExistsError(BillingException):
    """Raised when user already has an active subscription."""

    pass


class CannotDowngradeGrandfatheredError(BillingException):
    """Raised when attempting to downgrade a grandfathered subscription."""

    pass


class StripeAPIError(BillingException):
    """Raised when Stripe API call fails."""

    pass


class WebhookValidationError(BillingException):
    """Raised when webhook signature validation fails."""

    pass


class WebhookProcessingError(BillingException):
    """Raised when webhook event processing fails."""

    pass


class InsufficientPermissionsError(BillingException):
    """Raised when user lacks permissions for subscription operation."""

    pass


class FreeTrierRequiresBYOKError(BillingException):
    """Raised when Free tier user tries to use AI without OpenRouter token."""

    pass
