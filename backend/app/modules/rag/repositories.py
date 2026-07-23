"""Persistence for RAG documents and chunks."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.embeddings import EmbeddingService
from app.common.id_utils import generate_id
from app.modules.rag.db_models import DocumentChunk, RagDocument
from app.modules.rag.types import RetrievalAcl, RetrievalHit


class RagRepository:
    """CRUD + permissions-aware vector search for document chunks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(
        self,
        *,
        tenant_id: str,
        user_id: str,
        title: str,
        source_type: str = "paste",
        source_ref: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RagDocument:
        now = datetime.now(UTC)
        doc = RagDocument(
            id=generate_id(),
            tenant_id=tenant_id,
            user_id=user_id,
            title=title,
            source_type=source_type,
            source_ref=source_ref,
            metadata_=metadata,
            created_at=now,
            updated_at=now,
        )
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def insert_chunk(
        self,
        *,
        document_id: str,
        tenant_id: str,
        user_id: str,
        chunk_index: int,
        content: str,
        embedding: list[float],
        token_estimate: int | None = None,
    ) -> str:
        chunk_id = generate_id()
        now = datetime.now(UTC)
        vector_literal = EmbeddingService.vector_to_pg_literal(embedding)
        await self.db.execute(
            text("""
                INSERT INTO document_chunks (
                    id, document_id, tenant_id, user_id, chunk_index,
                    content, token_estimate, embedding, created_at
                ) VALUES (
                    :id, :document_id, :tenant_id, :user_id, :chunk_index,
                    :content, :token_estimate, CAST(:embedding AS vector), :created_at
                )
                """),
            {
                "id": chunk_id,
                "document_id": document_id,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "chunk_index": chunk_index,
                "content": content,
                "token_estimate": token_estimate,
                "embedding": vector_literal,
                "created_at": now,
            },
        )
        return chunk_id

    async def get_document(
        self,
        document_id: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> RagDocument | None:
        result = await self.db.execute(
            select(RagDocument).where(
                RagDocument.id == document_id,
                RagDocument.tenant_id == tenant_id,
                RagDocument.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        *,
        tenant_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[tuple[RagDocument, int]], int]:
        count_result = await self.db.execute(
            select(func.count())
            .select_from(RagDocument)
            .where(
                RagDocument.tenant_id == tenant_id,
                RagDocument.user_id == user_id,
            )
        )
        total = int(count_result.scalar() or 0)

        chunk_count = (
            select(func.count())
            .select_from(DocumentChunk)
            .where(DocumentChunk.document_id == RagDocument.id)
            .correlate(RagDocument)
            .scalar_subquery()
        )
        result = await self.db.execute(
            select(RagDocument, chunk_count.label("chunk_count"))
            .where(
                RagDocument.tenant_id == tenant_id,
                RagDocument.user_id == user_id,
            )
            .order_by(RagDocument.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = [(row[0], int(row[1] or 0)) for row in result.all()]
        return rows, total

    async def list_chunks(
        self,
        document_id: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.tenant_id == tenant_id,
                DocumentChunk.user_id == user_id,
            )
            .order_by(DocumentChunk.chunk_index.asc())
        )
        return list(result.scalars().all())

    async def delete_document(
        self,
        document_id: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> bool:
        doc = await self.get_document(document_id, tenant_id=tenant_id, user_id=user_id)
        if doc is None:
            return False
        await self.db.execute(
            delete(RagDocument).where(
                RagDocument.id == document_id,
                RagDocument.tenant_id == tenant_id,
                RagDocument.user_id == user_id,
            )
        )
        return True

    async def search_chunks(
        self,
        *,
        query_embedding: list[float],
        acl: RetrievalAcl,
        limit: int = 8,
        min_similarity: float = 0.5,
    ) -> list[RetrievalHit]:
        """Vector search with tenant/user ACL filtering before ranking."""
        vector_literal = EmbeddingService.vector_to_pg_literal(query_embedding)
        result = await self.db.execute(
            text("""
                SELECT
                    c.id,
                    c.content,
                    c.document_id,
                    c.chunk_index,
                    d.title,
                    1 - (c.embedding <=> CAST(:query_vec AS vector)) AS similarity
                FROM document_chunks c
                JOIN rag_documents d ON d.id = c.document_id
                WHERE c.tenant_id = :tenant_id
                  AND c.user_id = :user_id
                  AND c.embedding IS NOT NULL
                  AND 1 - (c.embedding <=> CAST(:query_vec AS vector)) >= :min_similarity
                ORDER BY c.embedding <=> CAST(:query_vec AS vector)
                LIMIT :limit
                """),
            {
                "tenant_id": acl.tenant_id,
                "user_id": acl.user_id,
                "query_vec": vector_literal,
                "min_similarity": min_similarity,
                "limit": limit,
            },
        )
        hits: list[RetrievalHit] = []
        for row in result.mappings().all():
            hits.append(
                RetrievalHit(
                    id=row["id"],
                    content=row["content"],
                    score=float(row["similarity"]),
                    document_id=row["document_id"],
                    metadata={
                        "title": row["title"],
                        "chunkIndex": row["chunk_index"],
                    },
                )
            )
        return hits


class PgChunkRetriever:
    """ChunkRetriever backed by Postgres/pgvector."""

    def __init__(self, repo: RagRepository):
        self._repo = repo

    async def search(
        self,
        *,
        query_embedding: list[float],
        acl: RetrievalAcl,
        limit: int,
        min_similarity: float,
    ) -> list[RetrievalHit]:
        return await self._repo.search_chunks(
            query_embedding=query_embedding,
            acl=acl,
            limit=limit,
            min_similarity=min_similarity,
        )
