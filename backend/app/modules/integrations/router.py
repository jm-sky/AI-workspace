"""API router for per-user integration OAuth tokens."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.modules.auth.dependencies import CurrentUser
from app.modules.integrations.exceptions import (
    IntegrationEncryptionError,
    IntegrationOAuthStateError,
    IntegrationPermissionError,
)
from app.modules.integrations.oauth_state import (
    create_integration_oauth_state,
    verify_integration_oauth_state,
)
from app.modules.integrations.providers import integration_oauth_registry
from app.modules.integrations.repositories import (
    IntegrationTokenRepository,
    get_integration_token_repository,
)
from app.modules.integrations.schemas import (
    IntegrationAuthUrlRequest,
    IntegrationAuthUrlResponse,
    IntegrationConnectionResponse,
    IntegrationConnectionsListResponse,
    IntegrationConnectionUpdateRequest,
    IntegrationOAuthCallbackRequest,
    IntegrationProviderSetupResponse,
    IntegrationScopeOptionResponse,
    IntegrationSetupResponse,
    IntegrationTokenStoreRequest,
)
from app.modules.integrations.service import IntegrationTokenService
from app.modules.integrations.types import (
    INTEGRATION_PROVIDER_SCOPES,
    IntegrationProvider,
    IntegrationVisibilityScope,
)
from app.modules.teams.repositories import TeamRepository, get_team_repository
from app.modules.tenants.dependencies import CurrentTenantContext

router = APIRouter(prefix="/integrations/oauth", tags=["Integrations"])


def _get_service(
    repo: Annotated[IntegrationTokenRepository, Depends(get_integration_token_repository)],
) -> IntegrationTokenService:
    return IntegrationTokenService(repo)


def _provider_kind(provider_id: str) -> str:
    if provider_id == IntegrationProvider.GITHUB.value and settings.integrations.github_app_id:
        return "github_app"
    return "oauth_app"


@router.get("/setup", response_model=IntegrationSetupResponse)
async def get_integration_setup(
    tenant_ctx: CurrentTenantContext,
    team_repo: Annotated[TeamRepository, Depends(get_team_repository)],
) -> IntegrationSetupResponse:
    teams = await team_repo.list_for_user_in_tenant(
        user_id=tenant_ctx.user_id,
        tenant_id=tenant_ctx.tenant_id,
    )
    providers: list[IntegrationProviderSetupResponse] = []
    for provider_id in integration_oauth_registry.supported_providers():
        provider = integration_oauth_registry.get(provider_id)
        enabled = bool(getattr(provider, "is_configured", lambda: False)())
        providers.append(
            IntegrationProviderSetupResponse(
                id=provider_id,
                enabled=enabled,
                kind=_provider_kind(provider_id),
                scopes=[
                    IntegrationScopeOptionResponse(
                        id=str(scope["id"]),
                        labelKey=str(scope["labelKey"]),
                        descriptionKey=str(scope["descriptionKey"]),
                        required=bool(scope.get("required", False)),
                    )
                    for scope in INTEGRATION_PROVIDER_SCOPES.get(provider_id, [])
                ],
            )
        )
    return IntegrationSetupResponse(
        tenantId=tenant_ctx.tenant_id,
        tenantRole=tenant_ctx.tenant_role,
        canManageShared=tenant_ctx.tenant_role in ("owner", "admin"),
        teams=[{"id": team.id, "name": team.name} for team, _membership in teams],
        providers=providers,
    )


@router.get("/connections", response_model=IntegrationConnectionsListResponse)
async def list_connections(
    tenant_ctx: CurrentTenantContext,
    team_repo: Annotated[TeamRepository, Depends(get_team_repository)],
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
) -> IntegrationConnectionsListResponse:
    teams = await team_repo.list_for_user_in_tenant(
        user_id=tenant_ctx.user_id,
        tenant_id=tenant_ctx.tenant_id,
    )
    team_ids = [team.id for team, _membership in teams]
    team_names = {team.id: team.name for team, _membership in teams}

    items = await service.list_connections(
        user_id=tenant_ctx.user_id,
        tenant_id=tenant_ctx.tenant_id,
        team_ids=team_ids,
        tenant_role=tenant_ctx.tenant_role,
    )
    connections = []
    for item in items:
        if item.get("teamId"):
            item["teamName"] = team_names.get(item["teamId"])
        connections.append(IntegrationConnectionResponse(**item))
    return IntegrationConnectionsListResponse(connections=connections)


@router.post("/auth-url", response_model=IntegrationAuthUrlResponse)
async def get_auth_url(
    payload: IntegrationAuthUrlRequest,
    current_user: CurrentUser,
    tenant_ctx: CurrentTenantContext,
    team_repo: Annotated[TeamRepository, Depends(get_team_repository)],
) -> IntegrationAuthUrlResponse:
    try:
        IntegrationTokenService.assert_shared_visibility_allowed(
            visibility_scope=payload.visibilityScope.value,
            tenant_role=tenant_ctx.tenant_role,
            team_id=payload.teamId,
        )
    except IntegrationPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if payload.visibilityScope == IntegrationVisibilityScope.TEAM:
        if payload.teamId is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="teamId is required for team visibility",
            )
        membership = await team_repo.get_membership(payload.teamId, current_user.id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of selected team",
            )

    provider = integration_oauth_registry.get(payload.provider)
    state = create_integration_oauth_state(
        {
            "userId": current_user.id,
            "provider": payload.provider,
            "scopes": payload.scopes,
            "visibilityScope": payload.visibilityScope.value,
            "tenantId": tenant_ctx.tenant_id,
            "teamId": payload.teamId,
        }
    )
    auth_url = provider.get_authorization_url(state=state, scopes=payload.scopes)
    return IntegrationAuthUrlResponse(authUrl=auth_url, state=state)


@router.post("/callback/{provider}", response_model=IntegrationConnectionResponse)
async def oauth_callback(
    provider: str,
    payload: IntegrationOAuthCallbackRequest,
    current_user: CurrentUser,
    tenant_ctx: CurrentTenantContext,
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
) -> IntegrationConnectionResponse:
    try:
        state_data = verify_integration_oauth_state(payload.state)
    except IntegrationOAuthStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if state_data.get("userId") != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="State mismatch")
    if state_data.get("provider") != provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider mismatch")
    if state_data.get("tenantId") != tenant_ctx.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")

    visibility_scope = state_data.get("visibilityScope", IntegrationVisibilityScope.USER.value)
    team_id = state_data.get("teamId")
    scopes = state_data.get("scopes", [])

    try:
        IntegrationTokenService.assert_shared_visibility_allowed(
            visibility_scope=visibility_scope,
            tenant_role=tenant_ctx.tenant_role,
            team_id=team_id,
        )
        oauth_provider = integration_oauth_registry.get(provider)
        token_result = await oauth_provider.exchange_code_for_token(
            payload.code,
            scopes=scopes,
        )
        connection = await service.store_tokens(
            owner_user_id=current_user.id,
            provider=provider,
            visibility_scope=visibility_scope,
            tenant_id=(tenant_ctx.tenant_id if visibility_scope != IntegrationVisibilityScope.USER.value else None),
            team_id=(team_id if visibility_scope == IntegrationVisibilityScope.TEAM.value else None),
            access_token=token_result.access_token,
            refresh_token=token_result.refresh_token,
            expires_at=token_result.expires_at,
            scopes=token_result.scope,
            provider_metadata=token_result.provider_metadata,
        )
    except IntegrationPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IntegrationEncryptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    item = service._connection_dict(  # noqa: SLF001
        connection,
        user_id=current_user.id,
        can_manage_shared=tenant_ctx.tenant_role in ("owner", "admin"),
    )
    return IntegrationConnectionResponse(**item)


@router.patch("/connections/{connection_id}", response_model=IntegrationConnectionResponse)
async def update_connection(
    connection_id: str,
    payload: IntegrationConnectionUpdateRequest,
    current_user: CurrentUser,
    tenant_ctx: CurrentTenantContext,
    repo: Annotated[IntegrationTokenRepository, Depends(get_integration_token_repository)],
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
    team_repo: Annotated[TeamRepository, Depends(get_team_repository)],
) -> IntegrationConnectionResponse:
    connection = await repo.get_by_id(connection_id)
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    is_owner = connection.owner_user_id == current_user.id
    is_shared_admin = tenant_ctx.tenant_role in ("owner", "admin")
    if not is_owner and not is_shared_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    try:
        IntegrationTokenService.assert_shared_visibility_allowed(
            visibility_scope=payload.visibilityScope.value,
            tenant_role=tenant_ctx.tenant_role,
            team_id=payload.teamId,
        )
    except IntegrationPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if payload.visibilityScope == IntegrationVisibilityScope.TEAM:
        membership = await team_repo.get_membership(payload.teamId or "", current_user.id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of selected team",
            )

    connection.visibility_scope = payload.visibilityScope.value
    connection.tenant_id = tenant_ctx.tenant_id if payload.visibilityScope != IntegrationVisibilityScope.USER else None
    connection.team_id = payload.teamId if payload.visibilityScope == IntegrationVisibilityScope.TEAM else None
    await repo.db.commit()
    await repo.db.refresh(connection)

    item = service._connection_dict(  # noqa: SLF001
        connection,
        user_id=current_user.id,
        can_manage_shared=is_shared_admin,
    )
    return IntegrationConnectionResponse(**item)


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: str,
    current_user: CurrentUser,
    tenant_ctx: CurrentTenantContext,
    repo: Annotated[IntegrationTokenRepository, Depends(get_integration_token_repository)],
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
) -> None:
    connection = await repo.get_by_id(connection_id)
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    is_owner = connection.owner_user_id == current_user.id
    is_shared_admin = tenant_ctx.tenant_role in ("owner", "admin")
    shared = connection.visibility_scope in (
        IntegrationVisibilityScope.TEAM.value,
        IntegrationVisibilityScope.TENANT.value,
    )
    if not is_owner and not (shared and is_shared_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await service.delete_connection(connection_id)


@router.put("/tokens", status_code=status.HTTP_204_NO_CONTENT)
async def store_tokens(
    payload: IntegrationTokenStoreRequest,
    current_user: CurrentUser,
    tenant_ctx: CurrentTenantContext,
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
) -> None:
    """Manual token store (dev / Jira-GitLab) — personal scope only."""
    try:
        await service.store_tokens(
            owner_user_id=current_user.id,
            provider=payload.provider,
            access_token=payload.accessToken,
            refresh_token=payload.refreshToken,
            expires_at=payload.expiresAt,
            scopes=payload.scopes,
            provider_metadata=payload.providerMetadata,
            visibility_scope=IntegrationVisibilityScope.USER.value,
        )
    except IntegrationEncryptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.delete("/tokens/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tokens(
    provider: str,
    current_user: CurrentUser,
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
) -> None:
    await service.delete_tokens(current_user.id, provider)
