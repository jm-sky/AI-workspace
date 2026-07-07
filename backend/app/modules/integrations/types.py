"""Types for integration OAuth connections."""

from enum import StrEnum


class IntegrationVisibilityScope(StrEnum):
    """Who may use a stored integration token."""

    USER = "user"
    TEAM = "team"
    TENANT = "tenant"


class IntegrationProvider(StrEnum):
    """Supported integration providers."""

    GITHUB = "github"
    JIRA = "jira"
    GITLAB = "gitlab"


GITHUB_OAUTH_SCOPES: list[dict[str, str | bool]] = [
    {
        "id": "read:user",
        "labelKey": "settings.integrations.scopes.github.read_user",
        "descriptionKey": "settings.integrations.scopes.github.read_user_desc",
        "required": True,
    },
    {
        "id": "repo",
        "labelKey": "settings.integrations.scopes.github.repo",
        "descriptionKey": "settings.integrations.scopes.github.repo_desc",
        "required": False,
    },
]

INTEGRATION_PROVIDER_SCOPES: dict[str, list[dict[str, str | bool]]] = {
    IntegrationProvider.GITHUB.value: GITHUB_OAUTH_SCOPES,
}

DEFAULT_GITHUB_SCOPES = ["read:user", "repo"]
