"""Business logic for document RAG ingest and search."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.embeddings import EmbeddingService
from app.core.config import settings
from app.modules.rag.chunker import split_text
from app.modules.rag.repositories import PgChunkRetriever, RagRepository
from app.modules.rag.schemas import (
    RagChunkResponse,
    RagDocumentDetailResponse,
    RagDocumentResponse,
    RagSearchHit,
)
from app.modules.rag.types import RetrievalAcl, RagSourceType
from app.modules.tenants.service import TenantContext


class RagService:
    """Ingest pasted text, search chunks with ACL, manage documents."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RagRepository(db)
        self.retriever = PgChunkRetriever(self.repo)
        self._embedding: EmbeddingService | None = None

    def _embedder(self) -> EmbeddingService:
        if self._embedding is None:
            self._embedding = EmbeddingService()
        return self._embedding

    async def ingest_paste(
        self,
        *,
        tenant_ctx: TenantContext,
        title: str,
        content: str,
    ) -> RagDocumentResponse:
        chunks = split_text(
            content,
            chunk_size=settings.ai.rag_chunk_size,
            overlap=settings.ai.rag_chunk_overlap,
            max_chunks=settings.ai.rag_max_chunks_per_document,
        )
        if not chunks:
            raise ValueError("content produced no chunks")

        doc = await self.repo.create_document(
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
            title=title.strip(),
            source_type=RagSourceType.PASTE.value,
        )

        embedder = self._embedder()
        for index, piece in enumerate(chunks):
            embedding = await embedder.embed(piece)
            await self.repo.insert_chunk(
                document_id=doc.id,
                tenant_id=tenant_ctx.tenant_id,
                user_id=tenant_ctx.user_id,
                chunk_index=index,
                content=piece,
                embedding=embedding,
                token_estimate=max(1, len(piece) // 4),
            )

        await self.db.commit()
        return RagDocumentResponse(
            id=doc.id,
            title=doc.title,
            sourceType=doc.source_type,
            sourceRef=doc.source_ref,
            metadata=doc.metadata_,
            chunkCount=len(chunks),
            createdAt=doc.created_at,
            updatedAt=doc.updated_at,
        )

    async def list_documents(
        self,
        *,
        tenant_ctx: TenantContext,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[RagDocumentResponse], int]:
        rows, total = await self.repo.list_documents(
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
            limit=limit,
            offset=offset,
        )
        items = [
            RagDocumentResponse(
                id=doc.id,
                title=doc.title,
                sourceType=doc.source_type,
                sourceRef=doc.source_ref,
                metadata=doc.metadata_,
                chunkCount=chunk_count,
                createdAt=doc.created_at,
                updatedAt=doc.updated_at,
            )
            for doc, chunk_count in rows
        ]
        return items, total

    async def get_document(
        self,
        *,
        tenant_ctx: TenantContext,
        document_id: str,
    ) -> RagDocumentDetailResponse | None:
        doc = await self.repo.get_document(
            document_id,
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
        )
        if doc is None:
            return None
        chunks = await self.repo.list_chunks(
            document_id,
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
        )
        return RagDocumentDetailResponse(
            id=doc.id,
            title=doc.title,
            sourceType=doc.source_type,
            sourceRef=doc.source_ref,
            metadata=doc.metadata_,
            chunkCount=len(chunks),
            createdAt=doc.created_at,
            updatedAt=doc.updated_at,
            chunks=[
                RagChunkResponse(
                    id=chunk.id,
                    chunkIndex=chunk.chunk_index,
                    content=chunk.content,
                    tokenEstimate=chunk.token_estimate,
                )
                for chunk in chunks
            ],
        )

    async def delete_document(
        self,
        *,
        tenant_ctx: TenantContext,
        document_id: str,
    ) -> bool:
        deleted = await self.repo.delete_document(
            document_id,
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
        )
        if deleted:
            await self.db.commit()
        return deleted

    async def search(
        self,
        *,
        tenant_ctx: TenantContext,
        query: str,
        limit: int | None = None,
        rag_enabled: bool = True,
    ) -> list[RagSearchHit]:
        if not rag_enabled:
            return []

        embedder = self._embedder()
        query_embedding = await embedder.embed(query)
        hits = await self.retriever.search(
            query_embedding=query_embedding,
            acl=RetrievalAcl(
                tenant_id=tenant_ctx.tenant_id,
                user_id=tenant_ctx.user_id,
            ),
            limit=limit or settings.ai.rag_search_limit,
            min_similarity=settings.ai.rag_similarity_threshold,
        )
        return [
            RagSearchHit(
                id=hit.id,
                content=hit.content,
                score=hit.score,
                documentId=hit.document_id,
                title=str(hit.metadata.get("title") or ""),
                chunkIndex=int(hit.metadata.get("chunkIndex") or 0),
            )
            for hit in hits
        ]
