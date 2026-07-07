"""Memory API router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.agent.dependencies import AgentTenantContext
from app.modules.auth.dependencies import CurrentUser
from app.modules.memory.schemas import (
    MemoryEntryCreate,
    MemoryEntryResponse,
    MemoryListResponse,
    MemorySearchRequest,
)
from app.modules.memory.services.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


def _get_memory_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MemoryService:
    return MemoryService(db)


@router.get("", response_model=MemoryListResponse)
async def list_memories(
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[MemoryService, Depends(_get_memory_service)],
    scope: str | None = Query(default=None),
    agent_key: str | None = Query(default=None, alias="agentKey"),
    session_id: str | None = Query(default=None, alias="sessionId"),
    search: str | None = Query(default=None, max_length=500),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> MemoryListResponse:
    _ = current_user
    entries, total = await service.list_entries(
        tenant_ctx=tenant_ctx,
        scope=scope,
        agent_key=agent_key,
        session_id=session_id,
        search_text=search,
        limit=limit,
        offset=offset,
    )
    return MemoryListResponse(entries=entries, total=total)


@router.post("/search", response_model=list[MemoryEntryResponse])
async def search_memories(
    request: MemorySearchRequest,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[MemoryService, Depends(_get_memory_service)],
) -> list[MemoryEntryResponse]:
    _ = current_user
    return await service.search(
        tenant_ctx=tenant_ctx,
        query=request.query,
        agent_key=request.agentKey,
        session_id=request.sessionId,
        scope=request.scope,
        limit=request.limit,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=MemoryEntryResponse)
async def create_memory(
    payload: MemoryEntryCreate,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[MemoryService, Depends(_get_memory_service)],
) -> MemoryEntryResponse:
    _ = current_user
    return await service.create_entry(
        tenant_ctx=tenant_ctx,
        content=payload.content,
        scope=payload.scope,
        agent_key=payload.agentKey,
        session_id=payload.sessionId,
        metadata=payload.metadata,
    )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    entry_id: str,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[MemoryService, Depends(_get_memory_service)],
) -> None:
    _ = current_user
    deleted = await service.delete_entry(tenant_ctx=tenant_ctx, entry_id=entry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
