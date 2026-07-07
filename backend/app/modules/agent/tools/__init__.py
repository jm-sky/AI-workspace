"""Build tool registry for a user session."""

from app.modules.agent.tools.base import AgentToolRegistry
from app.modules.agent.tools.gitlab import GitLabSearchByJiraKeyTool
from app.modules.agent.tools.jira import JiraGetIssueTool
from app.modules.integrations.service import IntegrationTokenService
from app.modules.tenants.service import TenantContext


def build_tool_registry(
    *,
    tenant_ctx: TenantContext,
    token_service: IntegrationTokenService,
) -> AgentToolRegistry:
    """Create in-process MCP-compatible tools with per-user token injection."""
    return AgentToolRegistry(
        tools=[
            JiraGetIssueTool(tenant_ctx=tenant_ctx, token_service=token_service),
            GitLabSearchByJiraKeyTool(tenant_ctx=tenant_ctx, token_service=token_service),
        ]
    )
