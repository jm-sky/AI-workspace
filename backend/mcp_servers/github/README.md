# GitHub MCP Server

Thin MCP-compatible GitHub integration for AI Workspace.

## Architecture

- **REST client:** `backend/app/modules/mcp/github/client.py`
- **Tool schemas + dispatch:** `backend/app/modules/mcp/github/tools.py`
- **Agent bridge:** `backend/app/modules/agent/tools/github.py` (in-process, per-user OAuth token injection)

Tools are exposed to the agent loop as OpenAI function-calling tools. OAuth tokens come from Settings → Integrations → GitHub.

## Tools

| Tool | Description |
|------|-------------|
| `github_get_user` | Authenticated user profile |
| `github_search_repositories` | Search repos |
| `github_get_repository` | Repo details |
| `github_search_issues` | Search issues/PRs |
| `github_get_issue` | Single issue or PR |
| `github_list_repository_issues` | List issues in a repo |
| `github_search_code` | Code search (requires `repo` OAuth scope) |

## Agent

Default agent `github-workspace` uses these tools plus `memory_search` / `memory_save`.

Connect GitHub in **Settings → Integrations** before using GitHub tools in chat.
