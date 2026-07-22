"""Tests for GitHub MCP tool execution."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.mcp.github.tools import execute_github_tool


@pytest.mark.asyncio
async def test_github_search_repositories():
    client = MagicMock()
    client.search_repositories = AsyncMock(
        return_value=[
            {
                "full_name": "acme/app",
                "description": "Main app",
                "url": "https://github.com/acme/app",
                "stars": 10,
                "language": "Python",
            }
        ]
    )

    result = await execute_github_tool(
        client,
        "github_search_repositories",
        {"query": "org:acme", "limit": 5},
    )

    assert result["total"] == 1
    assert result["repositories"][0]["full_name"] == "acme/app"
    client.search_repositories.assert_awaited_once()


@pytest.mark.asyncio
async def test_github_get_user():
    client = MagicMock()
    client.get_authenticated_user = AsyncMock(
        return_value={
            "login": "devuser",
            "name": "Dev User",
            "public_repos": 3,
            "html_url": "https://github.com/devuser",
        }
    )

    result = await execute_github_tool(client, "github_get_user", {})

    assert result["login"] == "devuser"
    assert result["public_repos"] == 3
