"""Base types for integration OAuth providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.modules.integrations.exceptions import IntegrationRefreshNotSupportedError


@dataclass(frozen=True)
class IntegrationOAuthTokenResult:
    """Token exchange result for integration OAuth."""

    access_token: str
    token_type: str = "Bearer"
    scope: str | None = None
    refresh_token: str | None = None
    expires_at: Any | None = None
    provider_metadata: dict[str, Any] | None = None


class IntegrationOAuthProvider(ABC):
    """OAuth provider for external integrations (not login)."""

    @abstractmethod
    def get_authorization_url(self, *, state: str, scopes: list[str]) -> str:
        """Build provider authorization URL."""

    @abstractmethod
    async def exchange_code_for_token(self, code: str, *, scopes: list[str]) -> IntegrationOAuthTokenResult:
        """Exchange authorization code for tokens."""

    async def refresh_access_token(self, refresh_token: str) -> IntegrationOAuthTokenResult:
        """Exchange a refresh token for a fresh access token."""
        raise IntegrationRefreshNotSupportedError(f"{type(self).__name__} does not support token refresh")
