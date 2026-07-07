"""GitLab integration tool for agent loop."""

from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.modules.agent.exceptions import AgentToolError
from app.modules.agent.tools.base import AgentTool, AgentToolDefinition
from app.modules.integrations.service import IntegrationTokenService


class GitLabSearchByJiraKeyTool(AgentTool):
    """Search GitLab merge requests and issues referencing a Jira key."""

    def __init__(
        self,
        *,
        user_id: str,
        token_service: IntegrationTokenService,
    ):
        self.user_id = user_id
        self.token_service = token_service

    @property
    def definition(self) -> AgentToolDefinition:
        return AgentToolDefinition(
            name="gitlab_search_by_jira_key",
            description=(
                "Search GitLab for merge requests and issues that reference "
                "a Jira issue key in title or description."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "jira_key": {
                        "type": "string",
                        "description": "Jira issue key to search for, e.g. IT-123",
                    },
                    "project_id": {
                        "type": "string",
                        "description": (
                            "Optional GitLab project ID or URL-encoded path "
                            "(e.g. group/project). Searches all accessible projects when omitted."
                        ),
                    },
                },
                "required": ["jira_key"],
            },
        )

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        jira_key = str(arguments.get("jira_key", "")).strip().upper()
        project_id = arguments.get("project_id")

        base_url = settings.integrations.gitlab_base_url.rstrip("/")
        if not base_url:
            raise AgentToolError("GITLAB_BASE_URL is not configured")

        token = await self.token_service.get_access_token(self.user_id, "gitlab")
        headers = {"PRIVATE-TOKEN": token}

        search_term = quote(jira_key)
        results: dict[str, list[dict[str, Any]]] = {
            "merge_requests": [],
            "issues": [],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            mr_items = await _search_scope(
                client,
                base_url=base_url,
                headers=headers,
                scope="merge_requests",
                search_term=search_term,
                project_id=project_id,
            )
            issue_items = await _search_scope(
                client,
                base_url=base_url,
                headers=headers,
                scope="issues",
                search_term=search_term,
                project_id=project_id,
            )

        for item in mr_items:
            results["merge_requests"].append(_normalize_item(item, base_url, "merge_requests"))
        for item in issue_items:
            results["issues"].append(_normalize_item(item, base_url, "issues"))

        return {
            "jira_key": jira_key,
            "total": len(results["merge_requests"]) + len(results["issues"]),
            **results,
        }


async def _search_scope(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    headers: dict[str, str],
    scope: str,
    search_term: str,
    project_id: str | None,
) -> list[dict[str, Any]]:
    if project_id:
        url = (
            f"{base_url}/api/v4/projects/{quote(str(project_id), safe='')}"
            f"/{scope}?search={search_term}&per_page=20"
        )
    else:
        url = f"{base_url}/api/v4/{scope}?search={search_term}&per_page=20"

    response = await client.get(url, headers=headers)
    if response.status_code == 401:
        raise AgentToolError("GitLab authentication failed — reconnect integration")
    if response.status_code >= 400:
        raise AgentToolError(
            f"GitLab API error {response.status_code}: {response.text[:500]}"
        )
    data = response.json()
    return data if isinstance(data, list) else []


def _normalize_item(item: dict[str, Any], base_url: str, scope: str) -> dict[str, Any]:
    web_url = item.get("web_url")
    if not web_url and item.get("references"):
        web_url = (item.get("references") or {}).get("full")

    return {
        "id": item.get("id") or item.get("iid"),
        "title": item.get("title"),
        "state": item.get("state"),
        "author": (item.get("author") or {}).get("name"),
        "url": web_url or f"{base_url}/{scope}/{item.get('iid')}",
        "updated_at": item.get("updated_at"),
    }
