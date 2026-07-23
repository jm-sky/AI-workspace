"""Unit tests for agent registry and explicit router."""

import pytest

from app.modules.agent.exceptions import AgentNotConfiguredError
from app.modules.agent.registry import (
    get_default_agent_key,
    list_builtin_agents,
    require_builtin_agent,
)
from app.modules.agent.routing import ExplicitAgentRouter


def test_builtin_agents_include_github_and_general():
    keys = {a.key for a in list_builtin_agents()}
    assert "github-workspace" in keys
    assert "general" in keys
    assert "jira-360" in keys


def test_default_agent_is_github_workspace():
    assert get_default_agent_key() == "github-workspace"
    assert require_builtin_agent("github-workspace").is_default


def test_unknown_agent_raises():
    with pytest.raises(AgentNotConfiguredError):
        require_builtin_agent("no-such-agent")


def test_explicit_router_prefers_session_over_explicit():
    router = ExplicitAgentRouter()
    decision = router.resolve_key(
        explicit_key="general",
        session_key="github-workspace",
        default_key="github-workspace",
    )
    assert decision.key == "github-workspace"
    assert decision.reason == "session"


def test_explicit_router_uses_explicit_when_no_session():
    router = ExplicitAgentRouter()
    decision = router.resolve_key(
        explicit_key="general",
        session_key=None,
        default_key="github-workspace",
    )
    assert decision.key == "general"
    assert decision.reason == "explicit"


def test_explicit_router_falls_back_to_default():
    router = ExplicitAgentRouter()
    decision = router.resolve_key(
        explicit_key=None,
        session_key=None,
        default_key=get_default_agent_key(),
    )
    assert decision.key == get_default_agent_key()
    assert decision.reason == "default"


def test_general_profile_is_memory_only():
    agent = require_builtin_agent("general")
    assert "memory" in agent.tool_profile
    assert "github" not in agent.tool_profile
    assert "gmail" not in agent.tool_profile


def test_agent_key_validation():
    from app.modules.agent.services.agent_definition_service import (
        AgentDefinitionError,
        AgentDefinitionService,
    )

    AgentDefinitionService._validate_key("github-workspace")
    with pytest.raises(AgentDefinitionError):
        AgentDefinitionService._validate_key("Bad Key")
    with pytest.raises(AgentDefinitionError):
        AgentDefinitionService._validate_key("")
