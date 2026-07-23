"""FastAPI router for gear settings endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser

from .repository import GearSettingsRepository
from .schemas import GearSettingsResponse, GearSettingsUpdate
from .service import GearSettingsService

router = APIRouter(prefix="/gear-settings", tags=["Gear Settings"])


def get_gear_settings_repository(
    db: AsyncSession = Depends(get_db),
) -> GearSettingsRepository:
    """Dependency to get gear settings repository instance.

    Args:
        db: Database session

    Returns:
        Gear settings repository instance
    """
    return GearSettingsRepository(db)


def get_gear_settings_service(
    repository: Annotated[GearSettingsRepository, Depends(get_gear_settings_repository)],
) -> GearSettingsService:
    """Dependency to get gear settings service instance.

    Args:
        repository: Gear settings repository

    Returns:
        Gear settings service instance
    """
    return GearSettingsService(repository)


@router.get("", response_model=GearSettingsResponse)
async def get_my_gear_settings(
    *,
    current_user: CurrentUser,
    service: Annotated[GearSettingsService, Depends(get_gear_settings_service)],
) -> GearSettingsResponse:
    """Get gear settings for the authenticated user.

    Args:
        current_user: Authenticated user
        service: Gear settings service

    Returns:
        Gear settings response
    """
    return await service.get_settings(current_user.id)


@router.patch("", response_model=GearSettingsResponse)
async def update_my_gear_settings(
    *,
    payload: GearSettingsUpdate,
    current_user: CurrentUser,
    service: Annotated[GearSettingsService, Depends(get_gear_settings_service)],
) -> GearSettingsResponse:
    """Update gear settings for the authenticated user.

    Args:
        payload: Settings updates
        current_user: Authenticated user
        service: Gear settings service

    Returns:
        Updated gear settings response
    """
    return await service.update_settings(current_user.id, payload)
