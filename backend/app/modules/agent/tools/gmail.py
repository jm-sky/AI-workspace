"""Gmail MCP tools bridged into the agent loop."""

from typing import Any

from app.modules.agent.tools.base import AgentTool, AgentToolDefinition
from app.modules.integrations.service import IntegrationTokenService
from app.modules.mcp.gmail.client import GmailApiClient
from app.modules.mcp.gmail.tools import GMAIL_MCP_TOOLS, execute_gmail_tool
from app.modules.tenants.service import TenantContext


class GmailMcpTool(AgentTool):
    """Single Gmail MCP tool exposed to the agent loop."""

    def __init__(
        self,
        *,
        tool_name: str,
        tool_schema: dict[str, Any],
        tenant_ctx: TenantContext,
        token_service: IntegrationTokenService,
    ):
        self._tool_name = tool_name
        self._tool_schema = tool_schema
        self.tenant_ctx = tenant_ctx
        self.token_service = token_service

    @property
    def definition(self) -> AgentToolDefinition:
        return AgentToolDefinition(
            name=self._tool_schema["name"],
            description=self._tool_schema["description"],
            parameters=self._tool_schema["parameters"],
        )

    async def _client(self) -> GmailApiClient:
        token = await self.token_service.resolve_access_token(
            user_id=self.tenant_ctx.user_id,
            tenant_id=self.tenant_ctx.tenant_id,
            team_id=self.tenant_ctx.team_id,
            provider="gmail",
        )
        return GmailApiClient(token)

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        client = await self._client()
        return await execute_gmail_tool(client, self._tool_name, arguments)


def build_gmail_mcp_tools(
    *,
    tenant_ctx: TenantContext,
    token_service: IntegrationTokenService,
) -> list[AgentTool]:
    """Instantiate all Gmail MCP tools for a session."""
    return [
        GmailMcpTool(
            tool_name=schema["name"],
            tool_schema=schema,
            tenant_ctx=tenant_ctx,
            token_service=token_service,
        )
        for schema in GMAIL_MCP_TOOLS
    ]
