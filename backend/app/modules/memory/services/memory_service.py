"""Business logic for semantic memory."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.memory.db_models import MemoryEntry
from app.modules.memory.repositories import MemoryRepository
from app.modules.memory.schemas import MemoryEntryResponse
from app.modules.memory.services.embedding_service import EmbeddingService
from app.modules.memory.types import MemoryScope, MemorySource
from app.modules.tenants.service import TenantContext


class MemoryService:
    """Create, search, and manage tenant-scoped memories."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MemoryRepository(db)
        self._embedding: EmbeddingService | None = None

    def _embedder(self) -> EmbeddingService:
        if self._embedding is None:
            self._embedding = EmbeddingService()
        return self._embedding

    async def create_entry(
        self,
        *,
        tenant_ctx: TenantContext,
        content: str,
        scope: str = MemoryScope.USER.value,
        agent_key: str | None = None,
        session_id: str | None = None,
        source: str = MemorySource.USER.value,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntryResponse:
        embedding = await self._embedder().embed(content)
        entry = await self.repo.create(
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
            scope=scope,
            content=content,
            embedding=embedding,
            source=source,
            agent_key=agent_key,
            session_id=session_id,
            metadata=metadata,
        )
        await self.db.commit()
        return self._to_response(entry)

    async def search(
        self,
        *,
        tenant_ctx: TenantContext,
        query: str,
        agent_key: str | None = None,
        session_id: str | None = None,
        scope: str | None = None,
        limit: int = 10,
    ) -> list[MemoryEntryResponse]:
        if not settings.ai.memory_enabled:
            return []

        embedding = await self._embedder().embed(query)
        results = await self.repo.search_similar(
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
            embedding=embedding,
            agent_key=agent_key,
            session_id=session_id,
            limit=limit,
            min_similarity=settings.ai.memory_similarity_threshold,
        )

        if scope:
            results = [(entry, sim) for entry, sim in results if entry.scope == scope]

        return [self._to_response(entry, similarity=sim) for entry, sim in results]

    async def list_entries(
        self,
        *,
        tenant_ctx: TenantContext,
        scope: str | None = None,
        agent_key: str | None = None,
        session_id: str | None = None,
        search_text: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[MemoryEntryResponse], int]:
        entries, total = await self.repo.list_entries(
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
            scope=scope,
            agent_key=agent_key,
            session_id=session_id,
            search_text=search_text,
            limit=limit,
            offset=offset,
        )
        return [self._to_response(entry) for entry in entries], total

    async def delete_entry(
        self,
        *,
        tenant_ctx: TenantContext,
        entry_id: str,
    ) -> bool:
        deleted = await self.repo.delete(
            entry_id,
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
        )
        if deleted:
            await self.db.commit()
        return deleted

    async def build_injection_context(
        self,
        *,
        tenant_ctx: TenantContext,
        user_message: str,
        agent_key: str,
        session_id: str | None = None,
    ) -> str:
        """Return memories to prepend to the system prompt."""
        if not settings.ai.memory_enabled:
            return ""

        matches = await self.search(
            tenant_ctx=tenant_ctx,
            query=user_message,
            agent_key=agent_key,
            session_id=session_id,
            limit=settings.ai.memory_injection_limit,
        )
        if not matches:
            return ""

        lines = ["## Relevant memories (auto-retrieved)", ""]
        for item in matches:
            scope_label = item.scope
            if item.agentKey:
                scope_label = f"{item.scope}/{item.agentKey}"
            sim = f" (similarity {item.similarity:.2f})" if item.similarity else ""
            lines.append(f"- [{scope_label}{sim}] {item.content}")
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _to_response(
        entry: MemoryEntry,
        *,
        similarity: float | None = None,
    ) -> MemoryEntryResponse:
        return MemoryEntryResponse(
            id=entry.id,
            content=entry.content,
            scope=entry.scope,
            agentKey=entry.agent_key,
            sessionId=entry.session_id,
            source=entry.source,
            metadata=entry.entry_metadata,
            similarity=similarity,
            createdAt=entry.created_at,
            updatedAt=entry.updated_at,
        )
