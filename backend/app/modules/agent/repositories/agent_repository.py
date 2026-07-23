"""Persistence for tenant-scoped agent definitions."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.modules.agent.db_models import AgentDB


class AgentRepository:
    """CRUD for ``agents`` table."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_tenant(
        self,
        tenant_id: str,
        *,
        enabled_only: bool = False,
    ) -> list[AgentDB]:
        stmt = select(AgentDB).where(AgentDB.tenant_id == tenant_id)
        if enabled_only:
            stmt = stmt.where(AgentDB.is_enabled.is_(True))
        stmt = stmt.order_by(AgentDB.is_default.desc(), AgentDB.name.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, agent_id: str, *, tenant_id: str) -> AgentDB | None:
        stmt = select(AgentDB).where(
            AgentDB.id == agent_id,
            AgentDB.tenant_id == tenant_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_key(self, tenant_id: str, key: str) -> AgentDB | None:
        stmt = select(AgentDB).where(
            AgentDB.tenant_id == tenant_id,
            AgentDB.key == key,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_default(self, tenant_id: str) -> AgentDB | None:
        stmt = select(AgentDB).where(
            AgentDB.tenant_id == tenant_id,
            AgentDB.is_default.is_(True),
            AgentDB.is_enabled.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        tenant_id: str,
        key: str,
        name: str,
        description: str,
        system_prompt: str,
        model: str | None = None,
        effort: str | None = None,
        tool_profile: list[str] | None = None,
        memory_scopes: list[str] | None = None,
        rag_enabled: bool = False,
        routing_hints: dict[str, Any] | None = None,
        is_enabled: bool = True,
        is_default: bool = False,
        created_by: str | None = None,
    ) -> AgentDB:
        agent = AgentDB(
            id=generate_id(),
            tenant_id=tenant_id,
            key=key,
            name=name,
            description=description,
            system_prompt=system_prompt,
            model=model,
            effort=effort,
            tool_profile=tool_profile or [],
            memory_scopes=memory_scopes or ["session", "user", "agent"],
            rag_enabled=rag_enabled,
            routing_hints=routing_hints or {},
            visibility="tenant",
            is_enabled=is_enabled,
            is_default=is_default,
            created_by=created_by,
        )
        self.db.add(agent)
        await self.db.flush()
        return agent

    async def clear_default(self, tenant_id: str, *, except_id: str | None = None) -> None:
        stmt = (
            update(AgentDB)
            .where(AgentDB.tenant_id == tenant_id, AgentDB.is_default.is_(True))
            .values(is_default=False, updated_at=datetime.now(UTC))
        )
        if except_id:
            stmt = stmt.where(AgentDB.id != except_id)
        await self.db.execute(stmt)

    async def touch(self, agent: AgentDB) -> AgentDB:
        agent.updated_at = datetime.now(UTC)
        await self.db.flush()
        return agent
