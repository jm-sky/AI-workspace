"""RAG types and retrieval contracts."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class RagSourceType(StrEnum):
    PASTE = "paste"
    ATTACHMENT = "attachment"
    WIKI = "wiki"


@dataclass(frozen=True)
class RetrievalAcl:
    """Permissions filter applied before vector ranking."""

    tenant_id: str
    user_id: str


@dataclass(frozen=True)
class RetrievalHit:
    """Single retrieval result from a chunk store."""

    id: str
    content: str
    score: float
    document_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ChunkRetriever(Protocol):
    """Permissions-aware chunk search (ACL before ranking)."""

    async def search(
        self,
        *,
        query_embedding: list[float],
        acl: RetrievalAcl,
        limit: int,
        min_similarity: float,
    ) -> list[RetrievalHit]: ...
