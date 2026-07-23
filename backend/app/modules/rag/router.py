"""RAG API router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.agent.dependencies import AgentTenantContext
from app.modules.auth.dependencies import CurrentUser
from app.modules.rag.schemas import (
    RagDocumentCreate,
    RagDocumentDetailResponse,
    RagDocumentListResponse,
    RagDocumentResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from app.modules.rag.services.rag_service import RagService
from app.modules.workspace_config.repositories import WorkspaceConfigRepository
from app.modules.workspace_config.resolver import WorkspaceConfigResolver

router = APIRouter(prefix="/rag", tags=["rag"])


def _get_rag_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RagService:
    return RagService(db)


async def _resolve_rag_enabled(
    db: AsyncSession,
    tenant_ctx: AgentTenantContext,
) -> bool:
    resolver = WorkspaceConfigResolver(WorkspaceConfigRepository(db))
    effective = await resolver.resolve(
        user_id=tenant_ctx.user_id,
        tenant_id=tenant_ctx.tenant_id,
        team_id=tenant_ctx.team_id,
    )
    return effective.ragEnabled


@router.post("/documents", status_code=status.HTTP_201_CREATED, response_model=RagDocumentResponse)
async def create_document(
    payload: RagDocumentCreate,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[RagService, Depends(_get_rag_service)],
) -> RagDocumentResponse:
    _ = current_user
    try:
        return await service.ingest_paste(
            tenant_ctx=tenant_ctx,
            title=payload.title,
            content=payload.content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/documents", response_model=RagDocumentListResponse)
async def list_documents(
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[RagService, Depends(_get_rag_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> RagDocumentListResponse:
    _ = current_user
    documents, total = await service.list_documents(
        tenant_ctx=tenant_ctx,
        limit=limit,
        offset=offset,
    )
    return RagDocumentListResponse(documents=documents, total=total)


@router.get("/documents/{document_id}", response_model=RagDocumentDetailResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[RagService, Depends(_get_rag_service)],
) -> RagDocumentDetailResponse:
    _ = current_user
    detail = await service.get_document(tenant_ctx=tenant_ctx, document_id=document_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return detail


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[RagService, Depends(_get_rag_service)],
) -> None:
    _ = current_user
    deleted = await service.delete_document(tenant_ctx=tenant_ctx, document_id=document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.post("/search", response_model=RagSearchResponse)
async def search_documents(
    request: RagSearchRequest,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[RagService, Depends(_get_rag_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RagSearchResponse:
    _ = current_user
    rag_enabled = await _resolve_rag_enabled(db, tenant_ctx)
    hits = await service.search(
        tenant_ctx=tenant_ctx,
        query=request.query,
        limit=request.limit,
        rag_enabled=rag_enabled,
    )
    return RagSearchResponse(hits=hits, total=len(hits))
