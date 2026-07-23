"""Router for AI history endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ai.dependencies import AdminUser
from app.modules.ai.repositories import HistoryRepository
from app.modules.ai.schemas import AiHistoryDetail, AiHistoryListResponse
from app.modules.ai.services import HistoryService

router = APIRouter(prefix="/history", tags=["ai-history"])


def get_history_service(db: AsyncSession = Depends(get_db)) -> HistoryService:
    """Get history service dependency.

    Args:
        db: Database session

    Returns:
        History service instance
    """
    repo = HistoryRepository(db)
    return HistoryService(repo)


@router.get("", response_model=AiHistoryListResponse)
async def get_history(
    current_user: AdminUser,
    service: HistoryService = Depends(get_history_service),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    operation_type: str | None = Query(None),
) -> AiHistoryListResponse:
    """Get AI history list for current user.

    Requires admin access.

    Args:
        limit: Maximum number of items
        offset: Pagination offset
        operation_type: Optional filter by operation type

    Returns:
        Paginated history list
    """
    return await service.get_history_list(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        operation_type=operation_type,
    )


@router.get("/{history_id}", response_model=AiHistoryDetail)
async def get_history_detail(
    history_id: UUID,
    current_user: AdminUser,
    service: HistoryService = Depends(get_history_service),
) -> AiHistoryDetail:
    """Get AI history entry detail.

    Requires admin access.

    Args:
        history_id: History entry ID

    Returns:
        History entry detail

    Raises:
        HTTPException: 404 if not found
    """
    detail = await service.get_history_detail(history_id, current_user.id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found")
    return detail


@router.delete("/{history_id}")
async def delete_history_entry(
    history_id: UUID,
    current_user: AdminUser,
    service: HistoryService = Depends(get_history_service),
) -> dict[str, str]:
    """Delete AI history entry.

    Requires admin access.

    Args:
        history_id: History entry ID

    Returns:
        Success message

    Raises:
        HTTPException: 404 if not found
    """
    deleted = await service.delete_entry(history_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found")
    return {"message": "History entry deleted successfully"}


@router.delete("")
async def clear_history(
    current_user: AdminUser,
    service: HistoryService = Depends(get_history_service),
) -> dict[str, str]:
    """Clear all AI history for current user.

    Requires admin access.

    Returns:
        Success message with count
    """
    count = await service.clear_all(current_user.id)
    return {"message": f"Cleared {count} history entries"}
