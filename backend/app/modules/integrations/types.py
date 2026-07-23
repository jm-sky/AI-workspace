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
    GMAIL = "gmail"
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

GMAIL_OAUTH_SCOPES: list[dict[str, str | bool]] = [
    {
        "id": "openid",
        "labelKey": "settings.integrations.scopes.gmail.openid",
        "descriptionKey": "settings.integrations.scopes.gmail.openid_desc",
        "required": True,
    },
    {
        "id": "https://www.googleapis.com/auth/userinfo.email",
        "labelKey": "settings.integrations.scopes.gmail.email",
        "descriptionKey": "settings.integrations.scopes.gmail.email_desc",
        "required": True,
    },
    {
        "id": "https://www.googleapis.com/auth/userinfo.profile",
        "labelKey": "settings.integrations.scopes.gmail.profile",
        "descriptionKey": "settings.integrations.scopes.gmail.profile_desc",
        "required": True,
    },
    {
        "id": "https://www.googleapis.com/auth/gmail.readonly",
        "labelKey": "settings.integrations.scopes.gmail.readonly",
        "descriptionKey": "settings.integrations.scopes.gmail.readonly_desc",
        "required": True,
    },
]

INTEGRATION_PROVIDER_SCOPES: dict[str, list[dict[str, str | bool]]] = {
    IntegrationProvider.GITHUB.value: GITHUB_OAUTH_SCOPES,
    IntegrationProvider.GMAIL.value: GMAIL_OAUTH_SCOPES,
}

DEFAULT_GITHUB_SCOPES = ["read:user", "repo"]
DEFAULT_GMAIL_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]
