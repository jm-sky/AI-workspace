"""Router for feature limits endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import AdminOrOwnerUser
from app.modules.feature_limits.repository import FeatureLimitRepository
from app.modules.feature_limits.schemas import (
    FeatureLimitCreate,
    FeatureLimitResponse,
    FeatureLimitUpdate,
)
from app.modules.feature_limits.service import FeatureLimitService

router = APIRouter(prefix="/feature-limits", tags=["feature-limits"])


def get_feature_limit_service(
    db: AsyncSession = Depends(get_db),
) -> FeatureLimitService:
    """Get feature limit service dependency.

    Args:
        db: Database session

    Returns:
        Feature limit service instance
    """
    repo = FeatureLimitRepository(db)
    return FeatureLimitService(repo)


@router.get("", response_model=list[FeatureLimitResponse])
async def get_all_limits(
    _: AdminOrOwnerUser,
    service: FeatureLimitService = Depends(get_feature_limit_service),
) -> list[FeatureLimitResponse]:
    """Get all feature limits.

    Requires admin or owner access.

    Returns:
        List of all limits
    """
    return await service.get_all()


@router.get("/{role}", response_model=FeatureLimitResponse)
async def get_limit_by_role(
    role: str,
    _: AdminOrOwnerUser,
    service: FeatureLimitService = Depends(get_feature_limit_service),
) -> FeatureLimitResponse:
    """Get limit by role.

    Requires admin or owner access.

    Args:
        role: User role

    Returns:
        Limit for the role
    """
    limit = await service.get_by_role(role)
    if not limit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Limit for role '{role}' not found",
        )
    return limit


@router.post(
    "", response_model=FeatureLimitResponse, status_code=status.HTTP_201_CREATED
)
async def create_limit(
    data: FeatureLimitCreate,
    _: AdminOrOwnerUser,
    service: FeatureLimitService = Depends(get_feature_limit_service),
) -> FeatureLimitResponse:
    """Create new feature limit.

    Requires admin or owner access.

    Args:
        data: Limit data

    Returns:
        Created limit
    """
    try:
        return await service.create(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{role}", response_model=FeatureLimitResponse)
async def update_limit(
    role: str,
    data: FeatureLimitUpdate,
    _: AdminOrOwnerUser,
    service: FeatureLimitService = Depends(get_feature_limit_service),
) -> FeatureLimitResponse:
    """Update feature limit.

    Requires admin or owner access.

    Args:
        role: User role
        data: Update data

    Returns:
        Updated limit
    """
    try:
        return await service.update(role, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{role}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_limit(
    role: str,
    _: AdminOrOwnerUser,
    service: FeatureLimitService = Depends(get_feature_limit_service),
) -> None:
    """Delete feature limit.

    Requires admin or owner access.

    Args:
        role: User role
    """
    try:
        await service.delete(role)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
