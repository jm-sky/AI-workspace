"""API router for workspace configuration."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.tenants.dependencies import CurrentTenantContext
from app.modules.workspace_config.repositories import (
    WorkspaceConfigRepository,
    get_workspace_config_repository,
)
from app.modules.workspace_config.resolver import WorkspaceConfigResolver
from app.modules.workspace_config.types import (
    ConfigEntryRequest,
    ConfigEntryResponse,
    ConfigKey,
    ConfigScope,
    EffectiveWorkspaceConfig,
)

router = APIRouter(prefix="/workspace/config", tags=["Workspace Config"])


@router.get("/effective", response_model=EffectiveWorkspaceConfig)
async def get_effective_config(
    tenant_ctx: CurrentTenantContext,
    repo: Annotated[WorkspaceConfigRepository, Depends(get_workspace_config_repository)],
) -> EffectiveWorkspaceConfig:
    resolver = WorkspaceConfigResolver(repo)
    return await resolver.resolve(
        user_id=tenant_ctx.user_id,
        tenant_id=tenant_ctx.tenant_id,
        team_id=tenant_ctx.team_id,
    )


@router.put("/tenant/{config_key}", response_model=ConfigEntryResponse)
async def set_tenant_config(
    config_key: str,
    payload: ConfigEntryRequest,
    tenant_ctx: CurrentTenantContext,
    repo: Annotated[WorkspaceConfigRepository, Depends(get_workspace_config_repository)],
) -> ConfigEntryResponse:
    if tenant_ctx.tenant_role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant owner or admin can set tenant config",
        )
    if payload.key.value != config_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Config key in path must match request body",
        )

    entry = await repo.upsert_entry(
        scope=ConfigScope.TENANT,
        scope_id=tenant_ctx.tenant_id,
        tenant_id=None,
        config_key=config_key,
        config_value=_normalize_value(payload.value),
    )
    return _to_response(entry)


@router.put("/user/{config_key}", response_model=ConfigEntryResponse)
async def set_user_config(
    config_key: str,
    payload: ConfigEntryRequest,
    tenant_ctx: CurrentTenantContext,
    repo: Annotated[WorkspaceConfigRepository, Depends(get_workspace_config_repository)],
) -> ConfigEntryResponse:
    if payload.key.value != config_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Config key in path must match request body",
        )

    entry = await repo.upsert_entry(
        scope=ConfigScope.USER,
        scope_id=tenant_ctx.user_id,
        tenant_id=tenant_ctx.tenant_id,
        config_key=config_key,
        config_value=_normalize_value(payload.value),
    )
    return _to_response(entry)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
        return value
    return str(value)


def _to_response(entry) -> ConfigEntryResponse:
    return ConfigEntryResponse(
        scope=ConfigScope(entry.scope),
        scopeId=entry.scope_id,
        tenantId=entry.tenant_id,
        key=ConfigKey(entry.config_key),
        value=entry.config_value,
    )
