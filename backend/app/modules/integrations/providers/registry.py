"""Registry of integration OAuth providers."""

from app.modules.integrations.providers.base import IntegrationOAuthProvider


class IntegrationOAuthRegistry:
    """Lookup integration OAuth providers by name."""

    def __init__(self, providers: dict[str, IntegrationOAuthProvider]):
        self._providers = providers

    def get(self, provider_name: str) -> IntegrationOAuthProvider:
        if provider_name not in self._providers:
            raise ValueError(f"Unsupported integration provider: {provider_name}")
        return self._providers[provider_name]

    def supported_providers(self) -> list[str]:
        return sorted(self._providers.keys())
