"""Router for AI models endpoints."""

from fastapi import APIRouter

from app.modules.ai.dependencies import AdminUser
from app.modules.ai.schemas import AiModel, AiModelsResponse
from app.modules.ai.utils.models_config import MODELS
from app.modules.auth.dependencies import CurrentUser

router = APIRouter(prefix="/models", tags=["ai-models"])


@router.get("", response_model=AiModelsResponse)
async def get_models(current_user: CurrentUser) -> AiModelsResponse:
    """Get list of available AI models.

    Available to all authenticated users - allows users to see available models
    when configuring their AI settings.

    Returns:
        List of configured models
    """
    models = [
        AiModel(
            id=model["id"],
            name=model["name"],
            provider=model["provider"],
            description=model.get("description"),
            context_length=model["context_length"],
            cost_per_1m_input=model["cost_per_1m_input"],
            cost_per_1m_output=model["cost_per_1m_output"],
            recommended=model.get("recommended", False),
        )
        for model in MODELS
    ]

    return AiModelsResponse(models=models)
