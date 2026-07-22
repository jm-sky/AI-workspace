"""Abstraction for injecting integration tokens into MCP tool calls."""

from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from app.modules.integrations.db_models import IntegrationOAuthTokenDB
from app.modules.integrations.exceptions import (
    IntegrationPermissionError,
    IntegrationRefreshFailedError,
    IntegrationRefreshNotSupportedError,
    IntegrationTokenExpiredError,
    IntegrationTokenNotFoundError,
)
from app.modules.integrations.providers import integration_oauth_registry
from app.modules.integrations.providers.registry import IntegrationOAuthRegistry
from app.modules.integrations.repositories import IntegrationTokenRepository
from app.modules.integrations.types import IntegrationVisibilityScope

# Refresh slightly early so a token cannot expire mid-request.
REFRESH_SKEW = timedelta(seconds=60)


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

    def __init__(
        self,
        repo: IntegrationTokenRepository,
        registry: IntegrationOAuthRegistry | None = None,
    ):
        self.repo = repo
        self.registry = registry or integration_oauth_registry

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
        expires_at: datetime | None = None,
        scopes: str | None = None,
        provider_metadata: dict | None = None,
    ) -> IntegrationOAuthTokenDB:
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
            return await self._require_valid_access_token(personal)

        if team_id:
            team_token = await self.repo.find_team_scoped(team_id, provider)
            if team_token is not None:
                return await self._require_valid_access_token(team_token)

        tenant_token = await self.repo.find_tenant_scoped(tenant_id, provider)
        if tenant_token is not None:
            return await self._require_valid_access_token(tenant_token)

        raise IntegrationTokenNotFoundError(f"No integration token for provider '{provider}'")

    async def get_access_token(self, user_id: str, provider: str) -> str:
        """Backward-compatible lookup for personal token only."""
        token = await self.repo.find_user_scoped(user_id, provider)
        if token is None:
            raise IntegrationTokenNotFoundError(f"No integration token for provider '{provider}'")
        return await self._require_valid_access_token(token)

    async def _require_valid_access_token(self, token: IntegrationOAuthTokenDB) -> str:
        if not self._is_expiring(token):
            return self.repo.decrypt_access_token(token)

        refresh_token = self.repo.decrypt_refresh_token(token)
        if not refresh_token:
            raise IntegrationTokenExpiredError(f"Token for '{token.provider}' expired and no refresh token available")
        return await self._refresh_access_token(token, refresh_token)

    @staticmethod
    def _is_expiring(token: IntegrationOAuthTokenDB) -> bool:
        expires_at = token.expires_at
        return expires_at is not None and expires_at <= _utcnow() + REFRESH_SKEW

    async def _refresh_access_token(self, token: IntegrationOAuthTokenDB, refresh_token: str) -> str:
        try:
            provider = self.registry.get(token.provider)
            result = await provider.refresh_access_token(refresh_token)
        except (
            IntegrationRefreshNotSupportedError,
            IntegrationRefreshFailedError,
            ValueError,
        ) as exc:
            raise IntegrationTokenExpiredError(f"Token for '{token.provider}' expired and could not be refreshed " f"— re-authenticate ({exc})") from exc

        await self.repo.update_tokens(
            token,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
            expires_at=result.expires_at,
            scopes=result.scope,
            provider_metadata=result.provider_metadata,
        )
        return result.access_token

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
        token: IntegrationOAuthTokenDB,
        *,
        user_id: str,
        can_manage_shared: bool,
        team_name: str | None = None,
    ) -> dict[str, Any]:
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
            raise IntegrationPermissionError("Only tenant owner or admin can create shared integration connections")
        if visibility_scope == IntegrationVisibilityScope.TEAM.value and not team_id:
            raise IntegrationPermissionError("teamId is required for team visibility")


def _utcnow() -> datetime:
    return datetime.now(UTC)
