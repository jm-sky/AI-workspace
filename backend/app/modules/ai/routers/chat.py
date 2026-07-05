"""Router for AI chat endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ai.cache.postgres_cache import PostgresCacheService
from app.modules.ai.dependencies import AdminUser
from app.modules.ai.repositories import HistoryRepository, SettingsRepository
from app.modules.ai.schemas import AiChatRequest, AiChatResponse
from app.modules.ai.services import ChatService, SettingsService

router = APIRouter(prefix="/chat", tags=["ai-chat"])


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Get chat service dependency.

    Args:
        db: Database session

    Returns:
        Chat service instance
    """
    settings_repo = SettingsRepository(db)
    settings_service = SettingsService(settings_repo)

    history_repo = HistoryRepository(db)

    cache_service = PostgresCacheService(db)

    return ChatService(
        settings_service=settings_service,
        history_repo=history_repo,
        cache_service=cache_service,
    )


@router.post("", response_model=AiChatResponse)
async def chat(
    request: AiChatRequest,
    current_user: AdminUser,
    service: ChatService = Depends(get_chat_service),
) -> AiChatResponse:
    """Send message to AI and get response.

    Requires admin access.

    This endpoint:
    - Uses user's settings (model, temperature, etc.)
    - Supports user's own API token if configured
    - Caches responses to reduce costs
    - Tracks usage in history
    - Parses structured output from AI

    Args:
        request: Chat request with message and context

    Returns:
        AI response with tokens and cost
    """
    return await service.chat(current_user.id, request)
