"""Persistence for semantic memory entries."""

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.modules.memory.db_models import MemoryEntry
from app.modules.memory.services.embedding_service import EmbeddingService


class MemoryRepository:
    """CRUD and vector search for memory_entries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        tenant_id: str,
        user_id: str,
        scope: str,
        content: str,
        embedding: list[float],
        source: str = "user",
        agent_key: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        entry_id = generate_id()
        now = datetime.now(UTC)
        vector_literal = EmbeddingService.vector_to_pg_literal(embedding)

        await self.db.execute(
            text(
                """
                INSERT INTO memory_entries (
                    id, tenant_id, user_id, scope, agent_key, session_id,
                    content, source, entry_metadata, embedding, created_at, updated_at
                ) VALUES (
                    :id, :tenant_id, :user_id, :scope, :agent_key, :session_id,
                    :content, :source, CAST(:metadata AS jsonb), CAST(:embedding AS vector), :created_at, :updated_at
                )
                """
            ),
            {
                "id": entry_id,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "scope": scope,
                "agent_key": agent_key,
                "session_id": session_id,
                "content": content,
                "source": source,
                "metadata": json.dumps(metadata) if metadata is not None else None,
                "embedding": vector_literal,
                "created_at": now,
                "updated_at": now,
            },
        )

        entry = MemoryEntry(
            id=entry_id,
            tenant_id=tenant_id,
            user_id=user_id,
            scope=scope,
            agent_key=agent_key,
            session_id=session_id,
            content=content,
            source=source,
            entry_metadata=metadata,
            created_at=now,
            updated_at=now,
        )
        return entry

    async def get_by_id(
        self,
        entry_id: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> MemoryEntry | None:
        result = await self.db.execute(
            select(MemoryEntry).where(
                MemoryEntry.id == entry_id,
                MemoryEntry.tenant_id == tenant_id,
                MemoryEntry.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(
        self,
        entry_id: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> bool:
        entry = await self.get_by_id(entry_id, tenant_id=tenant_id, user_id=user_id)
        if entry is None:
            return False
        await self.db.delete(entry)
        return True

    async def list_entries(
        self,
        *,
        tenant_id: str,
        user_id: str,
        scope: str | None = None,
        agent_key: str | None = None,
        session_id: str | None = None,
        search_text: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[MemoryEntry], int]:
        query = select(MemoryEntry).where(
            MemoryEntry.tenant_id == tenant_id,
            MemoryEntry.user_id == user_id,
        )
        count_query = select(func.count()).select_from(MemoryEntry).where(
            MemoryEntry.tenant_id == tenant_id,
            MemoryEntry.user_id == user_id,
        )

        if scope:
            query = query.where(MemoryEntry.scope == scope)
            count_query = count_query.where(MemoryEntry.scope == scope)
        if agent_key:
            query = query.where(MemoryEntry.agent_key == agent_key)
            count_query = count_query.where(MemoryEntry.agent_key == agent_key)
        if session_id:
            query = query.where(MemoryEntry.session_id == session_id)
            count_query = count_query.where(MemoryEntry.session_id == session_id)
        if search_text:
            pattern = f"%{search_text}%"
            query = query.where(MemoryEntry.content.ilike(pattern))
            count_query = count_query.where(MemoryEntry.content.ilike(pattern))

        total_result = await self.db.execute(count_query)
        total = int(total_result.scalar() or 0)

        result = await self.db.execute(
            query.order_by(MemoryEntry.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    @staticmethod
    def _scope_filter_sql(
        agent_key: str | None,
        session_id: str | None,
    ) -> str:
        """Build scope ACL clause without nullable-parameter IS NULL checks (asyncpg typing)."""
        clauses = ["scope = 'user'"]
        if agent_key is None:
            clauses.append("scope = 'agent'")
        else:
            clauses.append("(scope = 'agent' AND agent_key = :agent_key)")
        if session_id is None:
            clauses.append("scope = 'session'")
        else:
            clauses.append("(scope = 'session' AND session_id = :session_id)")
        return f"({' OR '.join(clauses)})"

    async def search_similar(
        self,
        *,
        tenant_id: str,
        user_id: str,
        embedding: list[float],
        agent_key: str | None = None,
        session_id: str | None = None,
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> list[tuple[MemoryEntry, float]]:
        """Vector similarity search with tenant/user ACL filtering."""
        vector_literal = EmbeddingService.vector_to_pg_literal(embedding)

        scope_filter = self._scope_filter_sql(agent_key, session_id)

        result = await self.db.execute(
            text(
                f"""
                SELECT
                    id, tenant_id, user_id, scope, agent_key, session_id,
                    content, source, entry_metadata, created_at, updated_at,
                    1 - (embedding <=> CAST(:query_vec AS vector)) AS similarity
                FROM memory_entries
                WHERE tenant_id = :tenant_id
                  AND user_id = :user_id
                  AND embedding IS NOT NULL
                  AND {scope_filter}
                  AND 1 - (embedding <=> CAST(:query_vec AS vector)) >= :min_similarity
                ORDER BY embedding <=> CAST(:query_vec AS vector)
                LIMIT :limit
                """
            ),
            {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "agent_key": agent_key,
                "session_id": session_id,
                "query_vec": vector_literal,
                "min_similarity": min_similarity,
                "limit": limit,
            },
        )

        rows: list[tuple[MemoryEntry, float]] = []
        for row in result.mappings().all():
            entry = MemoryEntry(
                id=row["id"],
                tenant_id=row["tenant_id"],
                user_id=row["user_id"],
                scope=row["scope"],
                agent_key=row["agent_key"],
                session_id=row["session_id"],
                content=row["content"],
                source=row["source"],
                entry_metadata=row["entry_metadata"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            rows.append((entry, float(row["similarity"])))
        return rows


def get_memory_repository(db: AsyncSession) -> MemoryRepository:
    return MemoryRepository(db)
