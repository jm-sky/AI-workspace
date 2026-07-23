"""Repository for AI history."""

from uuid import UUID

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.db_models import AIHistoryDB


class HistoryRepository:
    """Repository for AI history operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository.

        Args:
            db: Database session
        """
        self.db = db

    async def create(
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
            prompt_tokens: Prompt tokens count
            completion_tokens: Completion tokens count
            total_tokens: Total tokens count
            cost_usd: Cost in USD
            input_data: Input data
            output_data: Output data
            metadata: Optional metadata
            container_ids: Optional list of container IDs

        Returns:
            Created history entry
        """
        history = AIHistoryDB(
            user_id=user_id,
            operation_type=operation_type,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            input_data=input_data,
            output_data=output_data,
            metadata_=metadata,
            container_ids=container_ids,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_by_id(self, history_id: UUID, user_id: str) -> AIHistoryDB | None:
        """Get history entry by ID.

        Args:
            history_id: History ID
            user_id: User ID (for security)

        Returns:
            History entry or None
        """
        result = await self.db.execute(select(AIHistoryDB).where(AIHistoryDB.id == history_id, AIHistoryDB.user_id == user_id))
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        operation_type: str | None = None,
    ) -> tuple[list[AIHistoryDB], int]:
        """List history entries for user.

        Args:
            user_id: User ID
            limit: Maximum number of entries
            offset: Offset for pagination
            operation_type: Optional filter by operation type

        Returns:
            Tuple of (entries, total_count)
        """
        # Build query
        query = select(AIHistoryDB).where(AIHistoryDB.user_id == user_id)

        if operation_type:
            query = query.where(AIHistoryDB.operation_type == operation_type)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(desc(AIHistoryDB.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        entries = list(result.scalars().all())

        return entries, total

    async def delete_by_id(self, history_id: UUID, user_id: str) -> bool:
        """Delete history entry by ID.

        Args:
            history_id: History ID
            user_id: User ID (for security)

        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(delete(AIHistoryDB).where(AIHistoryDB.id == history_id, AIHistoryDB.user_id == user_id))
        await self.db.commit()
        return (result.rowcount or 0) > 0  # type: ignore[attr-defined]

    async def delete_all_by_user(self, user_id: str) -> int:
        """Delete all history entries for user.

        Args:
            user_id: User ID

        Returns:
            Number of deleted entries
        """
        result = await self.db.execute(delete(AIHistoryDB).where(AIHistoryDB.user_id == user_id))
        await self.db.commit()
        return result.rowcount or 0  # type: ignore[attr-defined]
