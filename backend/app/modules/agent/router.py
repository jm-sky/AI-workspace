"""Agent module API router."""

from fastapi import APIRouter

from app.modules.agent.routers import (
    agents_router,
    attachments_router,
    chat_router,
    runs_router,
    sessions_router,
)

router = APIRouter(prefix="/agent", tags=["agent"])

router.include_router(agents_router)
router.include_router(chat_router)
router.include_router(runs_router)
router.include_router(sessions_router)
router.include_router(attachments_router)
