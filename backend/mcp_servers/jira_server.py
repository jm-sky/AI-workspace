"""Thin MCP server for Jira — mirrors agent tool `jira_get_issue`.

Run: MCP_USER_ACCESS_TOKEN=... JIRA_BASE_URL=... python -m mcp_servers.jira_server
"""

from __future__ import annotations

import json
import os
from typing import Any

# Minimal MCP-style tool surface for external clients.
# Production agent loop uses app.modules.agent.tools.jira in-process.


def jira_get_issue(issue_key: str, *, access_token: str, base_url: str, client_field: str) -> dict[str, Any]:
    import httpx

    url = f"{base_url.rstrip('/')}/rest/api/3/issue/{issue_key.upper()}"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    response = httpx.get(url, headers=headers, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    fields = data.get("fields", {})
    client_name = fields.get(client_field)
    if isinstance(client_name, dict):
        client_name = client_name.get("value") or client_name.get("name")
    return {
        "key": data.get("key"),
        "summary": fields.get("summary"),
        "status": (fields.get("status") or {}).get("name"),
        "client": client_name,
        "url": f"{base_url.rstrip('/')}/browse/{issue_key.upper()}",
    }


def main() -> None:
    token = os.environ.get("MCP_USER_ACCESS_TOKEN", "")
    base_url = os.environ.get("JIRA_BASE_URL", "")
    client_field = os.environ.get("JIRA_CLIENT_FIELD", "customfield_10001")
    if not token or not base_url:
        raise SystemExit("Set MCP_USER_ACCESS_TOKEN and JIRA_BASE_URL")

    print(json.dumps({
        "server": "jira-mcp",
        "tools": ["jira_get_issue"],
        "note": "Use agent module in-process tools for production",
    }))


if __name__ == "__main__":
    main()
