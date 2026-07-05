"""Service for AI chat operations."""

import json
import re

from app.core.config import settings
from app.modules.ai.cache.postgres_cache import PostgresCacheService
from app.modules.ai.providers.openrouter import OpenRouterProvider
from app.modules.ai.repositories import HistoryRepository
from app.modules.ai.schemas import AiChatRequest, AiChatResponse, StructuredOutput
from app.modules.ai.services.settings_service import SettingsService
from app.modules.ai.utils.models_config import calculate_cost


class ChatService:
    """Service for AI chat operations."""

    def __init__(
        self,
        settings_service: SettingsService,
        history_repo: HistoryRepository,
        cache_service: PostgresCacheService | None = None,
    ):
        """Initialize service.

        Args:
            settings_service: Settings service
            history_repo: History repository
            cache_service: Optional cache service
        """
        self.settings_service = settings_service
        self.history_repo = history_repo
        self.cache_service = cache_service

    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        """Process chat request.

        Args:
            user_id: User ID
            request: Chat request

        Returns:
            Chat response
        """
        # Get user settings
        user_settings = await self.settings_service.get_settings(user_id)

        # Determine which model and token to use
        model = request.model or user_settings.selected_model
        max_tokens = request.max_tokens or user_settings.max_tokens
        temperature = (
            request.temperature
            if request.temperature != 1.0
            else user_settings.temperature
        )

        # Get API token (user's or system)
        api_token = None
        if user_settings.use_own_token:
            api_token = await self.settings_service.get_api_token(user_id)

        # Build messages (needed for cache key and debug)
        messages = self._build_messages(
            request.message, request.history, request.context
        )
        full_prompt = "\n\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in messages]
        )

        # Check cache if enabled
        if settings.ai.cache_enabled and self.cache_service:
            cache_key = PostgresCacheService.generate_cache_key(
                operation_type="chat",
                input_data={
                    "message": request.message,
                    "context": request.context,
                    "model": model,
                },
                model=model,
            )

            cached = await self.cache_service.get(cache_key)
            if cached:
                # Return cached response
                return AiChatResponse(
                    message=cached["message"],
                    structured_output=(
                        StructuredOutput(**cached["structured_output"])
                        if cached.get("structured_output")
                        else None
                    ),
                    tokens=cached["tokens"],
                    cost=cached.get("cost"),
                    model=cached["model"],
                    prompt=full_prompt,
                )

        # Initialize provider
        provider = OpenRouterProvider(api_key=api_token)

        # Call AI
        response = await provider.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Parse structured output if present
        structured = self._parse_structured_output(response.message)

        # Clean message (remove JSON blocks)
        cleaned_message = self._clean_message(response.message)

        # Calculate cost
        cost = calculate_cost(model, response.prompt_tokens, response.completion_tokens)

        # Extract container_ids from context keys (context is a dict where keys are container IDs)
        container_ids: list[str] | None = None
        if request.context and isinstance(request.context, dict):
            container_ids = [str(key) for key in request.context.keys() if key]
            if not container_ids:
                container_ids = None

        # Extract provider name from model (e.g., "openai/gpt-4o-mini" -> "openai")
        provider_name = model.split("/")[0] if "/" in model else "unknown"

        # Save to history with metadata
        await self.history_repo.create(
            user_id=user_id,
            operation_type="chat",
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            cost_usd=cost,
            input_data={"message": request.message, "context": request.context},
            output_data={
                "message": cleaned_message,
                "structured_output": structured.model_dump() if structured else None,
            },
            metadata={
                "provider": provider_name,
                "used_own_token": user_settings.use_own_token,
            },
            container_ids=container_ids,
        )

        # Cache result if enabled
        if settings.ai.cache_enabled and self.cache_service:
            cache_data = {
                "operation_type": "chat",
                "model": response.model,
                "message": cleaned_message,
                "structured_output": structured.model_dump() if structured else None,
                "tokens": {
                    "prompt": response.prompt_tokens,
                    "completion": response.completion_tokens,
                    "total": response.total_tokens,
                },
                "cost": cost,
            }
            await self.cache_service.set(
                cache_key, cache_data, ttl_days=settings.ai.cache_ttl_classify
            )

        return AiChatResponse(
            message=cleaned_message,
            structured_output=structured,
            tokens={
                "prompt": response.prompt_tokens,
                "completion": response.completion_tokens,
                "total": response.total_tokens,
            },
            cost=cost,
            model=response.model,
            prompt=full_prompt,
        )

    def _build_messages(
        self, user_message: str, history: list, context: dict
    ) -> list[dict[str, str]]:
        """Build messages array for AI.

        Args:
            user_message: User's message
            history: Previous messages in conversation
            context: Context data

        Returns:
            List of messages
        """
        messages = []

        # System message with instructions
        system_prompt = f"""You are a helpful AI assistant for a gear management application {settings.app.name}.
You help users manage their survival gear, bug-out bags, and equipment.

When the user asks you to perform actions (like adding items, updating quantities, etc.),
respond in a conversational way AND include structured output in JSON format at the end of your message.

Format your structured output as:
```json
{{
  "action": "action_name",
  "data": {{...}}
}}
```

Available actions:
- create_item: Create a new gear item
- update_item: Update existing item
- delete_item: Delete an item
- create_container: Create a new container
- None: Just conversation, no action needed

Keep your responses concise and helpful."""

        messages.append({"role": "system", "content": system_prompt})

        # Add context if provided
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}"
            messages.append({"role": "system", "content": context_str})

        # Add conversation history
        for hist_msg in history:
            messages.append({"role": hist_msg.role, "content": hist_msg.content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _parse_structured_output(self, message: str) -> StructuredOutput | None:
        """Parse structured output from AI response.

        Args:
            message: AI message

        Returns:
            Structured output or None
        """
        # Look for JSON code blocks
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, message, re.DOTALL)

        if not match:
            return None

        try:
            data = json.loads(match.group(1))
            return StructuredOutput(
                action=data.get("action"), data=data.get("data", {})
            )
        except (json.JSONDecodeError, ValueError):
            return None

    def _clean_message(self, message: str) -> str:
        """Remove structured output JSON from message.

        Args:
            message: AI message with potential JSON code blocks

        Returns:
            Cleaned message without JSON blocks
        """
        # Remove JSON code blocks (both with and without 'json' language identifier)
        # Match ```json...``` or ```{...}```
        patterns = [
            r"```json\s*\{[^`]*?\}\s*```",  # ```json { ... } ```
            r"```\s*\{[^`]*?\}\s*```",  # ``` { ... } ```
        ]

        cleaned = message
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL)

        # Clean up extra whitespace
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)  # Max 2 newlines
        cleaned = cleaned.strip()

        return cleaned
