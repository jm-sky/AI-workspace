"""Abstract base class for AI providers."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str  # 'system', 'user', 'assistant'
    content: str


class ChatResponse(BaseModel):
    """Chat response model."""

    message: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    finish_reason: str | None = None
    raw_response: dict[str, Any] | None = None


class AIProvider(ABC):
    """Abstract base class for AI providers.

    All AI providers must implement these methods.
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int | None = None,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat completion request.

        Args:
            messages: List of chat messages
            model: Model identifier
            max_tokens: Maximum tokens to generate (optional)
            temperature: Sampling temperature (0-2)
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatResponse with message and token usage

        Raises:
            OpenRouterError: If API request fails
        """
        pass

    @abstractmethod
    async def validate_token(self, api_token: str) -> bool:
        """Validate an API token.

        Args:
            api_token: API token to validate

        Returns:
            True if token is valid

        Raises:
            TokenValidationError: If token is invalid
        """
        pass
