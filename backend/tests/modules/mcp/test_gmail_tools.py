"""Tests for Gmail MCP helpers and OAuth URL building."""

from urllib.parse import parse_qs, urlparse

import pytest

from app.modules.integrations.providers.gmail import GmailIntegrationProvider
from app.modules.integrations.types import DEFAULT_GMAIL_SCOPES
from app.modules.mcp.gmail.client import _extract_text_body, _normalize_message, _strip_html
from app.modules.mcp.gmail.tools import execute_gmail_tool


def test_default_gmail_scopes_include_readonly():
    assert "openid" in DEFAULT_GMAIL_SCOPES
    assert "https://www.googleapis.com/auth/gmail.readonly" in DEFAULT_GMAIL_SCOPES
    assert "https://www.googleapis.com/auth/userinfo.email" in DEFAULT_GMAIL_SCOPES


def test_gmail_auth_url_contains_offline_and_readonly(monkeypatch):
    provider = GmailIntegrationProvider()
    monkeypatch.setattr(provider, "_client_id", lambda: "cid")
    monkeypatch.setattr(provider, "_client_secret", lambda: "secret")
    monkeypatch.setattr(
        provider,
        "_redirect_uri",
        lambda: "http://localhost:5176/settings/integrations/callback/gmail",
    )

    url = provider.get_authorization_url(state="abc", scopes=DEFAULT_GMAIL_SCOPES)
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    assert qs["access_type"] == ["offline"]
    assert qs["prompt"] == ["consent"]
    assert "gmail.readonly" in qs["scope"][0]
    assert qs["state"] == ["abc"]


def test_strip_html_keeps_text():
    assert "Hello" in _strip_html("<p>Hello <b>world</b></p>")


def test_extract_plain_from_multipart():
    payload = {
        "mimeType": "multipart/alternative",
        "parts": [
            {
                "mimeType": "text/plain",
                "body": {
                    # "hello" urlsafe b64
                    "data": "aGVsbG8=",
                },
            },
            {
                "mimeType": "text/html",
                "body": {"data": "PGI+aGVsbG88L2I+"},
            },
        ],
    }
    assert _extract_text_body(payload) == "hello"


def test_normalize_message_headers():
    item = {
        "id": "m1",
        "threadId": "t1",
        "snippet": "hi",
        "labelIds": ["INBOX"],
        "payload": {
            "headers": [
                {"name": "From", "value": "a@example.com"},
                {"name": "Subject", "value": "Hello"},
                {"name": "Date", "value": "Wed, 01 Jan 2020 12:00:00 +0000"},
            ],
            "mimeType": "text/plain",
            "body": {"data": "Ym9keQ=="},
        },
    }
    msg = _normalize_message(item, include_body=True)
    assert msg["id"] == "m1"
    assert msg["from"] == "a@example.com"
    assert msg["subject"] == "Hello"
    assert msg["bodyText"] == "body"


@pytest.mark.asyncio
async def test_execute_gmail_search_requires_query():
    class Dummy:
        pass

    result = await execute_gmail_tool(Dummy(), "gmail_search_messages", {})  # type: ignore[arg-type]
    assert "error" in result


@pytest.mark.asyncio
async def test_execute_gmail_search_dispatches():
    class DummyClient:
        async def list_messages(self, **kwargs):
            assert kwargs["query"] == "from:a@b.com"
            return {"messages": [{"id": "1"}], "resultSizeEstimate": 1}

    result = await execute_gmail_tool(
        DummyClient(),  # type: ignore[arg-type]
        "gmail_search_messages",
        {"query": "from:a@b.com", "limit": 5},
    )
    assert result["messages"][0]["id"] == "1"
