"""Tests for the source routing guard."""

from app.modules.agent.guards.source_routing import (
    check_source_mismatch,
    provider_of_tool,
)


def test_provider_of_tool():
    assert provider_of_tool("jira_get_issue") == "jira"
    assert provider_of_tool("gitlab_search_by_jira_key") == "gitlab"
    assert provider_of_tool("github_get_repository") == "github"
    assert provider_of_tool("memory_search") is None


def test_warns_when_named_source_not_queried():
    warnings = check_source_mismatch(
        user_message="Show me the GitLab MRs for IT-123",
        tools_used=["jira_get_issue"],
        available_providers={"jira", "gitlab"},
    )
    assert len(warnings) == 1
    assert warnings[0].provider == "gitlab"
    assert warnings[0].reason == "not_used"


def test_no_warning_when_source_was_queried():
    warnings = check_source_mismatch(
        user_message="Show me the GitLab MRs for IT-123",
        tools_used=["jira_get_issue", "gitlab_search_by_jira_key"],
        available_providers={"jira", "gitlab"},
    )
    assert warnings == []


def test_warns_unavailable_when_integration_missing():
    warnings = check_source_mismatch(
        user_message="Check Gmail for the client",
        tools_used=["jira_get_issue"],
        available_providers={"jira", "gitlab"},
    )
    assert len(warnings) == 1
    assert warnings[0].provider == "gmail"
    assert warnings[0].reason == "unavailable"


def test_no_false_positive_on_email_address_wording():
    # "email" must not trigger the gmail keyword (only "gmail" does).
    warnings = check_source_mismatch(
        user_message="Find the client's email address in the issue",
        tools_used=["jira_get_issue"],
        available_providers={"jira", "gitlab"},
    )
    assert warnings == []


def test_no_warning_when_no_source_named():
    warnings = check_source_mismatch(
        user_message="Give me a 360 overview of IT-123",
        tools_used=["jira_get_issue"],
        available_providers={"jira", "gitlab"},
    )
    assert warnings == []
