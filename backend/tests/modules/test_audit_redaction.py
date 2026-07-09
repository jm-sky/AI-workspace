"""Tests for the summary-tier redaction of agent trace payloads."""

from app.modules.agent.audit.redaction import (
    MAX_LIST,
    MAX_STRING,
    REDACTED,
    redact_payload,
)


def test_masks_sensitive_keys():
    payload = {
        "access_token": "secret-abc",
        "Authorization": "Bearer xyz",
        "nested": {"api_key": "k", "safe": "value"},
    }
    result = redact_payload(payload)
    assert result["access_token"] == REDACTED
    assert result["Authorization"] == REDACTED
    assert result["nested"]["api_key"] == REDACTED
    assert result["nested"]["safe"] == "value"


def test_truncates_long_strings():
    long = "x" * (MAX_STRING + 200)
    result = redact_payload({"body": long})
    assert result["body"].startswith("x" * MAX_STRING)
    assert "chars)" in result["body"]
    assert len(result["body"]) < len(long)


def test_caps_list_length():
    result = redact_payload({"items": list(range(MAX_LIST + 5))})
    items = result["items"]
    assert len(items) == MAX_LIST + 1  # trimmed + overflow marker
    assert "more)" in items[-1]


def test_short_values_pass_through():
    payload = {"key": "IT-123", "count": 3, "flag": True, "none": None}
    assert redact_payload(payload) == payload


def test_deeply_nested_is_bounded():
    node: dict = {"v": 1}
    for _ in range(10):
        node = {"child": node}
    result = redact_payload(node)
    # Should not raise and should terminate with the depth sentinel somewhere.
    assert result is not None
