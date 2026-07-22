"""GitHub REST API client for MCP tools."""

from typing import Any, cast

import httpx

from app.modules.agent.exceptions import AgentToolError


class GitHubApiClient:
    """Thin GitHub API v3 client."""

    API_BASE = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ai-workspace-mcp-github",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.API_BASE}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                url,
                headers=self._headers,
                params=params,
            )
            if response.status_code == 401:
                raise AgentToolError("GitHub authentication failed — reconnect integration")
            if response.status_code == 403:
                raise AgentToolError("GitHub API rate limit or insufficient permissions — check OAuth scopes")
            if response.status_code == 404:
                raise AgentToolError(f"GitHub resource not found: {path}")
            if response.status_code >= 400:
                raise AgentToolError(f"GitHub API error {response.status_code}: {response.text[:500]}")
            if response.status_code == 204:
                return {}
            return cast(dict[str, Any], response.json())

    async def get_authenticated_user(self) -> dict[str, Any]:
        return await self._request("GET", "/user")

    async def search_repositories(
        self,
        query: str,
        *,
        per_page: int = 10,
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            "/search/repositories",
            params={"q": query, "per_page": per_page, "sort": "updated"},
        )
        return _normalize_repos(data.get("items", []))

    async def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        data = await self._request("GET", f"/repos/{owner}/{repo}")
        return _normalize_repo(data)

    async def search_issues(
        self,
        query: str,
        *,
        per_page: int = 15,
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            "/search/issues",
            params={"q": query, "per_page": per_page, "sort": "updated"},
        )
        return [_normalize_issue(item) for item in data.get("items", [])]

    async def get_issue(
        self,
        owner: str,
        repo: str,
        number: int,
    ) -> dict[str, Any]:
        data = await self._request("GET", f"/repos/{owner}/{repo}/issues/{number}")
        return _normalize_issue(data)

    async def list_repository_issues(
        self,
        owner: str,
        repo: str,
        *,
        state: str = "open",
        per_page: int = 15,
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page},
        )
        if not isinstance(data, list):
            return []
        return [_normalize_issue(item) for item in data]

    async def search_code(
        self,
        query: str,
        *,
        per_page: int = 10,
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            "/search/code",
            params={"q": query, "per_page": per_page},
        )
        items = []
        for item in data.get("items", []):
            items.append(
                {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "repository": (item.get("repository") or {}).get("full_name"),
                    "url": item.get("html_url"),
                }
            )
        return items


def _normalize_repo(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_name": item.get("full_name"),
        "description": item.get("description"),
        "url": item.get("html_url"),
        "stars": item.get("stargazers_count"),
        "forks": item.get("forks_count"),
        "language": item.get("language"),
        "default_branch": item.get("default_branch"),
        "open_issues": item.get("open_issues_count"),
        "updated_at": item.get("updated_at"),
        "private": item.get("private"),
    }


def _normalize_repos(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_normalize_repo(item) for item in items]


def _normalize_issue(item: dict[str, Any]) -> dict[str, Any]:
    labels = [label.get("name") for label in (item.get("labels") or []) if label.get("name")]
    is_pr = "pull_request" in item
    return {
        "number": item.get("number"),
        "title": item.get("title"),
        "state": item.get("state"),
        "type": "pull_request" if is_pr else "issue",
        "author": (item.get("user") or {}).get("login"),
        "labels": labels,
        "url": item.get("html_url"),
        "repository": (item.get("repository_url") or "").replace("https://api.github.com/repos/", ""),
        "body_preview": (item.get("body") or "")[:300] or None,
        "updated_at": item.get("updated_at"),
    }
