"""Repository for integration OAuth tokens."""

from datetime import UTC, datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.integrations.crypto import (
    decrypt_integration_token,
    encrypt_integration_token,
)
from app.modules.integrations.db_models import IntegrationOAuthTokenDB
from app.modules.integrations.types import IntegrationVisibilityScope


class IntegrationTokenRepository:
    """Data access for integration OAuth tokens with visibility scopes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, connection_id: str) -> IntegrationOAuthTokenDB | None:
        result = await self.db.execute(select(IntegrationOAuthTokenDB).where(IntegrationOAuthTokenDB.id == connection_id))
        return result.scalar_one_or_none()

    async def find_user_scoped(self, owner_user_id: str, provider: str) -> IntegrationOAuthTokenDB | None:
        result = await self.db.execute(
            select(IntegrationOAuthTokenDB).where(
                IntegrationOAuthTokenDB.owner_user_id == owner_user_id,
                IntegrationOAuthTokenDB.provider == provider,
                IntegrationOAuthTokenDB.visibility_scope == IntegrationVisibilityScope.USER.value,
            )
        )
        return result.scalar_one_or_none()

    async def find_team_scoped(self, team_id: str, provider: str) -> IntegrationOAuthTokenDB | None:
        result = await self.db.execute(
            select(IntegrationOAuthTokenDB).where(
                IntegrationOAuthTokenDB.team_id == team_id,
                IntegrationOAuthTokenDB.provider == provider,
                IntegrationOAuthTokenDB.visibility_scope == IntegrationVisibilityScope.TEAM.value,
            )
        )
        return result.scalar_one_or_none()

    async def find_tenant_scoped(self, tenant_id: str, provider: str) -> IntegrationOAuthTokenDB | None:
        result = await self.db.execute(
            select(IntegrationOAuthTokenDB).where(
                IntegrationOAuthTokenDB.tenant_id == tenant_id,
                IntegrationOAuthTokenDB.provider == provider,
                IntegrationOAuthTokenDB.visibility_scope == IntegrationVisibilityScope.TENANT.value,
            )
        )
        return result.scalar_one_or_none()

    async def list_visible_for_user(
        self,
        *,
        user_id: str,
        tenant_id: str,
        team_ids: list[str],
    ) -> list[IntegrationOAuthTokenDB]:
        conditions = [
            ((IntegrationOAuthTokenDB.owner_user_id == user_id) & (IntegrationOAuthTokenDB.visibility_scope == IntegrationVisibilityScope.USER.value)),
            ((IntegrationOAuthTokenDB.tenant_id == tenant_id) & (IntegrationOAuthTokenDB.visibility_scope == IntegrationVisibilityScope.TENANT.value)),
        ]
        if team_ids:
            conditions.append((IntegrationOAuthTokenDB.team_id.in_(team_ids)) & (IntegrationOAuthTokenDB.visibility_scope == IntegrationVisibilityScope.TEAM.value))

        result = await self.db.execute(
            select(IntegrationOAuthTokenDB)
            .where(or_(*conditions))
            .order_by(
                IntegrationOAuthTokenDB.provider,
                IntegrationOAuthTokenDB.visibility_scope,
            )
        )
        return list(result.scalars().all())

    async def upsert_connection(
        self,
        *,
        owner_user_id: str,
        provider: str,
        visibility_scope: str,
        tenant_id: str | None,
        team_id: str | None,
        access_token: str,
        refresh_token: str | None = None,
        token_type: str = "Bearer",
        expires_at: datetime | None = None,
        scopes: str | None = None,
        provider_metadata: dict[str, Any] | None = None,
    ) -> IntegrationOAuthTokenDB:
        existing = await self._find_existing(
            provider=provider,
            visibility_scope=visibility_scope,
            owner_user_id=owner_user_id,
            tenant_id=tenant_id,
            team_id=team_id,
        )
        encrypted_access = encrypt_integration_token(access_token)
        encrypted_refresh = encrypt_integration_token(refresh_token) if refresh_token else None

        if existing:
            existing.encrypted_access_token = encrypted_access
            existing.encrypted_refresh_token = encrypted_refresh
            existing.token_type = token_type
            existing.expires_at = expires_at
            existing.scopes = scopes
            existing.provider_metadata = provider_metadata
            existing.updated_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        token = IntegrationOAuthTokenDB(
            id=generate_id(),
            owner_user_id=owner_user_id,
            provider=provider,
            visibility_scope=visibility_scope,
            tenant_id=tenant_id,
            team_id=team_id,
            encrypted_access_token=encrypted_access,
            encrypted_refresh_token=encrypted_refresh,
            token_type=token_type,
            expires_at=expires_at,
            scopes=scopes,
            provider_metadata=provider_metadata,
        )
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def update_tokens(
        self,
        token: IntegrationOAuthTokenDB,
        *,
        access_token: str,
        refresh_token: str | None = None,
        token_type: str = "Bearer",
        expires_at: datetime | None = None,
        scopes: str | None = None,
        provider_metadata: dict[str, Any] | None = None,
    ) -> IntegrationOAuthTokenDB:
        """Rotate tokens in place, preserving fields the provider did not return."""
        token.encrypted_access_token = encrypt_integration_token(access_token)
        if refresh_token:
            token.encrypted_refresh_token = encrypt_integration_token(refresh_token)
        token.token_type = token_type
        token.expires_at = expires_at
        if scopes is not None:
            token.scopes = scopes
        if provider_metadata is not None:
            token.provider_metadata = provider_metadata
        token.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def _find_existing(
        self,
        *,
        provider: str,
        visibility_scope: str,
        owner_user_id: str,
        tenant_id: str | None,
        team_id: str | None,
    ) -> IntegrationOAuthTokenDB | None:
        stmt = select(IntegrationOAuthTokenDB).where(
            IntegrationOAuthTokenDB.provider == provider,
            IntegrationOAuthTokenDB.visibility_scope == visibility_scope,
        )
        if visibility_scope == IntegrationVisibilityScope.USER.value:
            stmt = stmt.where(IntegrationOAuthTokenDB.owner_user_id == owner_user_id)
        elif visibility_scope == IntegrationVisibilityScope.TEAM.value:
            stmt = stmt.where(IntegrationOAuthTokenDB.team_id == team_id)
        elif visibility_scope == IntegrationVisibilityScope.TENANT.value:
            stmt = stmt.where(IntegrationOAuthTokenDB.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_connection(self, connection_id: str) -> bool:
        result = await self.db.execute(delete(IntegrationOAuthTokenDB).where(IntegrationOAuthTokenDB.id == connection_id))
        await self.db.commit()
        return (result.rowcount or 0) > 0  # type: ignore[attr-defined]

    async def delete_user_provider(self, owner_user_id: str, provider: str) -> bool:
        result = await self.db.execute(
            delete(IntegrationOAuthTokenDB).where(
                IntegrationOAuthTokenDB.owner_user_id == owner_user_id,
                IntegrationOAuthTokenDB.provider == provider,
                IntegrationOAuthTokenDB.visibility_scope == IntegrationVisibilityScope.USER.value,
            )
        )
        await self.db.commit()
        return (result.rowcount or 0) > 0  # type: ignore[attr-defined]

    def decrypt_access_token(self, token: IntegrationOAuthTokenDB) -> str:
        return decrypt_integration_token(token.encrypted_access_token)

    def decrypt_refresh_token(self, token: IntegrationOAuthTokenDB) -> str | None:
        if not token.encrypted_refresh_token:
            return None
        return decrypt_integration_token(token.encrypted_refresh_token)


def get_integration_token_repository(
    db: AsyncSession = Depends(get_db),
) -> IntegrationTokenRepository:
    return IntegrationTokenRepository(db)
