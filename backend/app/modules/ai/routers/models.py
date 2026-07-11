"""Router for AI models endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.core.redis import get_redis
from app.modules.ai.schemas import AiModel, AiModelsResponse
from app.modules.ai.services.model_catalog_service import get_catalog
from app.modules.auth.dependencies import CurrentUser

router = APIRouter(prefix="/models", tags=["ai-models"])


@router.get("", response_model=AiModelsResponse)
async def get_models(
    current_user: CurrentUser,
    redis: Annotated[Redis, Depends(get_redis)],
) -> AiModelsResponse:
    """Get list of available AI models.

    Serves the live OpenRouter catalog (Redis-cached), falling back to the
    curated list when OpenRouter is unreachable. The full catalog is returned
    unfiltered; the workspace allow-list and all search/sort/filter work happen
    client-side.

    Available to all authenticated users - allows users to see available models
    when configuring their AI settings.

    Returns:
        List of available models
    """
    models = await get_catalog(redis)

    return AiModelsResponse(
        models=[
            AiModel(
                id=model["id"],
                name=model["name"],
                provider=model["provider"],
                description=model.get("description"),
                context_length=model["context_length"],
                cost_per_1m_input=model["cost_per_1m_input"],
                cost_per_1m_output=model["cost_per_1m_output"],
                tier=model.get("tier", "balanced"),
                supports_vision=model.get("supports_vision", False),
                supports_tools=model.get("supports_tools", True),
                supports_reasoning=model.get("supports_reasoning", False),
                recommended=model.get("recommended", False),
            )
            for model in models
        ]
    )
