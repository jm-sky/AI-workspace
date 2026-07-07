"""Signed OAuth state for integration connect flows."""

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.modules.integrations.exceptions import IntegrationOAuthStateError


def _signing_key() -> str:
    return settings.security.secret_key


def create_integration_oauth_state(payload: dict[str, Any]) -> str:
    """Create a signed, time-limited OAuth state token."""
    data = {
        **payload,
        "nonce": secrets.token_urlsafe(16),
        "exp": (datetime.now(UTC) + timedelta(minutes=10)).timestamp(),
    }
    raw = base64.urlsafe_b64encode(json.dumps(data, sort_keys=True).encode()).decode()
    signature = hmac.new(
        _signing_key().encode(),
        raw.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{raw}.{signature}"


def verify_integration_oauth_state(state: str) -> dict[str, Any]:
    """Verify signature and expiry; return decoded payload."""
    try:
        raw, signature = state.rsplit(".", 1)
    except ValueError as exc:
        raise IntegrationOAuthStateError("Malformed OAuth state") from exc

    expected = hmac.new(
        _signing_key().encode(),
        raw.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise IntegrationOAuthStateError("Invalid OAuth state signature")

    try:
        data: dict[str, Any] = json.loads(base64.urlsafe_b64decode(raw.encode()))
    except (json.JSONDecodeError, ValueError) as exc:
        raise IntegrationOAuthStateError("Invalid OAuth state payload") from exc

    expires_at = data.get("exp")
    if not isinstance(expires_at, (int, float)) or expires_at < datetime.now(UTC).timestamp():
        raise IntegrationOAuthStateError("OAuth state expired")

    return data
