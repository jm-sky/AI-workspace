"""Tests for RAG chunker, ACL search gate, and rag_search tool."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.rag.chunker import split_text
from app.modules.rag.db_models import RagDocument
from app.modules.rag.services.rag_service import RagService
from app.modules.rag.types import RetrievalAcl, RetrievalHit
from app.modules.tenants.service import TenantContext


def test_split_text_basic_overlap():
    text = "a" * 2500
    chunks = split_text(text, chunk_size=1000, overlap=100, max_chunks=10)
    assert len(chunks) == 3
    assert all(len(c) <= 1000 for c in chunks)


def test_split_text_skips_whitespace_only():
    assert split_text("   \n\t  ") == []


def test_split_text_respects_max_chunks():
    text = "x" * 10_000
    chunks = split_text(text, chunk_size=500, overlap=0, max_chunks=3)
    assert len(chunks) == 3


def test_split_text_rejects_bad_overlap():
    with pytest.raises(ValueError, match="overlap"):
        split_text("hello", chunk_size=10, overlap=10)


def _tenant_ctx(tenant_id: str = "tenant-a", user_id: str = "user-a") -> TenantContext:
    return TenantContext(tenant_id=tenant_id, user_id=user_id, tenant_role="member")


@pytest.mark.asyncio
async def test_search_returns_empty_when_rag_disabled():
    service = RagService(AsyncMock())
    service._embedding = MagicMock()
    service._embedding.embed = AsyncMock(return_value=[0.1])
    service.retriever = MagicMock()
    service.retriever.search = AsyncMock()

    hits = await service.search(
        tenant_ctx=_tenant_ctx(),
        query="anything",
        rag_enabled=False,
    )

    assert hits == []
    service._embedding.embed.assert_not_awaited()
    service.retriever.search.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_maps_retriever_hits():
    service = RagService(AsyncMock())
    service._embedding = MagicMock()
    service._embedding.embed = AsyncMock(return_value=[0.2, 0.3])
    service.retriever = MagicMock()
    service.retriever.search = AsyncMock(
        return_value=[
            RetrievalHit(
                id="chunk-1",
                content="Hello world",
                score=0.9,
                document_id="doc-1",
                metadata={"title": "Doc", "chunkIndex": 0},
            )
        ]
    )

    hits = await service.search(
        tenant_ctx=_tenant_ctx(),
        query="hello",
        limit=5,
        rag_enabled=True,
    )

    assert len(hits) == 1
    assert hits[0].documentId == "doc-1"
    assert hits[0].title == "Doc"
    service.retriever.search.assert_awaited_once()
    call_kwargs = service.retriever.search.await_args.kwargs
    assert call_kwargs["acl"] == RetrievalAcl(tenant_id="tenant-a", user_id="user-a")
    assert call_kwargs["limit"] == 5


@pytest.mark.asyncio
async def test_ingest_paste_embeds_each_chunk():
    db = AsyncMock()
    service = RagService(db)
    now = datetime.now(UTC)
    doc = RagDocument(
        id="doc-1",
        tenant_id="tenant-a",
        user_id="user-a",
        title="Note",
        source_type="paste",
        source_ref=None,
        metadata_=None,
        created_at=now,
        updated_at=now,
    )
    service.repo = MagicMock()
    service.repo.create_document = AsyncMock(return_value=doc)
    service.repo.insert_chunk = AsyncMock(return_value="chunk-id")
    service._embedding = MagicMock()
    service._embedding.embed = AsyncMock(side_effect=lambda text: [float(len(text))])

    with patch(
        "app.modules.rag.services.rag_service.split_text",
        return_value=["chunk-a", "chunk-b"],
    ):
        result = await service.ingest_paste(
            tenant_ctx=_tenant_ctx(),
            title="Note",
            content="ignored body",
        )

    assert result.chunkCount == 2
    assert service._embedding.embed.await_count == 2
    assert service.repo.insert_chunk.await_count == 2
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_document_acl_miss():
    db = AsyncMock()
    service = RagService(db)
    service.repo = MagicMock()
    service.repo.delete_document = AsyncMock(return_value=False)

    deleted = await service.delete_document(
        tenant_ctx=_tenant_ctx(tenant_id="other", user_id="other"),
        document_id="doc-1",
    )

    assert deleted is False
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_rag_search_tool_disabled():
    from app.modules.agent.tools.rag import RagSearchTool

    tool = RagSearchTool(
        tenant_ctx=_tenant_ctx(),
        db=AsyncMock(),
        rag_enabled=False,
    )
    result = await tool.execute({"query": "test"})
    assert result["hits"] == []
    assert "disabled" in result["message"].lower()


@pytest.mark.asyncio
async def test_rag_search_tool_requires_query():
    from app.modules.agent.tools.rag import RagSearchTool

    tool = RagSearchTool(
        tenant_ctx=_tenant_ctx(),
        db=AsyncMock(),
        rag_enabled=True,
    )
    assert await tool.execute({}) == {"error": "query is required"}
