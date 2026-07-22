"""API router for team management within a tenant."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.teams.repositories import TeamRepository, get_team_repository
from app.modules.teams.schemas import (
    TeamCreateRequest,
    TeamListResponse,
    TeamResponse,
)
from app.modules.tenants.dependencies import CurrentTenantContext
from app.modules.tenants.repositories import TenantRepository, get_tenant_repository
from app.modules.tenants.service import TenantContext

router = APIRouter(prefix="/tenants/{tenant_id}/teams", tags=["Teams"])


def _require_tenant_access(tenant_ctx: TenantContext, tenant_id: str) -> None:
    if tenant_ctx.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")


@router.get("", response_model=TeamListResponse)
async def list_teams(
    tenant_id: str,
    tenant_ctx: CurrentTenantContext,
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
) -> TeamListResponse:
    _require_tenant_access(tenant_ctx, tenant_id)

    items = await repo.list_for_user_in_tenant(
        user_id=tenant_ctx.user_id,
        tenant_id=tenant_id,
    )
    teams = [
        TeamResponse(
            id=team.id,
            tenantId=team.tenant_id,
            name=team.name,
            description=team.description,
            role=membership.role,
            createdAt=team.created_at,
        )
        for team, membership in items
    ]
    return TeamListResponse(teams=teams)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TeamResponse)
async def create_team(
    tenant_id: str,
    payload: TeamCreateRequest,
    tenant_ctx: CurrentTenantContext,
    repo: Annotated[TeamRepository, Depends(get_team_repository)],
    tenant_repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
) -> TeamResponse:
    _require_tenant_access(tenant_ctx, tenant_id)

    membership = await tenant_repo.get_membership(tenant_id, tenant_ctx.user_id)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a tenant member")
    if membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant owner or admin can create teams",
        )

    team, team_membership = await repo.create_team(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        creator_user_id=tenant_ctx.user_id,
    )
    return TeamResponse(
        id=team.id,
        tenantId=team.tenant_id,
        name=team.name,
        description=team.description,
        role=team_membership.role,
        createdAt=team.created_at,
    )
