"""RAG search tool for the agent loop."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.agent.tools.base import AgentTool, AgentToolDefinition
from app.modules.rag.services.rag_service import RagService
from app.modules.tenants.service import TenantContext


class RagSearchTool(AgentTool):
    """Semantic search over user-ingested knowledge documents."""

    def __init__(
        self,
        *,
        tenant_ctx: TenantContext,
        db: AsyncSession,
        rag_enabled: bool = False,
    ):
        self.tenant_ctx = tenant_ctx
        self.rag_service = RagService(db)
        self.rag_enabled = rag_enabled

    @property
    def definition(self) -> AgentToolDefinition:
        return AgentToolDefinition(
            name="rag_search",
            description=(
                "Search the user's knowledge documents (pasted sources) semantically. "
                "Use for material stored as documents, not personal preferences "
                "(those belong in memory_search)."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max chunks to return (default 8)",
                    },
                },
                "required": ["query"],
            },
        )

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self.rag_enabled:
            return {
                "hits": [],
                "total": 0,
                "message": "RAG is disabled for this workspace",
            }

        query = str(arguments.get("query", "")).strip()
        if not query:
            return {"error": "query is required"}

        limit = int(arguments.get("limit") or settings.ai.rag_search_limit)
        hits = await self.rag_service.search(
            tenant_ctx=self.tenant_ctx,
            query=query,
            limit=min(limit, 50),
            rag_enabled=True,
        )
        return {
            "total": len(hits),
            "hits": [
                {
                    "id": hit.id,
                    "content": hit.content,
                    "score": hit.score,
                    "documentId": hit.documentId,
                    "title": hit.title,
                    "chunkIndex": hit.chunkIndex,
                }
                for hit in hits
            ],
        }
