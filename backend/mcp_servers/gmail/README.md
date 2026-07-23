# Gmail MCP (in-process)

Thin Gmail REST wrapper used by the agent loop (`mcp/gmail` + `agent/tools/gmail.py`).

## Tools

| Tool | Description |
|------|-------------|
| `gmail_search_messages` | Gmail `q=` search |
| `gmail_list_messages` | List by label (default INBOX) |
| `gmail_get_message` | Full message + plain text body |

## OAuth

Provider id: `gmail`  
Env: `GMAIL_INTEGRATION_OAUTH_CLIENT_ID/SECRET/REDIRECT_URI`  
Scopes: `openid`, `userinfo.email`, `userinfo.profile`, `gmail.readonly`  
Callback: `/settings/integrations/callback/gmail`
