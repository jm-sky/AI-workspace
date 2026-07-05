"""Router for AI settings endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ai.dependencies import AdminUser
from app.modules.ai.repositories import SettingsRepository
from app.modules.ai.schemas import (
    AiSetTokenRequest,
    AiSetTokenResponse,
    AiSettings,
    AiUpdateSettings,
)
from app.modules.ai.services import SettingsService
from app.modules.auth.dependencies import CurrentUser

router = APIRouter(prefix="/settings", tags=["ai-settings"])


def get_settings_service(db: AsyncSession = Depends(get_db)) -> SettingsService:
    """Get settings service dependency.

    Args:
        db: Database session

    Returns:
        Settings service instance
    """
    repo = SettingsRepository(db)
    return SettingsService(repo)


@router.get("", response_model=AiSettings)
async def get_settings(
    current_user: CurrentUser,
    service: SettingsService = Depends(get_settings_service),
) -> AiSettings:
    """Get AI settings for current user.

    Available to all authenticated users - allows users to view and configure
    their AI settings, including setting up their own OpenRouter token.

    Returns:
        User's AI settings
    """
    return await service.get_settings(current_user.id)


@router.put("", response_model=AiSettings)
async def update_settings(
    updates: AiUpdateSettings,
    current_user: CurrentUser,
    service: SettingsService = Depends(get_settings_service),
) -> AiSettings:
    """Update AI settings.

    Available to all authenticated users - allows users to configure their
    AI preferences (model, temperature, etc.).

    Args:
        updates: Settings updates

    Returns:
        Updated settings
    """
    return await service.update_settings(current_user.id, updates)


@router.post("/token", response_model=AiSetTokenResponse)
async def set_api_token(
    request: AiSetTokenRequest,
    current_user: CurrentUser,
    service: SettingsService = Depends(get_settings_service),
) -> AiSetTokenResponse:
    """Set user's OpenRouter API token.

    Available to all authenticated users - allows regular users to configure
    their own OpenRouter token to access AI features.

    Args:
        request: Token request

    Returns:
        Success response
    """
    await service.set_api_token(current_user.id, request)
    return AiSetTokenResponse(success=True, message="API token set successfully")


@router.delete("/token")
async def remove_api_token(
    current_user: CurrentUser,
    service: SettingsService = Depends(get_settings_service),
) -> dict[str, str]:
    """Remove user's API token.

    Available to all authenticated users.

    Returns:
        Success message
    """
    await service.remove_api_token(current_user.id)
    return {"message": "API token removed successfully"}
