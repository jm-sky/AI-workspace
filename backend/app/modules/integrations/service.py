"""Abstraction for injecting integration tokens into MCP tool calls."""

from typing import Protocol

from app.modules.integrations.exceptions import (
    IntegrationPermissionError,
    IntegrationTokenExpiredError,
    IntegrationTokenNotFoundError,
)
from app.modules.integrations.repositories import IntegrationTokenRepository
from app.modules.integrations.types import IntegrationVisibilityScope


class IntegrationTokenProvider(Protocol):
    """Protocol for retrieving valid access tokens per user and provider."""

    async def resolve_access_token(
        self,
        *,
        user_id: str,
        tenant_id: str,
        team_id: str | None,
        provider: str,
    ) -> str:
        """Return a valid access token using cascade resolution."""
        ...


class IntegrationTokenService:
    """Service for storing and retrieving integration OAuth tokens."""

    def __init__(self, repo: IntegrationTokenRepository):
        self.repo = repo

    async def store_tokens(
        self,
        *,
        owner_user_id: str,
        provider: str,
        access_token: str,
        visibility_scope: str = IntegrationVisibilityScope.USER.value,
        tenant_id: str | None = None,
        team_id: str | None = None,
        refresh_token: str | None = None,
        expires_at=None,
        scopes: str | None = None,
        provider_metadata: dict | None = None,
    ):
        return await self.repo.upsert_connection(
            owner_user_id=owner_user_id,
            provider=provider,
            visibility_scope=visibility_scope,
            tenant_id=tenant_id,
            team_id=team_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scopes=scopes,
            provider_metadata=provider_metadata,
        )

    async def resolve_access_token(
        self,
        *,
        user_id: str,
        tenant_id: str,
        team_id: str | None,
        provider: str,
    ) -> str:
        """Resolve token: personal > active team > tenant."""
        personal = await self.repo.find_user_scoped(user_id, provider)
        if personal is not None:
            return self._require_valid_access_token(personal)

        if team_id:
            team_token = await self.repo.find_team_scoped(team_id, provider)
            if team_token is not None:
                return self._require_valid_access_token(team_token)

        tenant_token = await self.repo.find_tenant_scoped(tenant_id, provider)
        if tenant_token is not None:
            return self._require_valid_access_token(tenant_token)

        raise IntegrationTokenNotFoundError(
            f"No integration token for provider '{provider}'"
        )

    async def get_access_token(self, user_id: str, provider: str) -> str:
        """Backward-compatible lookup for personal token only."""
        token = await self.repo.find_user_scoped(user_id, provider)
        if token is None:
            raise IntegrationTokenNotFoundError(
                f"No integration token for provider '{provider}'"
            )
        return self._require_valid_access_token(token)

    def _require_valid_access_token(self, token) -> str:
        if token.expires_at and token.expires_at <= _utcnow():
            if token.encrypted_refresh_token:
                raise IntegrationTokenExpiredError(
                    f"Token for '{token.provider}' expired — re-authenticate "
                    "(provider refresh not yet implemented)"
                )
            raise IntegrationTokenExpiredError(
                f"Token for '{token.provider}' expired and no refresh token available"
            )
        return self.repo.decrypt_access_token(token)

    async def delete_connection(self, connection_id: str) -> bool:
        return await self.repo.delete_connection(connection_id)

    async def delete_tokens(self, user_id: str, provider: str) -> bool:
        return await self.repo.delete_user_provider(user_id, provider)

    async def list_connections(
        self,
        *,
        user_id: str,
        tenant_id: str,
        team_ids: list[str],
        tenant_role: str,
    ) -> list[dict]:
        tokens = await self.repo.list_visible_for_user(
            user_id=user_id,
            tenant_id=tenant_id,
            team_ids=team_ids,
        )
        can_manage_shared = tenant_role in ("owner", "admin")
        return [
            self._connection_dict(
                token,
                user_id=user_id,
                can_manage_shared=can_manage_shared,
            )
            for token in tokens
        ]

    def _connection_dict(
        self,
        token,
        *,
        user_id: str,
        can_manage_shared: bool,
        team_name: str | None = None,
    ) -> dict:
        is_owner = token.owner_user_id == user_id
        shared = token.visibility_scope in (
            IntegrationVisibilityScope.TEAM.value,
            IntegrationVisibilityScope.TENANT.value,
        )
        can_manage = is_owner or (shared and can_manage_shared)
        return {
            "id": token.id,
            "provider": token.provider,
            "visibilityScope": token.visibility_scope,
            "tenantId": token.tenant_id,
            "teamId": token.team_id,
            "teamName": team_name,
            "ownerUserId": token.owner_user_id,
            "isOwner": is_owner,
            "expiresAt": token.expires_at,
            "scopes": token.scopes,
            "hasRefreshToken": token.encrypted_refresh_token is not None,
            "providerMetadata": token.provider_metadata,
            "canManage": can_manage,
        }

    @staticmethod
    def assert_shared_visibility_allowed(
        *,
        visibility_scope: str,
        tenant_role: str,
        team_id: str | None,
    ) -> None:
        if visibility_scope == IntegrationVisibilityScope.USER.value:
            return
        if tenant_role not in ("owner", "admin"):
            raise IntegrationPermissionError(
                "Only tenant owner or admin can create shared integration connections"
            )
        if visibility_scope == IntegrationVisibilityScope.TEAM.value and not team_id:
            raise IntegrationPermissionError("teamId is required for team visibility")


def _utcnow():
    from datetime import UTC, datetime

    return datetime.now(UTC)
