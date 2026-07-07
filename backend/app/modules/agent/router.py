"""Agent module API router."""

from fastapi import APIRouter

from app.modules.agent.routers import chat_router, runs_router

router = APIRouter(prefix="/agent", tags=["agent"])

router.include_router(chat_router)
router.include_router(runs_router)
