"""Agent run audit endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.agent.dependencies import AgentTenantContext
from app.modules.agent.repositories import AgentRunRepository
from app.modules.agent.schemas import AgentRunResponse, AgentRunsListResponse
from app.modules.agent.services.agent_run_service import AgentRunService, _to_run_response
from app.modules.auth.dependencies import AdminUser, CurrentUser
from app.modules.integrations.repositories import (
    IntegrationTokenRepository,
    get_integration_token_repository,
)
from app.modules.integrations.service import IntegrationTokenService

router = APIRouter(prefix="/runs", tags=["agent-runs"])


def _get_agent_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    token_repo: Annotated[
        IntegrationTokenRepository, Depends(get_integration_token_repository)
    ],
) -> AgentRunService:
    return AgentRunService(db, IntegrationTokenService(token_repo))


@router.get("", response_model=AgentRunsListResponse)
async def list_runs(
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[AgentRunService, Depends(_get_agent_service)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AgentRunsListResponse:
    runs, total = await service.list_runs(
        tenant_ctx=tenant_ctx,
        limit=limit,
        offset=offset,
    )
    return AgentRunsListResponse(runs=runs, total=total)


@router.get("/{run_id}", response_model=AgentRunResponse)
async def get_run(
    run_id: str,
    current_user: CurrentUser,
    service: Annotated[AgentRunService, Depends(_get_agent_service)],
) -> AgentRunResponse:
    run = await service.get_run(run_id, user_id=current_user.id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


@router.get("/{run_id}/export")
async def export_run(
    run_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Export run trace (summary tier — redacted) for the owner, incl. system prompt."""
    repo = AgentRunRepository(db)
    run = await repo.get_run(run_id, user_id=current_user.id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    steps = await repo.get_steps(run_id)
    return _to_run_response(run, steps).model_dump(mode="json")


@router.get("/{run_id}/raw")
async def export_run_raw(
    run_id: str,
    admin_user: AdminUser,
    service: Annotated[AgentRunService, Depends(_get_agent_service)],
) -> dict:
    """Admin-only: full (raw) trace payloads; expired raw is withheld by retention."""
    raw = await service.get_run_raw(run_id)
    if raw is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return raw
