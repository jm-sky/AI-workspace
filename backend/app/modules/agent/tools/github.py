"""GitHub MCP tools bridged into the agent loop."""

from typing import Any

from app.modules.agent.tools.base import AgentTool, AgentToolDefinition
from app.modules.integrations.service import IntegrationTokenService
from app.modules.mcp.github.client import GitHubApiClient
from app.modules.mcp.github.tools import GITHUB_MCP_TOOLS, execute_github_tool
from app.modules.tenants.service import TenantContext


class GitHubMcpTool(AgentTool):
    """Single GitHub MCP tool exposed to the agent loop."""

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

    async def _client(self) -> GitHubApiClient:
        token = await self.token_service.resolve_access_token(
            user_id=self.tenant_ctx.user_id,
            tenant_id=self.tenant_ctx.tenant_id,
            team_id=self.tenant_ctx.team_id,
            provider="github",
        )
        return GitHubApiClient(token)

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        client = await self._client()
        return await execute_github_tool(client, self._tool_name, arguments)


def build_github_mcp_tools(
    *,
    tenant_ctx: TenantContext,
    token_service: IntegrationTokenService,
) -> list[AgentTool]:
    """Instantiate all GitHub MCP tools for a session."""
    return [
        GitHubMcpTool(
            tool_name=schema["name"],
            tool_schema=schema,
            tenant_ctx=tenant_ctx,
            token_service=token_service,
        )
        for schema in GITHUB_MCP_TOOLS
    ]
