"""FastAPI dependencies for agent module."""

from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.auth.repositories import UserRepository, get_user_repository
from app.modules.teams.repositories import TeamRepository, get_team_repository
from app.modules.tenants.repositories import TenantRepository, get_tenant_repository
from app.modules.tenants.service import TenantContext, TenantWorkspaceService


async def require_tenant_context(
    current_user: CurrentUser,
    tenant_repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
    team_repo: Annotated[TeamRepository, Depends(get_team_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> TenantContext:
    service = TenantWorkspaceService(tenant_repo, team_repo, user_repo)
    ctx = await service.resolve_workspace_for_user(current_user)
    if ctx is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active tenant workspace — select or create a tenant first",
        )
    return ctx


AgentTenantContext = Annotated[TenantContext, Depends(require_tenant_context)]
