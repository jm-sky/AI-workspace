"""Build tool registry for a user session."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agent.tools.base import AgentToolRegistry
from app.modules.agent.tools.github import build_github_mcp_tools
from app.modules.agent.tools.gitlab import GitLabSearchByJiraKeyTool
from app.modules.agent.tools.jira import JiraGetIssueTool
from app.modules.agent.tools.memory import MemorySaveTool, MemorySearchTool
from app.modules.integrations.service import IntegrationTokenService
from app.modules.tenants.service import TenantContext

AGENT_TOOL_PROFILES: dict[str, list[str]] = {
    "github-workspace": ["github", "memory"],
    "jira-360": ["jira", "gitlab", "memory"],
}


def build_tool_registry(
    *,
    tenant_ctx: TenantContext,
    token_service: IntegrationTokenService,
    db: AsyncSession,
    agent_key: str = "github-workspace",
    session_id: str | None = None,
) -> AgentToolRegistry:
    """Create in-process MCP-compatible tools with per-user token injection."""
    profile = AGENT_TOOL_PROFILES.get(agent_key, ["github", "memory"])
    tools = []

    if "github" in profile:
        tools.extend(build_github_mcp_tools(tenant_ctx=tenant_ctx, token_service=token_service))
    if "jira" in profile:
        tools.append(JiraGetIssueTool(tenant_ctx=tenant_ctx, token_service=token_service))
    if "gitlab" in profile:
        tools.append(GitLabSearchByJiraKeyTool(tenant_ctx=tenant_ctx, token_service=token_service))
    if "memory" in profile:
        tools.extend(
            [
                MemorySearchTool(
                    tenant_ctx=tenant_ctx,
                    db=db,
                    agent_key=agent_key,
                    session_id=session_id,
                ),
                MemorySaveTool(
                    tenant_ctx=tenant_ctx,
                    db=db,
                    agent_key=agent_key,
                    session_id=session_id,
                ),
            ]
        )

    return AgentToolRegistry(tools=tools)
