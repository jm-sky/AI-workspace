"""Integration OAuth providers."""

from app.modules.integrations.providers.github import GitHubIntegrationProvider
from app.modules.integrations.providers.registry import IntegrationOAuthRegistry

integration_oauth_registry = IntegrationOAuthRegistry(
    providers={
        "github": GitHubIntegrationProvider(),
    }
)
