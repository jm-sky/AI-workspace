"""Service for AI settings management."""

from app.modules.ai.db_models import AIUserSettingsDB
from app.modules.ai.repositories import SettingsRepository
from app.modules.ai.schemas import AiSettings, AiSetTokenRequest, AiUpdateSettings
from app.modules.ai.utils.encryption import decrypt_token, encrypt_token


class SettingsService:
    """Service for AI settings operations."""

    def __init__(self, repo: SettingsRepository):
        """Initialize service.

        Args:
            repo: Settings repository
        """
        self.repo = repo

    async def get_settings(self, user_id: str) -> AiSettings:
        """Get user settings.

        Creates default settings if none exist.

        Args:
            user_id: User ID

        Returns:
            User settings
        """
        settings = await self.repo.get_or_create(user_id)
        return self._to_schema(settings)

    async def update_settings(self, user_id: str, updates: AiUpdateSettings) -> AiSettings:
        """Update user settings.

        Args:
            user_id: User ID
            updates: Settings updates

        Returns:
            Updated settings
        """
        settings = await self.repo.get_or_create(user_id)

        # Use by_alias=False to get snake_case field names for database columns
        update_dict = updates.model_dump(exclude_none=True, by_alias=False)
        settings = await self.repo.update(settings, **update_dict)

        return self._to_schema(settings)

    async def set_api_token(self, user_id: str, request: AiSetTokenRequest) -> None:
        """Set user's API token.

        Args:
            user_id: User ID
            request: Token request
        """
        settings = await self.repo.get_or_create(user_id)

        encrypted = encrypt_token(request.api_token)

        await self.repo.update(settings, use_own_token=True, encrypted_api_token=encrypted)

    async def remove_api_token(self, user_id: str) -> None:
        """Remove user's API token.

        Args:
            user_id: User ID
        """
        settings = await self.repo.get_or_create(user_id)
        await self.repo.update(settings, use_own_token=False, encrypted_api_token=None)

    async def get_api_token(self, user_id: str) -> str | None:
        """Get decrypted API token for user.

        Args:
            user_id: User ID

        Returns:
            Decrypted token or None
        """
        settings = await self.repo.get_by_user_id(user_id)

        if not settings or not settings.use_own_token or not settings.encrypted_api_token:
            return None

        return decrypt_token(settings.encrypted_api_token)

    def _to_schema(self, settings: AIUserSettingsDB) -> AiSettings:
        """Convert DB model to schema.

        Args:
            settings: DB settings

        Returns:
            Settings schema
        """
        # Use model_validate with dict to handle aliases automatically
        return AiSettings.model_validate(
            {
                "id": settings.id,
                "userId": settings.user_id,
                "useOwnToken": settings.use_own_token,
                "hasToken": bool(settings.encrypted_api_token),
                "selectedModel": settings.selected_model,
                "contextFields": settings.context_fields,
                "maxTokens": settings.max_tokens,
                "temperature": settings.temperature,
                "monthlyTokenLimit": settings.monthly_token_limit,
                "monthlyTokensUsed": settings.monthly_tokens_used,
                "monthlyCostLimit": settings.monthly_cost_limit,
                "monthlyCostUsed": settings.monthly_cost_used,
                "createdAt": settings.created_at,
                "updatedAt": settings.updated_at,
            }
        )
