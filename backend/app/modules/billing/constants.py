"""Constants for billing module."""

# Webhook endpoint paths that require raw body (no JSON modification)
# These paths are excluded from ConvertEmptyStringsToNoneMiddleware
# to preserve raw payload bytes for Stripe signature verification
WEBHOOK_PATHS = [
    "/api/billing/webhook",
    "/api/billing/webhooks/stripe",
]
