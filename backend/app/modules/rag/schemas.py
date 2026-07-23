"""Pydantic schemas for RAG API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RagDocumentCreate(BaseModel):
    """Ingest a pasted text document."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1, max_length=100_000)


class RagDocumentResponse(BaseModel):
    """Document metadata (no embeddings)."""

    id: str
    title: str
    sourceType: str
    sourceRef: str | None = None
    metadata: dict[str, Any] | None = None
    chunkCount: int = 0
    createdAt: datetime
    updatedAt: datetime


class RagDocumentListResponse(BaseModel):
    documents: list[RagDocumentResponse]
    total: int


class RagChunkResponse(BaseModel):
    id: str
    chunkIndex: int
    content: str
    tokenEstimate: int | None = None


class RagDocumentDetailResponse(RagDocumentResponse):
    chunks: list[RagChunkResponse] = Field(default_factory=list)


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    limit: int = Field(default=8, ge=1, le=50)


class RagSearchHit(BaseModel):
    id: str
    content: str
    score: float
    documentId: str
    title: str
    chunkIndex: int


class RagSearchResponse(BaseModel):
    hits: list[RagSearchHit]
    total: int
