"""SSE chat endpoint for workspace agent."""

import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.agent.exceptions import (
    AgentError,
    AgentNotConfiguredError,
    AgentToolsDisabledError,
)
from app.modules.agent.dependencies import AgentTenantContext
from app.modules.agent.schemas import AgentChatRequest
from app.modules.agent.services.agent_run_service import AgentRunService
from app.modules.auth.dependencies import CurrentUser
from app.modules.integrations.repositories import (
    IntegrationTokenRepository,
    get_integration_token_repository,
)
from app.modules.integrations.service import IntegrationTokenService

router = APIRouter(prefix="/chat", tags=["agent-chat"])


def _get_agent_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    token_repo: Annotated[
        IntegrationTokenRepository, Depends(get_integration_token_repository)
    ],
) -> AgentRunService:
    return AgentRunService(db, IntegrationTokenService(token_repo))


@router.post("/stream")
async def agent_chat_stream(
    request: AgentChatRequest,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[AgentRunService, Depends(_get_agent_service)],
) -> StreamingResponse:
    """Stream agent execution via Server-Sent Events."""
    if not settings.ai.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are disabled",
        )
    if not settings.ai.openrouter_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENROUTER_API_KEY is not configured",
        )

    async def event_generator() -> AsyncIterator[str]:
        try:
            async for event in service.run_stream(
                tenant_ctx=tenant_ctx,
                message=request.message,
                agent_key=request.agentKey,
                model=request.model,
            ):
                payload = json.dumps(event.data, default=str)
                yield f"event: {event.event}\ndata: {payload}\n\n"
        except (AgentNotConfiguredError, AgentToolsDisabledError) as exc:
            payload = json.dumps({"message": str(exc)})
            yield f"event: error\ndata: {payload}\n\n"
        except AgentError as exc:
            payload = json.dumps({"message": str(exc)})
            yield f"event: error\ndata: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
