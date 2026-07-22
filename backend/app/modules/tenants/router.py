"""API router for tenant management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.auth_utils import verify_token
from app.modules.auth.dependencies import CurrentUser, get_current_token
from app.modules.tenants.db_models import TenantDB, TenantMembershipDB
from app.modules.tenants.repositories import TenantRepository, get_tenant_repository
from app.modules.tenants.schemas import (
    SwitchTenantRequest,
    SwitchTenantResponse,
    TenantCreateRequest,
    TenantListResponse,
    TenantResponse,
)
from app.modules.tenants.service import (
    TenantWorkspaceService,
    get_tenant_workspace_service,
)

router = APIRouter(prefix="/tenants", tags=["Tenants"])


def _switch_response(
    *,
    tokens: dict[str, str | int],
    tenant: TenantDB,
    membership: TenantMembershipDB,
    team_id: str | None,
) -> SwitchTenantResponse:
    return SwitchTenantResponse(
        accessToken=str(tokens["accessToken"]),
        refreshToken=str(tokens["refreshToken"]),
        tokenType=str(tokens["tokenType"]),
        expiresIn=int(tokens["expiresIn"]),
        tenant=TenantResponse(
            id=tenant.id,
            name=tenant.name,
            description=tenant.description,
            role=membership.role,
            createdAt=tenant.created_at,
        ),
        teamId=team_id,
    )


@router.get("", response_model=TenantListResponse)
async def list_tenants(
    current_user: CurrentUser,
    repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
) -> TenantListResponse:
    items = await repo.list_for_user(current_user.id)
    tenants = [
        TenantResponse(
            id=tenant.id,
            name=tenant.name,
            description=tenant.description,
            role=membership.role,
            createdAt=tenant.created_at,
        )
        for tenant, membership in items
    ]
    return TenantListResponse(tenants=tenants)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SwitchTenantResponse)
async def create_tenant(
    payload: TenantCreateRequest,
    current_user: CurrentUser,
    token: Annotated[str, Depends(get_current_token)],
    repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
    workspace_service: Annotated[TenantWorkspaceService, Depends(get_tenant_workspace_service)],
) -> SwitchTenantResponse:
    tenant, membership = await repo.create_tenant(
        name=payload.name,
        description=payload.description,
        owner_user_id=current_user.id,
    )

    session_jti = None
    tfa_verified = False
    tfa_method = None
    try:
        token_payload = verify_token(token)
        session_jti = token_payload.get("jti")
        tfa_verified = bool(token_payload.get("tfaVerified") or False)
        tfa_method = token_payload.get("tfaMethod")
    except Exception:
        pass

    tokens = await workspace_service.switch_workspace(
        user=current_user,
        tenant_id=tenant.id,
        team_id=None,
        session_jti=session_jti,
        tfa_verified=tfa_verified,
        tfa_method=tfa_method,
    )

    return _switch_response(
        tokens=tokens,
        tenant=tenant,
        membership=membership,
        team_id=None,
    )


@router.post("/switch", response_model=SwitchTenantResponse)
async def switch_tenant(
    payload: SwitchTenantRequest,
    current_user: CurrentUser,
    token: Annotated[str, Depends(get_current_token)],
    workspace_service: Annotated[TenantWorkspaceService, Depends(get_tenant_workspace_service)],
    repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
) -> SwitchTenantResponse:
    session_jti = None
    tfa_verified = False
    tfa_method = None
    try:
        token_payload = verify_token(token)
        session_jti = token_payload.get("jti")
        tfa_verified = bool(token_payload.get("tfaVerified") or False)
        tfa_method = token_payload.get("tfaMethod")
    except Exception:
        pass

    tokens = await workspace_service.switch_workspace(
        user=current_user,
        tenant_id=payload.tenantId,
        team_id=payload.teamId,
        session_jti=session_jti,
        tfa_verified=tfa_verified,
        tfa_method=tfa_method,
    )

    tenant = await repo.get_tenant(payload.tenantId)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    membership = await repo.get_membership(payload.tenantId, current_user.id)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a tenant member")

    return _switch_response(
        tokens=tokens,
        tenant=tenant,
        membership=membership,
        team_id=payload.teamId,
    )
