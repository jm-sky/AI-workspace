"""Pydantic schemas for memory API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


MemoryScopeLiteral = Literal["session", "user", "agent"]


class MemoryEntryCreate(BaseModel):
    """Create a memory entry."""

    content: str = Field(..., min_length=1, max_length=8000)
    scope: MemoryScopeLiteral = "user"
    agentKey: str | None = Field(default=None, alias="agent_key")
    sessionId: str | None = Field(default=None, alias="session_id")
    metadata: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}


class MemoryEntryResponse(BaseModel):
    """Memory entry returned to clients."""

    id: str
    content: str
    scope: str
    agentKey: str | None = None
    sessionId: str | None = None
    source: str
    metadata: dict[str, Any] | None = None
    similarity: float | None = None
    createdAt: datetime
    updatedAt: datetime


class MemoryListResponse(BaseModel):
    """Paginated memory list."""

    entries: list[MemoryEntryResponse]
    total: int


class MemorySearchRequest(BaseModel):
    """Semantic search over memories."""

    query: str = Field(..., min_length=1, max_length=2000)
    scope: MemoryScopeLiteral | None = None
    agentKey: str | None = Field(default=None, alias="agent_key")
    sessionId: str | None = Field(default=None, alias="session_id")
    limit: int = Field(default=10, ge=1, le=50)

    model_config = {"populate_by_name": True}
