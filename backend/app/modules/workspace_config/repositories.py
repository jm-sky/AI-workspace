"""Repository for workspace configuration entries."""

from datetime import UTC, datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.workspace_config.db_models import WorkspaceConfigEntryDB
from app.modules.workspace_config.types import ConfigScope


class WorkspaceConfigRepository:
    """Data access for workspace config entries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_entries_for_scope(
        self,
        *,
        scope: ConfigScope,
        scope_id: str | None,
        tenant_id: str | None = None,
    ) -> list[WorkspaceConfigEntryDB]:
        stmt = select(WorkspaceConfigEntryDB).where(WorkspaceConfigEntryDB.scope == scope.value)
        if scope_id is None:
            stmt = stmt.where(WorkspaceConfigEntryDB.scope_id.is_(None))
        else:
            stmt = stmt.where(WorkspaceConfigEntryDB.scope_id == scope_id)

        if tenant_id is None:
            stmt = stmt.where(WorkspaceConfigEntryDB.tenant_id.is_(None))
        else:
            stmt = stmt.where(WorkspaceConfigEntryDB.tenant_id == tenant_id)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def upsert_entry(
        self,
        *,
        scope: ConfigScope,
        scope_id: str | None,
        tenant_id: str | None,
        config_key: str,
        config_value: Any,
    ) -> WorkspaceConfigEntryDB:
        stmt = select(WorkspaceConfigEntryDB).where(
            WorkspaceConfigEntryDB.scope == scope.value,
            WorkspaceConfigEntryDB.config_key == config_key,
        )
        if scope_id is None:
            stmt = stmt.where(WorkspaceConfigEntryDB.scope_id.is_(None))
        else:
            stmt = stmt.where(WorkspaceConfigEntryDB.scope_id == scope_id)

        if tenant_id is None:
            stmt = stmt.where(WorkspaceConfigEntryDB.tenant_id.is_(None))
        else:
            stmt = stmt.where(WorkspaceConfigEntryDB.tenant_id == tenant_id)

        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.config_value = config_value
            existing.updated_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        entry = WorkspaceConfigEntryDB(
            id=generate_id(),
            scope=scope.value,
            scope_id=scope_id,
            tenant_id=tenant_id,
            config_key=config_key,
            config_value=config_value,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def delete_entry(
        self,
        *,
        scope: ConfigScope,
        scope_id: str | None,
        tenant_id: str | None,
        config_key: str,
    ) -> bool:
        stmt = delete(WorkspaceConfigEntryDB).where(
            WorkspaceConfigEntryDB.scope == scope.value,
            WorkspaceConfigEntryDB.config_key == config_key,
        )
        if scope_id is None:
            stmt = stmt.where(WorkspaceConfigEntryDB.scope_id.is_(None))
        else:
            stmt = stmt.where(WorkspaceConfigEntryDB.scope_id == scope_id)

        if tenant_id is None:
            stmt = stmt.where(WorkspaceConfigEntryDB.tenant_id.is_(None))
        else:
            stmt = stmt.where(WorkspaceConfigEntryDB.tenant_id == tenant_id)

        result = await self.db.execute(stmt)
        await self.db.commit()
        return (result.rowcount or 0) > 0  # type: ignore[attr-defined]


def get_workspace_config_repository(
    db: AsyncSession = Depends(get_db),
) -> WorkspaceConfigRepository:
    return WorkspaceConfigRepository(db)
