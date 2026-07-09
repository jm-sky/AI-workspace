"""Redaction for the PII-safe summary tier of the agent trace.

The full payload is kept in the raw tier (admin-only, retention-bounded). The
summary tier that any run-owner can see is truncated and has secret-looking keys
masked, so long client data (issue bodies, email contents) and credentials are
not bulk-exposed in the normal audit view.
"""

from typing import Any

# Substrings that mark a key as a secret regardless of nesting.
SENSITIVE_KEY_HINTS: tuple[str, ...] = (
    "token",
    "authorization",
    "secret",
    "password",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "cookie",
    "bearer",
    "credential",
)

REDACTED = "[redacted]"
MAX_STRING = 500
MAX_LIST = 20
MAX_DEPTH = 6


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(hint in lowered for hint in SENSITIVE_KEY_HINTS)


def redact_payload(value: Any, *, _depth: int = 0) -> Any:
    """Return a PII-safe copy: mask secret keys, truncate long strings/lists."""
    if _depth >= MAX_DEPTH:
        return "…"

    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(key, str) and _is_sensitive_key(key):
                out[key] = REDACTED
            else:
                out[key] = redact_payload(item, _depth=_depth + 1)
        return out

    if isinstance(value, (list, tuple)):
        trimmed = list(value)[:MAX_LIST]
        result = [redact_payload(item, _depth=_depth + 1) for item in trimmed]
        overflow = len(value) - MAX_LIST
        if overflow > 0:
            result.append(f"…(+{overflow} more)")
        return result

    if isinstance(value, str) and len(value) > MAX_STRING:
        return value[:MAX_STRING] + f"…(+{len(value) - MAX_STRING} chars)"

    return value
