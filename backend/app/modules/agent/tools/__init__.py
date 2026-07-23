"""Build tool registry for a user session."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.agent.tools.base import AgentToolRegistry
from app.modules.agent.tools.github import build_github_mcp_tools
from app.modules.agent.tools.gitlab import GitLabSearchByJiraKeyTool
from app.modules.agent.tools.gmail import build_gmail_mcp_tools
from app.modules.agent.tools.jira import JiraGetIssueTool
from app.modules.agent.tools.memory import MemorySaveTool, MemorySearchTool, MemoryUpdateTool
from app.modules.agent.tools.rag import RagSearchTool
from app.modules.agent.tools.tool_search import ToolSearchTool
from app.modules.integrations.service import IntegrationTokenService
from app.modules.tenants.service import TenantContext

AGENT_TOOL_PROFILES: dict[str, list[str]] = {
    # Profile = default / quick tools. Provider MCP buckets (github, gmail, …)
    # can later be discoverable across agents via tool_search; for now wire
    # gmail into the primary workspace agent.
    "github-workspace": ["github", "gmail", "memory", "rag"],
    "jira-360": ["jira", "gitlab", "memory", "rag"],
}

# Always loaded when tool search mode is active (profile tools may be deferred).
CORE_TOOL_NAMES: frozenset[str] = frozenset(
    {"tool_search", "memory_search", "memory_save", "memory_update"}
)


def build_tool_registry(
    *,
    tenant_ctx: TenantContext,
    token_service: IntegrationTokenService,
    db: AsyncSession,
    agent_key: str = "github-workspace",
    session_id: str | None = None,
    rag_enabled: bool = False,
) -> AgentToolRegistry:
    """Create in-process MCP-compatible tools with per-user token injection.

    When tool search is enabled and the profile catalog exceeds the threshold,
    only core tools (+ ``tool_search``) are exposed initially; the rest are
    deferred until discovered via search.
    """
    profile = AGENT_TOOL_PROFILES.get(agent_key, ["github", "memory", "rag"])
    tools = []

    if "github" in profile:
        tools.extend(build_github_mcp_tools(tenant_ctx=tenant_ctx, token_service=token_service))
    if "gmail" in profile:
        tools.extend(build_gmail_mcp_tools(tenant_ctx=tenant_ctx, token_service=token_service))
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
                MemoryUpdateTool(
                    tenant_ctx=tenant_ctx,
                    db=db,
                    agent_key=agent_key,
                    session_id=session_id,
                ),
            ]
        )
    if "rag" in profile:
        tools.append(
            RagSearchTool(
                tenant_ctx=tenant_ctx,
                db=db,
                rag_enabled=rag_enabled,
            )
        )

    registry = AgentToolRegistry(tools=tools)
    profile_count = len(tools)

    if (
        settings.ai.tool_search_enabled
        and profile_count > settings.ai.tool_search_threshold
    ):
        registry.register(
            ToolSearchTool(
                registry=registry,
                top_k=settings.ai.tool_search_top_k,
            )
        )
        core_present = [name for name in CORE_TOOL_NAMES if name in registry]
        registry.set_active(core_present)

    return registry
