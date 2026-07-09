"""Multi-turn chat session endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.agent.dependencies import AgentTenantContext
from app.modules.agent.schemas import (
    AgentSessionDetail,
    AgentSessionsListResponse,
)
from app.modules.agent.services.agent_run_service import AgentRunService
from app.modules.auth.dependencies import CurrentUser
from app.modules.integrations.repositories import (
    IntegrationTokenRepository,
    get_integration_token_repository,
)
from app.modules.integrations.service import IntegrationTokenService

router = APIRouter(prefix="/sessions", tags=["agent-sessions"])


def _get_agent_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    token_repo: Annotated[
        IntegrationTokenRepository, Depends(get_integration_token_repository)
    ],
) -> AgentRunService:
    return AgentRunService(db, IntegrationTokenService(token_repo))


@router.get("", response_model=AgentSessionsListResponse)
async def list_sessions(
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[AgentRunService, Depends(_get_agent_service)],
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AgentSessionsListResponse:
    sessions, total = await service.list_sessions(
        tenant_ctx=tenant_ctx,
        limit=limit,
        offset=offset,
    )
    return AgentSessionsListResponse(sessions=sessions, total=total)


@router.get("/{session_id}", response_model=AgentSessionDetail)
async def get_session(
    session_id: str,
    current_user: CurrentUser,
    service: Annotated[AgentRunService, Depends(_get_agent_service)],
) -> AgentSessionDetail:
    detail = await service.get_session_detail(session_id, user_id=current_user.id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return detail
