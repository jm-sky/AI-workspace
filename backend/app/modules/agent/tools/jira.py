"""Jira integration tool for agent loop."""

import re
from typing import Any

import httpx

from app.core.config import settings
from app.modules.agent.exceptions import AgentToolError
from app.modules.agent.tools.base import AgentTool, AgentToolDefinition
from app.modules.integrations.service import IntegrationTokenService
from app.modules.tenants.service import TenantContext


class JiraGetIssueTool(AgentTool):
    """Fetch a Jira issue and extract the Klient custom field."""

    def __init__(
        self,
        *,
        tenant_ctx: TenantContext,
        token_service: IntegrationTokenService,
    ):
        self.tenant_ctx = tenant_ctx
        self.token_service = token_service

    @property
    def definition(self) -> AgentToolDefinition:
        return AgentToolDefinition(
            name="jira_get_issue",
            description=(
                "Fetch a Jira issue by key (e.g. IT-123). Returns summary, "
                "status, description, and the Klient (client) field when present."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key, e.g. IT-123",
                    },
                },
                "required": ["issue_key"],
            },
        )

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        issue_key = str(arguments.get("issue_key", "")).strip().upper()
        if not re.match(r"^[A-Z][A-Z0-9]+-\d+$", issue_key):
            raise AgentToolError(f"Invalid Jira issue key: {issue_key}")

        base_url = settings.integrations.jira_base_url.rstrip("/")
        if not base_url:
            raise AgentToolError("JIRA_BASE_URL is not configured")

        token = await self.token_service.resolve_access_token(
            user_id=self.tenant_ctx.user_id,
            tenant_id=self.tenant_ctx.tenant_id,
            team_id=self.tenant_ctx.team_id,
            provider="jira",
        )
        client_field = settings.integrations.jira_client_field

        url = f"{base_url}/rest/api/3/issue/{issue_key}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 401:
                raise AgentToolError("Jira authentication failed — reconnect integration")
            if response.status_code == 404:
                raise AgentToolError(f"Jira issue not found: {issue_key}")
            if response.status_code >= 400:
                raise AgentToolError(
                    f"Jira API error {response.status_code}: {response.text[:500]}"
                )
            data = response.json()

        fields = data.get("fields", {})
        client_name = fields.get(client_field)
        if isinstance(client_name, dict):
            client_name = client_name.get("value") or client_name.get("name")

        return {
            "key": data.get("key", issue_key),
            "summary": fields.get("summary"),
            "status": (fields.get("status") or {}).get("name"),
            "description": _flatten_description(fields.get("description")),
            "client": client_name,
            "url": f"{base_url}/browse/{issue_key}",
        }


def _flatten_description(description: Any) -> str | None:
    if description is None:
        return None
    if isinstance(description, str):
        return description
    if isinstance(description, dict):
        return _adf_to_text(description)
    return str(description)


def _adf_to_text(node: dict[str, Any]) -> str:
    """Best-effort plain text from Atlassian Document Format."""
    parts: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            if item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            for child in item.get("content", []):
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(node)
    return "\n".join(line for line in "".join(parts).splitlines() if line.strip())
