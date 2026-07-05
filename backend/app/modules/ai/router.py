"""Main AI module router."""

from fastapi import APIRouter

from app.modules.ai.routers import (
    chat_router,
    history_router,
    models_router,
    settings_router,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health", dependencies=[])
async def health_check() -> dict[str, str]:
    """Health check endpoint for AI module.

    Returns:
        Status message
    """
    return {"status": "ok", "module": "ai"}


@router.get("/status")
async def get_ai_status() -> dict[str, bool]:
    """Get AI module status.

    Requires admin access.

    Returns:
        Dict with AI module status
    """
    from app.core.config import settings

    return {"enabled": settings.ai.enabled, "cache_enabled": settings.ai.cache_enabled}


# Register sub-routers
router.include_router(chat_router)
router.include_router(models_router)
router.include_router(settings_router)
router.include_router(history_router)
