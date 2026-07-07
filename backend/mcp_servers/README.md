# MCP servers — Phase 1 (Jira + GitLab)

Thin MCP servers per provider. The **agent loop** uses in-process tool execution
(`app/modules/agent/tools/`) with the same JSON schemas for performance and
per-user token injection.

These standalone servers are for:

- MCP-compatible testing with external clients
- Future subprocess isolation

## Tools

| Server | Tool | Description |
|--------|------|-------------|
| `jira_server.py` | `jira_get_issue` | Fetch issue + Klient field |
| `gitlab_server.py` | `gitlab_search_by_jira_key` | Search MRs/issues by Jira key |

## Run (stdio MCP)

Requires env: `JIRA_BASE_URL`, `GITLAB_BASE_URL`, `INTEGRATION_TOKEN_ENCRYPTION_KEY`,
and a user token stored via `PUT /api/integrations/oauth/tokens` (or pass
`MCP_USER_ACCESS_TOKEN` for local dev).

```bash
cd backend
MCP_USER_ID=<user-id> MCP_PROVIDER=jira python -m mcp_servers.jira_server
```

Phase 1 production path: agent module calls tools in-process — no separate MCP process required.
