"""Repository for integration OAuth tokens."""

from datetime import UTC, datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.integrations.crypto import (
    decrypt_integration_token,
    encrypt_integration_token,
)
from app.modules.integrations.db_models import IntegrationOAuthTokenDB


class IntegrationTokenRepository:
    """Data access for per-user integration OAuth tokens."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_token(
        self, user_id: str, provider: str
    ) -> IntegrationOAuthTokenDB | None:
        result = await self.db.execute(
            select(IntegrationOAuthTokenDB).where(
                IntegrationOAuthTokenDB.user_id == user_id,
                IntegrationOAuthTokenDB.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: str) -> list[IntegrationOAuthTokenDB]:
        result = await self.db.execute(
            select(IntegrationOAuthTokenDB)
            .where(IntegrationOAuthTokenDB.user_id == user_id)
            .order_by(IntegrationOAuthTokenDB.provider)
        )
        return list(result.scalars().all())

    async def upsert_token(
        self,
        *,
        user_id: str,
        provider: str,
        access_token: str,
        refresh_token: str | None = None,
        token_type: str = "Bearer",
        expires_at: datetime | None = None,
        scopes: str | None = None,
        provider_metadata: dict[str, Any] | None = None,
    ) -> IntegrationOAuthTokenDB:
        existing = await self.get_token(user_id, provider)
        encrypted_access = encrypt_integration_token(access_token)
        encrypted_refresh = (
            encrypt_integration_token(refresh_token) if refresh_token else None
        )

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
            user_id=user_id,
            provider=provider,
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

    async def delete_token(self, user_id: str, provider: str) -> bool:
        result = await self.db.execute(
            delete(IntegrationOAuthTokenDB).where(
                IntegrationOAuthTokenDB.user_id == user_id,
                IntegrationOAuthTokenDB.provider == provider,
            )
        )
        await self.db.commit()
        return result.rowcount > 0

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
