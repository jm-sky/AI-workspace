"""API router for per-user integration OAuth tokens."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.integrations.exceptions import IntegrationEncryptionError
from app.modules.integrations.repositories import (
    IntegrationTokenRepository,
    get_integration_token_repository,
)
from app.modules.integrations.schemas import (
    IntegrationConnectionResponse,
    IntegrationConnectionsListResponse,
    IntegrationTokenStoreRequest,
)
from app.modules.integrations.service import IntegrationTokenService

router = APIRouter(prefix="/integrations/oauth", tags=["Integrations"])


def _get_service(
    repo: Annotated[IntegrationTokenRepository, Depends(get_integration_token_repository)],
) -> IntegrationTokenService:
    return IntegrationTokenService(repo)


@router.get("/connections", response_model=IntegrationConnectionsListResponse)
async def list_connections(
    current_user: CurrentUser,
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
) -> IntegrationConnectionsListResponse:
    items = await service.list_connections(current_user.id)
    return IntegrationConnectionsListResponse(
        connections=[IntegrationConnectionResponse(**item) for item in items]
    )


@router.put("/tokens", status_code=status.HTTP_204_NO_CONTENT)
async def store_tokens(
    payload: IntegrationTokenStoreRequest,
    current_user: CurrentUser,
    service: Annotated[IntegrationTokenService, Depends(_get_service)],
) -> None:
    try:
        await service.store_tokens(
            user_id=current_user.id,
            provider=payload.provider,
            access_token=payload.accessToken,
            refresh_token=payload.refreshToken,
            expires_at=payload.expiresAt,
            scopes=payload.scopes,
            provider_metadata=payload.providerMetadata,
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
