"""Abstraction for injecting integration tokens into MCP tool calls."""

from typing import Protocol

from app.modules.integrations.exceptions import (
    IntegrationTokenExpiredError,
    IntegrationTokenNotFoundError,
)
from app.modules.integrations.repositories import IntegrationTokenRepository


class IntegrationTokenProvider(Protocol):
    """Protocol for retrieving valid access tokens per user and provider."""

    async def get_access_token(self, user_id: str, provider: str) -> str:
        """Return a valid access token, refreshing if needed."""
        ...


class IntegrationTokenService:
    """Service for storing and retrieving per-user integration OAuth tokens."""

    def __init__(self, repo: IntegrationTokenRepository):
        self.repo = repo

    async def store_tokens(
        self,
        *,
        user_id: str,
        provider: str,
        access_token: str,
        refresh_token: str | None = None,
        expires_at=None,
        scopes: str | None = None,
        provider_metadata: dict | None = None,
    ):
        return await self.repo.upsert_token(
            user_id=user_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scopes=scopes,
            provider_metadata=provider_metadata,
        )

    async def get_access_token(self, user_id: str, provider: str) -> str:
        token = await self.repo.get_token(user_id, provider)
        if token is None:
            raise IntegrationTokenNotFoundError(
                f"No integration token for provider '{provider}'"
            )

        if token.expires_at and token.expires_at <= _utcnow():
            if token.encrypted_refresh_token:
                raise IntegrationTokenExpiredError(
                    f"Token for '{provider}' expired — re-authenticate "
                    "(provider refresh not yet implemented)"
                )
            raise IntegrationTokenExpiredError(
                f"Token for '{provider}' expired and no refresh token available"
            )

        return self.repo.decrypt_access_token(token)

    async def delete_tokens(self, user_id: str, provider: str) -> bool:
        return await self.repo.delete_token(user_id, provider)

    async def list_connections(self, user_id: str) -> list[dict]:
        tokens = await self.repo.list_for_user(user_id)
        return [
            {
                "provider": token.provider,
                "expiresAt": token.expires_at,
                "scopes": token.scopes,
                "hasRefreshToken": token.encrypted_refresh_token is not None,
            }
            for token in tokens
        ]


def _utcnow():
    from datetime import UTC, datetime

    return datetime.now(UTC)
