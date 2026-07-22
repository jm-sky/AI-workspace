"""Thin MCP server for GitLab — mirrors agent tool `gitlab_search_by_jira_key`.

Run: MCP_USER_ACCESS_TOKEN=... GITLAB_BASE_URL=... python -m mcp_servers.gitlab_server
"""

from __future__ import annotations

import json
import os


def main() -> None:
    token = os.environ.get("MCP_USER_ACCESS_TOKEN", "")
    base_url = os.environ.get("GITLAB_BASE_URL", "")
    if not token or not base_url:
        raise SystemExit("Set MCP_USER_ACCESS_TOKEN and GITLAB_BASE_URL")

    print(
        json.dumps(
            {
                "server": "gitlab-mcp",
                "tools": ["gitlab_search_by_jira_key"],
                "note": "Use agent module in-process tools for production",
            }
        )
    )


if __name__ == "__main__":
    main()
