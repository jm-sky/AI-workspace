"""Build tool registry for a user session."""

from app.modules.agent.tools.base import AgentToolRegistry
from app.modules.agent.tools.gitlab import GitLabSearchByJiraKeyTool
from app.modules.agent.tools.jira import JiraGetIssueTool
from app.modules.integrations.service import IntegrationTokenService


def build_tool_registry(
    *,
    user_id: str,
    token_service: IntegrationTokenService,
) -> AgentToolRegistry:
    """Create in-process MCP-compatible tools with per-user token injection."""
    return AgentToolRegistry(
        tools=[
            JiraGetIssueTool(user_id=user_id, token_service=token_service),
            GitLabSearchByJiraKeyTool(user_id=user_id, token_service=token_service),
        ]
    )
