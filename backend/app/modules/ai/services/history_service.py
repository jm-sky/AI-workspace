"""Service for AI history management."""

from uuid import UUID

from app.modules.ai.db_models import AIHistoryDB
from app.modules.ai.repositories import HistoryRepository
from app.modules.ai.schemas import AiHistoryDetail, AiHistoryItem, AiHistoryListResponse
from app.modules.ai.utils.models_config import calculate_cost, get_model_by_id


class HistoryService:
    """Service for AI history operations."""

    def __init__(self, repo: HistoryRepository):
        """Initialize service.

        Args:
            repo: History repository
        """
        self.repo = repo

    async def create_entry(
        self,
        user_id: str,
        operation_type: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost_usd: float | None,
        input_data: dict,
        output_data: dict,
        metadata: dict | None = None,
        container_ids: list[str] | None = None,
    ) -> AIHistoryDB:
        """Create new history entry.

        Args:
            user_id: User ID
            operation_type: Operation type
            model: Model used
            prompt_tokens: Prompt tokens
            completion_tokens: Completion tokens
            total_tokens: Total tokens
            cost_usd: Cost in USD
            input_data: Input data
            output_data: Output data
            metadata: Optional metadata
            container_ids: Optional list of container IDs

        Returns:
            Created history entry
        """
        return await self.repo.create(
            user_id=user_id,
            operation_type=operation_type,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata,
            container_ids=container_ids,
        )

    async def get_history_list(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        operation_type: str | None = None,
    ) -> AiHistoryListResponse:
        """Get paginated history list.

        Args:
            user_id: User ID
            limit: Maximum entries
            offset: Pagination offset
            operation_type: Optional filter

        Returns:
            History list response
        """
        entries, total = await self.repo.list_by_user(
            user_id=user_id, limit=limit, offset=offset, operation_type=operation_type
        )

        items = [self._to_list_item(entry) for entry in entries]

        return AiHistoryListResponse(
            items=items, total=total, limit=limit, offset=offset
        )

    async def get_history_detail(
        self, history_id: UUID, user_id: str
    ) -> AiHistoryDetail | None:
        """Get history entry detail.

        Args:
            history_id: History ID
            user_id: User ID

        Returns:
            History detail or None
        """
        entry = await self.repo.get_by_id(history_id, user_id)
        if not entry:
            return None

        return self._to_detail(entry)

    async def delete_entry(self, history_id: UUID, user_id: str) -> bool:
        """Delete history entry.

        Args:
            history_id: History ID
            user_id: User ID

        Returns:
            True if deleted
        """
        return await self.repo.delete_by_id(history_id, user_id)

    async def clear_all(self, user_id: str) -> int:
        """Clear all history for user.

        Args:
            user_id: User ID

        Returns:
            Number of deleted entries
        """
        return await self.repo.delete_all_by_user(user_id)

    def _to_list_item(self, entry: AIHistoryDB) -> AiHistoryItem:
        """Convert DB model to list item schema.

        Args:
            entry: History entry

        Returns:
            History list item
        """
        # Extract final_prompt from input_data
        # Support both old format (final_prompt) and new format (message)
        input_data = entry.input_data or {}
        final_prompt = input_data.get("message") or input_data.get("final_prompt") or ""

        # Extract context_data
        context_data = input_data.get("context") or input_data.get("context_data")

        # Extract response_data
        response_data = entry.output_data or {}

        # Extract metadata
        metadata = entry.metadata_ or {}
        provider = metadata.get("provider") or (
            entry.model.split("/")[0] if "/" in entry.model else "unknown"
        )
        duration_ms = metadata.get("duration_ms")
        used_own_token = metadata.get("used_own_token", False)

        # Build tokens object
        tokens = {
            "input": entry.prompt_tokens,
            "output": entry.completion_tokens,
            "total": entry.total_tokens,
        }

        # Build cost object
        # Calculate input/output costs if we have model info, otherwise use total cost
        cost_input = 0.0
        cost_output = 0.0
        if entry.cost_usd is not None:
            model_config = get_model_by_id(entry.model)
            if model_config:
                # Calculate costs based on token counts
                cost_input = (entry.prompt_tokens / 1_000_000) * model_config[
                    "cost_per_1m_input"
                ]
                cost_output = (entry.completion_tokens / 1_000_000) * model_config[
                    "cost_per_1m_output"
                ]
            else:
                # Fallback: split total cost proportionally
                if entry.total_tokens > 0:
                    cost_input = entry.cost_usd * (
                        entry.prompt_tokens / entry.total_tokens
                    )
                    cost_output = entry.cost_usd * (
                        entry.completion_tokens / entry.total_tokens
                    )

        cost = {
            "input": float(round(cost_input, 6)),
            "output": float(round(cost_output, 6)),
            "total": float(entry.cost_usd) if entry.cost_usd is not None else 0.0,
        }

        return AiHistoryItem(
            id=entry.id,
            operation_type=entry.operation_type,
            final_prompt=final_prompt,
            context_data=context_data,
            response_data=response_data,
            model=entry.model,
            provider=provider,
            tokens=tokens,
            cost=cost,
            duration_ms=duration_ms,
            used_own_token=used_own_token,
            container_ids=entry.container_ids,
            created_at=entry.created_at,
        )

    def _to_detail(self, entry: AIHistoryDB) -> AiHistoryDetail:
        """Convert DB model to detail schema.

        Args:
            entry: History entry

        Returns:
            History detail
        """
        return AiHistoryDetail(
            id=entry.id,
            user_id=entry.user_id,
            operation_type=entry.operation_type,
            model=entry.model,
            prompt_tokens=entry.prompt_tokens,
            completion_tokens=entry.completion_tokens,
            total_tokens=entry.total_tokens,
            cost_usd=entry.cost_usd,
            input_data=entry.input_data,
            output_data=entry.output_data,
            metadata=entry.metadata_,
            container_ids=entry.container_ids,
            created_at=entry.created_at,
        )
