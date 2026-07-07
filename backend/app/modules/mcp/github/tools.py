"""GitHub MCP tool definitions and execution (OpenAI/MCP-compatible schemas)."""

from typing import Any

from app.modules.agent.exceptions import AgentToolError
from app.modules.mcp.github.client import GitHubApiClient

GITHUB_MCP_TOOLS: list[dict[str, Any]] = [
    {
        "name": "github_search_repositories",
        "description": (
            "Search GitHub repositories accessible to the user. "
            "Use GitHub search syntax (e.g. 'org:myorg language:python')."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "GitHub repository search query",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 10)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "github_get_repository",
        "description": "Get details of a GitHub repository by owner and name.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner (user or org)"},
                "repo": {"type": "string", "description": "Repository name"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_search_issues",
        "description": (
            "Search GitHub issues and pull requests. "
            "Supports GitHub search qualifiers (repo:, is:pr, is:issue, author:, label:)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "GitHub issue/PR search query",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 15)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "github_get_issue",
        "description": "Get a specific GitHub issue or pull request by repo and number.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "number": {"type": "integer", "description": "Issue or PR number"},
            },
            "required": ["owner", "repo", "number"],
        },
    },
    {
        "name": "github_list_repository_issues",
        "description": "List open or closed issues/PRs in a repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "description": "Issue state filter (default open)",
                },
                "limit": {"type": "integer"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "github_search_code",
        "description": (
            "Search code in GitHub repositories. Requires repo scope. "
            "Include repo:owner/name in query for best results."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Code search query (e.g. 'repo:org/app class:User')",
                },
                "limit": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "github_get_user",
        "description": "Get the authenticated GitHub user profile (login, name, repos count).",
        "parameters": {"type": "object", "properties": {}},
    },
]


async def execute_github_tool(
    client: GitHubApiClient,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Dispatch a GitHub MCP tool call."""
    if tool_name == "github_search_repositories":
        query = str(arguments.get("query", "")).strip()
        if not query:
            raise AgentToolError("query is required")
        limit = int(arguments.get("limit") or 10)
        repos = await client.search_repositories(query, per_page=min(limit, 30))
        return {"query": query, "total": len(repos), "repositories": repos}

    if tool_name == "github_get_repository":
        owner = str(arguments.get("owner", "")).strip()
        repo = str(arguments.get("repo", "")).strip()
        if not owner or not repo:
            raise AgentToolError("owner and repo are required")
        return await client.get_repository(owner, repo)

    if tool_name == "github_search_issues":
        query = str(arguments.get("query", "")).strip()
        if not query:
            raise AgentToolError("query is required")
        limit = int(arguments.get("limit") or 15)
        issues = await client.search_issues(query, per_page=min(limit, 30))
        return {"query": query, "total": len(issues), "issues": issues}

    if tool_name == "github_get_issue":
        owner = str(arguments.get("owner", "")).strip()
        repo = str(arguments.get("repo", "")).strip()
        number = int(arguments.get("number") or 0)
        if not owner or not repo or number <= 0:
            raise AgentToolError("owner, repo, and number are required")
        return await client.get_issue(owner, repo, number)

    if tool_name == "github_list_repository_issues":
        owner = str(arguments.get("owner", "")).strip()
        repo = str(arguments.get("repo", "")).strip()
        state = str(arguments.get("state") or "open")
        limit = int(arguments.get("limit") or 15)
        if not owner or not repo:
            raise AgentToolError("owner and repo are required")
        issues = await client.list_repository_issues(
            owner, repo, state=state, per_page=min(limit, 30)
        )
        return {"owner": owner, "repo": repo, "state": state, "total": len(issues), "issues": issues}

    if tool_name == "github_search_code":
        query = str(arguments.get("query", "")).strip()
        if not query:
            raise AgentToolError("query is required")
        limit = int(arguments.get("limit") or 10)
        results = await client.search_code(query, per_page=min(limit, 30))
        return {"query": query, "total": len(results), "results": results}

    if tool_name == "github_get_user":
        user = await client.get_authenticated_user()
        return {
            "login": user.get("login"),
            "name": user.get("name"),
            "bio": user.get("bio"),
            "public_repos": user.get("public_repos"),
            "url": user.get("html_url"),
        }

    raise AgentToolError(f"Unknown GitHub MCP tool: {tool_name}")
