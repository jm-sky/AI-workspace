"""Gmail REST API client for MCP tools."""

from __future__ import annotations

import base64
import re
from email.utils import parsedate_to_datetime
from typing import Any, cast

import httpx

from app.modules.agent.exceptions import AgentToolError


class GmailApiClient:
    """Thin Gmail API v1 client (readonly)."""

    API_BASE = "https://gmail.googleapis.com/gmail/v1"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": "ai-workspace-mcp-gmail",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        url = f"{self.API_BASE}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                url,
                headers=self._headers,
                params=params,
            )
            if response.status_code == 401:
                raise AgentToolError("Gmail authentication failed — reconnect integration")
            if response.status_code == 403:
                raise AgentToolError(
                    "Gmail API permission denied — ensure gmail.readonly scope and Gmail API enabled"
                )
            if response.status_code == 404:
                raise AgentToolError(f"Gmail resource not found: {path}")
            if response.status_code >= 400:
                raise AgentToolError(f"Gmail API error {response.status_code}: {response.text[:500]}")
            if response.status_code == 204:
                return {}
            return cast(dict[str, Any] | list[Any], response.json())

    async def list_messages(
        self,
        *,
        query: str | None = None,
        label_ids: list[str] | None = None,
        max_results: int = 15,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "maxResults": max(1, min(max_results, 50)),
        }
        if query:
            params["q"] = query
        if label_ids:
            params["labelIds"] = label_ids
        if page_token:
            params["pageToken"] = page_token

        data = await self._request("GET", "/users/me/messages", params=params)
        if not isinstance(data, dict):
            return {"messages": [], "nextPageToken": None, "resultSizeEstimate": 0}

        stubs = data.get("messages") or []
        messages: list[dict[str, Any]] = []
        for stub in stubs:
            mid = stub.get("id")
            if not mid:
                continue
            try:
                messages.append(await self.get_message(mid, format="metadata"))
            except AgentToolError:
                messages.append({"id": mid, "threadId": stub.get("threadId")})

        return {
            "messages": messages,
            "nextPageToken": data.get("nextPageToken"),
            "resultSizeEstimate": data.get("resultSizeEstimate"),
        }

    async def get_message(
        self,
        message_id: str,
        *,
        format: str = "full",
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"format": format}
        if format == "metadata":
            params["metadataHeaders"] = ["From", "To", "Cc", "Subject", "Date"]
        data = await self._request("GET", f"/users/me/messages/{message_id}", params=params)
        if not isinstance(data, dict):
            raise AgentToolError("Unexpected Gmail message payload")
        return _normalize_message(data, include_body=format == "full")


def _header_map(payload: dict[str, Any]) -> dict[str, str]:
    headers = (payload.get("headers") or []) if payload else []
    out: dict[str, str] = {}
    for item in headers:
        name = (item.get("name") or "").lower()
        value = item.get("value")
        if name and value is not None:
            out[name] = str(value)
    return out


def _decode_body_data(data: str | None) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_text_body(payload: dict[str, Any] | None) -> str:
    if not payload:
        return ""
    mime = (payload.get("mimeType") or "").lower()
    body = payload.get("body") or {}
    data = body.get("data")
    if mime == "text/plain" and data:
        return _decode_body_data(data)
    if mime == "text/html" and data:
        html = _decode_body_data(data)
        return _strip_html(html)
    parts = payload.get("parts") or []
    plain_parts: list[str] = []
    html_parts: list[str] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        nested = _extract_text_body(part)
        part_mime = (part.get("mimeType") or "").lower()
        if part_mime == "text/plain" and nested:
            plain_parts.append(nested)
        elif part_mime == "text/html" and nested:
            html_parts.append(nested)
        elif nested:
            plain_parts.append(nested)
    if plain_parts:
        return "\n\n".join(plain_parts)
    if html_parts:
        return "\n\n".join(html_parts)
    if data:
        return _decode_body_data(data)
    return ""


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<br\s*/?>", "\n", text)
    text = re.sub(r"(?s)</p>", "\n\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize_message(item: dict[str, Any], *, include_body: bool) -> dict[str, Any]:
    payload = item.get("payload") or {}
    headers = _header_map(payload)
    date_raw = headers.get("date")
    date_iso = None
    if date_raw:
        try:
            date_iso = parsedate_to_datetime(date_raw).isoformat()
        except Exception:
            date_iso = date_raw

    result: dict[str, Any] = {
        "id": item.get("id"),
        "threadId": item.get("threadId"),
        "snippet": item.get("snippet"),
        "labelIds": item.get("labelIds") or [],
        "from": headers.get("from"),
        "to": headers.get("to"),
        "cc": headers.get("cc"),
        "subject": headers.get("subject"),
        "date": date_iso,
        "internalDate": item.get("internalDate"),
    }
    if include_body:
        body = _extract_text_body(payload)
        # Cap body size for model context.
        if len(body) > 20_000:
            body = body[:20_000] + "\n\n[truncated]"
        result["bodyText"] = body or None
    return result
