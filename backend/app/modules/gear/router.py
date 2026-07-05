"""FastAPI router for gear management endpoints.

This module provides REST API endpoints for managing gear containers and items.
All endpoints require authentication.
"""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import AdminUser, CurrentUser
from app.modules.auth.models import User
from app.modules.auth.repositories import get_user_repository
from app.modules.auth.types.repository import UserRepositoryInterface
from app.modules.billing.service import BillingService
from app.modules.settings.db_models import UserSettingsDB

from .repository import GearRepository
from .schemas import (
    BatchOrderUpdateRequest,
    ContainerCreate,
    ContainerResponse,
    ContainerUpdate,
    ContainerRatingCreate,
    ContentReportCreate,
    ContentReportResponse,
    GlobalCatalogueItemCreate,
    GlobalCatalogueItemResponse,
    GlobalCatalogueItemSearchParams,
    GlobalCatalogueItemUpdate,
    ItemCreate,
    ItemMoveRequest,
    ItemPromotionStatus,
    ItemResponse,
    ItemUpdate,
    PromoteItemResponse,
    ShareTokenCreate,
    ShareTokenResponse,
    UserLimitsResponse,
)
from .service import GearService
from .catalogue_item_image_router import router as catalogue_item_image_router
from .item_image_router import router as item_image_router

router = APIRouter(prefix="/gear", tags=["gear"])

logger = logging.getLogger(__name__)

# Include item images router
router.include_router(item_image_router)
# Include catalogue item images router
router.include_router(catalogue_item_image_router)


def get_gear_repository(db: AsyncSession = Depends(get_db)) -> GearRepository:
    """Dependency to get gear repository instance.

    Args:
        db: Database session

    Returns:
        Gear repository instance
    """
    return GearRepository(db)


def get_gear_service(
    repository: GearRepository = Depends(get_gear_repository),
) -> GearService:
    """Dependency to get gear service instance.

    Args:
        repository: Gear repository instance

    Returns:
        Gear service instance
    """
    return GearService(repository)


GearServiceDep = Annotated[GearService, Depends(get_gear_service)]


def get_optional_billing_service(
    db: AsyncSession = Depends(get_db),
) -> BillingService | None:
    """Get billing service optionally (returns None if unavailable).

    This allows graceful degradation when billing service is not available.

    Args:
        db: Database session

    Returns:
        BillingService instance or None if unavailable
    """
    try:
        from app.modules.billing.dependencies import (
            get_billing_service,
            get_stripe_client,
        )
        from app.modules.billing.repository import BillingRepository

        billing_repo = BillingRepository(db)
        stripe_client = get_stripe_client()
        return get_billing_service(billing_repo, stripe_client)
    except Exception:
        # Graceful degradation - return None if billing service unavailable
        return None


OptionalBillingServiceDep = Annotated[
    BillingService | None, Depends(get_optional_billing_service)
]

# Optional authentication for public endpoints
optional_security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Security(optional_security),
    user_repository: Annotated[
        UserRepositoryInterface | None, Depends(get_user_repository)
    ] = None,
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None
    try:
        from app.modules.auth.dependencies import _verify_user_token
        from app.core.redis import get_redis_client
        from app.core.config import settings
        from app.core.auth.token_blacklist import TokenBlacklistService

        token = credentials.credentials
        if user_repository is None:
            return None

        # Get blacklist service
        redis_client = await get_redis_client()
        blacklist_service = TokenBlacklistService(
            redis_client=redis_client, key_prefix=settings.redis.token_blacklist_prefix
        )

        return await _verify_user_token(token, user_repository, blacklist_service, None)
    except Exception:
        # If authentication fails, return None (endpoint is public)
        return None


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


# Container endpoints
@router.post(
    "/containers",
    response_model=ContainerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new gear container",
)
async def create_container(
    data: ContainerCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
    db: AsyncSession = Depends(get_db),
    billing_service: OptionalBillingServiceDep = None,
) -> ContainerResponse:
    """Create a new gear container for the current user.

    Args:
        data: Container creation data
        current_user: Authenticated user
        service: Gear service instance
        db: Database session
        billing_service: Optional billing service for limit validation

    Returns:
        Created container

    Raises:
        HTTPException: If validation fails
    """
    # Get user settings for default public setting
    result = await db.execute(
        select(UserSettingsDB).where(UserSettingsDB.user_id == current_user.id)
    )
    settings = result.scalars().first()
    default_public = settings.default_containers_public if settings else False

    return await service.create_container(
        current_user.id,
        data,
        default_public=default_public,
        billing_service=billing_service,
    )


@router.get(
    "/containers",
    response_model=list[ContainerResponse],
    summary="Get all containers for the current user",
)
async def get_containers(
    current_user: CurrentUser,
    service: GearServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
) -> list[ContainerResponse]:
    """Get all gear containers for the current user.

    Args:
        current_user: Authenticated user
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of containers
    """
    return await service.get_containers(current_user.id, skip, limit)


@router.get(
    "/containers/{container_id}",
    response_model=ContainerResponse,
    summary="Get a container by ID",
)
async def get_container(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ContainerResponse:
    """Get a gear container by ID.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Container

    Raises:
        HTTPException: If container not found
    """
    container = await service.get_container(container_id, current_user.id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return container


@router.patch(
    "/containers/{container_id}",
    response_model=ContainerResponse,
    summary="Update a container",
)
async def update_container(
    container_id: str,
    data: ContainerUpdate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ContainerResponse:
    """Update a gear container.

    Args:
        container_id: Container ID
        data: Update data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated container

    Raises:
        HTTPException: If container not found
    """
    container = await service.update_container(container_id, current_user.id, data)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return container


@router.delete(
    "/containers",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all containers",
)
async def delete_all_containers(
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Delete all gear containers for the current user.

    Args:
        current_user: Authenticated user
        service: Gear service instance
    """
    await service.delete_all_containers(current_user.id)


@router.delete(
    "/containers/{container_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a container",
)
async def delete_container(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Delete a gear container and all its items.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If container not found
    """
    deleted = await service.delete_container(container_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )


# Item endpoints
@router.post(
    "/containers/{container_id}/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item in a container",
)
async def create_item(
    container_id: str,
    data: ItemCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
    billing_service: OptionalBillingServiceDep = None,
) -> ItemResponse:
    """Create a new gear item in a container.

    Args:
        container_id: Parent container ID
        data: Item creation data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Created item

    Raises:
        HTTPException: If container not found or validation fails
    """
    item = await service.create_item(
        container_id, current_user.id, data, billing_service=billing_service
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return item


@router.get(
    "/containers/{container_id}/items",
    response_model=list[ItemResponse],
    summary="Get all items in a container",
)
async def get_items(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
) -> list[ItemResponse]:
    """Get all items in a container.

    Args:
        container_id: Parent container ID
        current_user: Authenticated user
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of items
    """
    return await service.get_items(container_id, current_user.id, skip, limit)


@router.get(
    "/items",
    response_model=list[ItemResponse],
    summary="Get all items for the current user",
)
async def get_all_items(
    current_user: CurrentUser,
    service: GearServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
) -> list[ItemResponse]:
    """Get all gear items for the current user across all containers.

    Args:
        current_user: Authenticated user
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of items
    """
    return await service.get_all_items(current_user.id, skip, limit)


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Get an item by ID",
)
async def get_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Get a gear item by ID.

    Args:
        item_id: Item ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Item

    Raises:
        HTTPException: If item not found
    """
    item = await service.get_item(item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


@router.patch(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Update an item",
)
async def update_item(
    item_id: str,
    data: ItemUpdate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Update a gear item.

    Args:
        item_id: Item ID
        data: Update data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated item

    Raises:
        HTTPException: If item not found
    """
    item = await service.update_item(item_id, current_user.id, data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


@router.patch(
    "/items/{item_id}/move",
    response_model=ItemResponse,
    summary="Move an item to a different container",
)
async def move_item(
    item_id: str,
    data: ItemMoveRequest,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Move a gear item to a different container.

    Args:
        item_id: Item ID to move
        data: Move request with target container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated item with new container

    Raises:
        HTTPException: If item not found or target container invalid
    """
    try:
        item = await service.move_item(item_id, current_user.id, data.targetContainerId)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
)
async def delete_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Delete a gear item.

    Args:
        item_id: Item ID
        current_user: Authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If item not found
    """
    deleted = await service.delete_item(item_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )


@router.patch(
    "/items/batch-order",
    response_model=list[ItemResponse],
    summary="Batch update items order",
)
async def batch_update_item_order(
    data: BatchOrderUpdateRequest,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> list[ItemResponse]:
    """Batch update items' order values.

    Args:
        data: Batch order update request with list of item IDs and their new order values
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        List of updated item responses

    Raises:
        HTTPException: If validation fails or items not found
    """
    try:
        return await service.batch_update_item_order(current_user.id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# Statistics endpoints
@router.get(
    "/containers/{container_id}/stats/weight",
    summary="Calculate container weight",
)
async def get_container_weight(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> dict[str, float]:
    """Calculate total weight of a container.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Dictionary with weight in grams and kilograms

    Raises:
        HTTPException: If container not found
    """
    container = await service.get_container(container_id, current_user.id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return service.calculate_container_weight(container)


@router.get(
    "/containers/{container_id}/stats/readiness",
    summary="Calculate container readiness",
)
async def get_container_readiness(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> dict[str, int | float]:
    """Calculate container readiness statistics.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Dictionary with readiness statistics

    Raises:
        HTTPException: If container not found
    """
    container = await service.get_container(container_id, current_user.id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return service.calculate_container_readiness(container)


# Public container endpoints (no authentication required)
@router.get(
    "/public/containers",
    response_model=list[ContainerResponse],
    summary="Get all public containers",
)
async def get_public_containers(
    service: GearServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    current_user: OptionalUser = None,
) -> list[ContainerResponse]:
    """Get all public containers from all users.

    Args:
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Optional authenticated user (for user rating data)

    Returns:
        List of public containers with author names
    """
    requesting_user_id = current_user.id if current_user else None
    return await service.get_public_containers(skip, limit, requesting_user_id)


@router.get(
    "/public/containers/{container_id}",
    response_model=ContainerResponse,
    summary="Get a public container by ID",
)
async def get_public_container(
    container_id: str,
    service: GearServiceDep,
    current_user: OptionalUser = None,
) -> ContainerResponse:
    """Get a public container by ID.

    Args:
        container_id: Container ID
        service: Gear service instance
        current_user: Optional authenticated user (for user rating data)

    Returns:
        Public container with author name

    Raises:
        HTTPException: If container not found or not public
    """
    requesting_user_id = current_user.id if current_user else None
    container = await service.get_public_container(container_id, requesting_user_id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public container not found",
        )
    return container


# Shared container endpoints (no authentication required, token-based access)
@router.get(
    "/shared/containers/{token}",
    response_model=ContainerResponse,
    summary="Get a shared container by token",
)
async def get_shared_container(
    token: str,
    service: GearServiceDep,
) -> ContainerResponse:
    """Get a container by share token.

    Args:
        token: Share token
        service: Gear service instance

    Returns:
        Shared container with author name

    Raises:
        HTTPException: If token is invalid, expired, or container not found
    """
    container = await service.get_container_by_share_token(token)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared container not found or token expired",
        )
    return container


# Share token management endpoints (requires authentication)
@router.get(
    "/containers/{container_id}/share-tokens",
    response_model=list[ShareTokenResponse],
    summary="Get share tokens for a container",
)
async def get_container_share_tokens(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> list[ShareTokenResponse]:
    """Get all share tokens for a container.

    Args:
        container_id: Container ID
        current_user: Current authenticated user
        service: Gear service instance

    Returns:
        List of share tokens for the container

    Raises:
        HTTPException: If container not found or user doesn't own it
    """
    tokens = await service.get_share_tokens(container_id, current_user.id)
    return [ShareTokenResponse(**token) for token in tokens]


@router.post(
    "/containers/{container_id}/share-tokens",
    response_model=ShareTokenResponse,
    summary="Create a share token for a container",
)
async def create_container_share_token(
    container_id: str,
    current_user: CurrentUser,
    data: ShareTokenCreate,
    service: GearServiceDep,
) -> ShareTokenResponse:
    """Create a share token for a container.

    Args:
        container_id: Container ID
        current_user: Current authenticated user
        data: Share token creation data
        service: Gear service instance

    Returns:
        Created share token with share URL

    Raises:
        HTTPException: If container not found or user doesn't own it
    """
    token = await service.create_share_token(
        container_id, current_user.id, data.expiresAt
    )
    tokens = await service.get_share_tokens(container_id, current_user.id)
    # Find the newly created token
    token_data = next((t for t in tokens if t["token"] == token), None)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created token",
        )
    return ShareTokenResponse(**token_data)


@router.delete(
    "/containers/{container_id}/share-tokens/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a share token",
)
async def revoke_container_share_token(
    container_id: str,
    token: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Revoke a share token.

    Args:
        container_id: Container ID
        token: Share token to revoke
        current_user: Current authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If token not found or user doesn't own it
    """
    revoked = await service.revoke_share_token(token, current_user.id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share token not found or access denied",
        )


# Rating endpoints
@router.post(
    "/containers/{container_id}/rating", response_model=dict, summary="Rate a container"
)
async def rate_container(
    container_id: str,
    rating_data: ContainerRatingCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Rate a container (create or update rating).

    Supports two rating types:
    - 'owner': Rating by container owner (only if current_user is owner)
    - 'user': Rating by other users (only for public containers)
    """
    repository = GearRepository(db)

    # Verify container exists
    container = await repository.get_container(container_id, current_user.id)
    if not container:
        # Try public container
        container = await repository.get_public_container(container_id)
        if not container:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Container not found"
            )

    # Validate rating type
    is_owner = container.user_id == current_user.id

    if rating_data.ratingType == "owner" and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only container owner can set owner rating",
        )

    if rating_data.ratingType == "user" and is_owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Container owner should use 'owner' rating type",
        )

    if rating_data.ratingType == "user" and not container.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ratings are only allowed for public containers",
        )

    # Upsert rating
    rating = await repository.upsert_container_rating(
        container_id=container_id,
        user_id=current_user.id,
        rating=rating_data.rating,
        rating_type=rating_data.ratingType,
    )
    await db.commit()

    # Get updated stats
    if rating_data.ratingType == "owner":
        owner_rating: int | None = rating.rating
        avg_user_rating = await repository.get_container_average_user_rating(
            container_id
        )
        user_rating_count = await repository.get_container_user_rating_count(
            container_id
        )
    else:
        owner_rating = await repository.get_container_owner_rating(container_id)
        avg_user_rating = await repository.get_container_average_user_rating(
            container_id
        )
        user_rating_count = await repository.get_container_user_rating_count(
            container_id
        )

    return {
        "rating": rating.rating,
        "ratingType": rating.rating_type,
        "ownerRating": owner_rating,
        "averageUserRating": float(avg_user_rating) if avg_user_rating else None,
        "userRatingCount": user_rating_count,
    }


@router.delete("/containers/{container_id}/rating", summary="Delete container rating")
async def delete_container_rating(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
    rating_type: str = Query(
        default="user", description="Type of rating to delete: 'owner' or 'user'"
    ),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete user's rating for a container."""
    repository = GearRepository(db)

    # Verify container exists
    container = await repository.get_container(container_id, current_user.id)
    if not container:
        container = await repository.get_public_container(container_id)
        if not container:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Container not found"
            )

    # Validate rating type
    is_owner = container.user_id == current_user.id

    if rating_type == "owner" and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only container owner can delete owner rating",
        )

    # Delete rating
    deleted = await repository.delete_container_rating(
        container_id, current_user.id, rating_type
    )
    await db.commit()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found"
        )

    # Get updated stats
    owner_rating = await repository.get_container_owner_rating(container_id)
    avg_user_rating = await repository.get_container_average_user_rating(container_id)
    user_rating_count = await repository.get_container_user_rating_count(container_id)

    return {
        "message": "Rating deleted",
        "ownerRating": owner_rating,
        "averageUserRating": float(avg_user_rating) if avg_user_rating else None,
        "userRatingCount": user_rating_count,
    }


# Global Catalogue endpoints (public - no authentication required for GET)
@router.get(
    "/catalogue/items",
    response_model=list[GlobalCatalogueItemResponse],
    summary="Get global catalogue items",
)
async def get_catalogue_items(
    service: GearServiceDep,
    query: str | None = Query(None, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    brand: str | None = Query(None, description="Filter by brand"),
    priceTier: Literal["low", "medium", "high"] | None = Query(
        None, description="Filter by price tier", alias="priceTier"
    ),
    quality: Literal["low", "medium", "high"] | None = Query(
        None, description="Filter by quality"
    ),
    isActive: bool | None = Query(
        True, description="Filter by active status", alias="isActive"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    current_user: OptionalUser = None,
) -> list[GlobalCatalogueItemResponse]:
    """Get global catalogue items with filtering and search.

    Args:
        query: Search query
        category: Filter by category
        brand: Filter by brand
        priceTier: Filter by price tier
        quality: Filter by quality
        isActive: Filter by active status
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: Gear service instance
        current_user: Optional authenticated user (for future use, e.g., personalized results)

    Returns:
        List of catalogue items
    """
    search_params = GlobalCatalogueItemSearchParams(
        query=query,
        category=category,
        brand=brand,
        priceTier=priceTier,
        quality=quality,
        isActive=isActive,
        skip=skip,
        limit=limit,
    )
    return await service.get_catalogue_items(search_params)


@router.get(
    "/catalogue/items/{item_id}",
    response_model=GlobalCatalogueItemResponse,
    summary="Get a catalogue item by ID",
)
async def get_catalogue_item(
    item_id: str,
    service: GearServiceDep,
    current_user: OptionalUser = None,
) -> GlobalCatalogueItemResponse:
    """Get a single catalogue item by ID.

    Args:
        item_id: Catalogue item ID
        service: Gear service instance
        current_user: Optional authenticated user (for future use, e.g., personalized results)

    Returns:
        Catalogue item

    Raises:
        HTTPException: If item not found
    """
    item = await service.get_catalogue_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalogue item not found",
        )
    return item


@router.post(
    "/catalogue/items",
    response_model=GlobalCatalogueItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new catalogue item",
)
async def create_catalogue_item(
    data: GlobalCatalogueItemCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> GlobalCatalogueItemResponse:
    """Create a new catalogue item.

    Args:
        data: Item creation data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Created catalogue item
    """
    return await service.create_catalogue_item(current_user.id, data)


@router.patch(
    "/catalogue/items/{item_id}",
    response_model=GlobalCatalogueItemResponse,
    summary="Update a catalogue item",
)
async def update_catalogue_item(
    item_id: str,
    data: GlobalCatalogueItemUpdate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> GlobalCatalogueItemResponse:
    """Update a catalogue item.

    Only the creator or admin can update items.

    Args:
        item_id: Catalogue item ID
        data: Update data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated catalogue item

    Raises:
        HTTPException: If item not found or user doesn't have permission
    """
    # Check if user is admin/owner
    is_admin = (
        current_user.isAdmin if hasattr(current_user, "isAdmin") else False
    ) or (current_user.isOwner if hasattr(current_user, "isOwner") else False)
    item = await service.update_catalogue_item(
        item_id,
        current_user.id,
        data,
        is_admin=is_admin,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalogue item not found or you don't have permission to update it",
        )
    return item


@router.delete(
    "/catalogue/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a catalogue item (soft delete)",
)
async def delete_catalogue_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Delete a catalogue item (soft delete by setting is_active=False).

    Only the creator or admin can delete items.

    Args:
        item_id: Catalogue item ID
        current_user: Authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If item not found or user doesn't have permission
    """
    # Check if user is admin/owner
    is_admin = (
        current_user.isAdmin if hasattr(current_user, "isAdmin") else False
    ) or (current_user.isOwner if hasattr(current_user, "isOwner") else False)
    deleted = await service.delete_catalogue_item(
        item_id,
        current_user.id,
        is_admin=is_admin,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalogue item not found or you don't have permission to delete it",
        )


@router.post(
    "/containers/{container_id}/items/from-catalogue/{catalogue_item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a catalogue item to a container",
)
async def add_catalogue_item_to_container(
    container_id: str,
    catalogue_item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
    quantity: int = Query(1, ge=1, description="Item quantity"),
    status_param: str = Query("owned", description="Item status", alias="status"),
    priority: str = Query("medium", description="Item priority"),
    copy_image: bool = Query(False, description="Copy image from catalogue item"),
) -> ItemResponse:
    """Add a catalogue item to a user's container.

    Creates a new item in the container based on catalogue item data.
    The new item is independent (not linked to catalogue).

    Args:
        container_id: Target container ID
        catalogue_item_id: Catalogue item ID to copy
        current_user: Authenticated user
        quantity: Item quantity
        status_param: Item status
        priority: Item priority
        copy_image: Whether to copy images from catalogue item
        service: Gear service instance

    Returns:
        Created item

    Raises:
        HTTPException: If container or catalogue item not found
    """
    item = await service.add_catalogue_item_to_container(
        container_id,
        catalogue_item_id,
        current_user.id,
        quantity=quantity,
        status=status_param,
        priority=priority,
        copy_image=copy_image,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container or catalogue item not found",
        )
    return item


@router.patch(
    "/items/{item_id}/link-to-catalogue/{catalogue_item_id}",
    response_model=ItemResponse,
    summary="Link item to catalogue",
)
async def link_item_to_catalogue(
    item_id: str,
    catalogue_item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Link an item to a catalogue item (set catalogue_item_id).

    Args:
        item_id: Item ID to link
        catalogue_item_id: Catalogue item ID to link to
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated item

    Raises:
        HTTPException: If item or catalogue item not found, or user doesn't own the item
    """
    item = await service.link_item_to_catalogue(
        item_id, catalogue_item_id, current_user.id
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item or catalogue item not found, or you don't have permission to modify it",
        )
    return item


@router.patch(
    "/items/{item_id}/update-from-catalogue",
    response_model=ItemResponse,
    summary="Update item from catalogue",
)
async def update_item_from_catalogue(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
    fields: str | None = Query(
        None,
        description="Comma-separated list of fields to update (e.g., 'name,weight,price')",
    ),
) -> ItemResponse:
    """Update an item with data from its linked catalogue item.

    Updates only specified fields from catalogue while preserving user-specific fields
    like quantity, status, priority, and notes.

    Args:
        item_id: Item ID to update
        current_user: Authenticated user
        service: Gear service instance
        fields: Comma-separated list of field names to update. If not provided, updates all available fields.

    Returns:
        Updated item

    Raises:
        HTTPException: If item not found, not linked to catalogue, or user doesn't own it
    """
    fields_list = None
    if fields:
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]

    item = await service.update_item_from_catalogue(
        item_id, current_user.id, fields_list
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found, not linked to catalogue, or you don't have permission to modify it",
        )
    return item


@router.post(
    "/items/{item_id}/fetch-images-from-catalogue",
    response_model=ItemResponse,
    summary="Fetch images from catalogue",
)
async def fetch_images_from_catalogue(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Fetch images from catalogue item and attach them to the gear item.

    Copies images from the linked catalogue item to the user's item.
    The item must be linked to a catalogue item (have catalogue_item_id).

    Args:
        item_id: Item ID to fetch images for
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated item with fetched images

    Raises:
        HTTPException: If item not found, not linked to catalogue, or user doesn't own it
    """
    item = await service.fetch_images_from_catalogue(item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found, not linked to catalogue, or you don't have permission to modify it",
        )
    return item


@router.patch(
    "/items/{item_id}/unlink-from-catalogue",
    response_model=ItemResponse,
    summary="Unlink item from catalogue",
)
async def unlink_item_from_catalogue(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Unlink an item from the catalogue (clear catalogue_item_id).

    Args:
        item_id: Item ID to unlink
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated item

    Raises:
        HTTPException: If item not found or user doesn't own it
    """
    item = await service.unlink_item_from_catalogue(item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you don't have permission to modify it",
        )
    return item


@router.post(
    "/items/{item_id}/promote",
    response_model=PromoteItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Promote item to catalogue",
    description="Promote an item from a public container to the global catalogue. Requires authenticated user with account older than 1 month.",
)
async def promote_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> PromoteItemResponse:
    """Promote an item to catalogue.

    Args:
        item_id: Item ID to promote
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Promotion response with updated count

    Raises:
        HTTPException: If promotion is not allowed or item not found
    """
    try:
        item = await service.promote_item(item_id, current_user.id)
        return PromoteItemResponse(
            success=True,
            promote_count=item.promoteCount,
            message="Item promoted successfully",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/items/{item_id}/promotion-status",
    response_model=ItemPromotionStatus,
    summary="Get item promotion status",
    description="Get promotion status for an item. Public endpoint, but includes user-specific info if authenticated.",
)
async def get_promotion_status(
    item_id: str,
    service: GearServiceDep,
    current_user: OptionalUser = None,
) -> ItemPromotionStatus:
    """Get promotion status for an item.

    Args:
        item_id: Item ID
        current_user: Optional authenticated user (for user-specific info)
        service: Gear service instance

    Returns:
        Promotion status

    Raises:
        HTTPException: If item not found
    """
    try:
        user_id = current_user.id if current_user else None
        return await service.get_promotion_status(item_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post(
    "/items/{item_id}/add-to-catalogue",
    response_model=GlobalCatalogueItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to catalogue (admin)",
    description="Add an item to the global catalogue directly (admin override - bypasses promotion threshold).",
)
async def add_item_to_catalogue(
    item_id: str,
    admin_user: AdminUser,
    service: GearServiceDep,
) -> GlobalCatalogueItemResponse:
    """Add an item to catalogue (admin override).

    Args:
        item_id: Item ID to add to catalogue
        admin_user: Authenticated admin user
        service: Gear service instance

    Returns:
        Created catalogue item

    Raises:
        HTTPException: If item not found or already in catalogue
    """
    try:
        catalogue_item = await service.add_item_to_catalogue(item_id, admin_user.id)
        return catalogue_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/containers/{container_id}/report",
    response_model=ContentReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report a public container",
    description="Report a public container for inappropriate content. Requires authentication.",
)
async def report_container(
    container_id: str,
    report_data: ContentReportCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ContentReportResponse:
    """Report a public container for inappropriate content.

    Args:
        container_id: Container ID to report
        report_data: Report data (reason and optional additional info)
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Created report

    Raises:
        HTTPException: If container not found, not public, or already reported by user
    """
    try:
        report = await service.report_container(
            container_id=container_id,
            reporter_user_id=current_user.id,
            reason=report_data.reason,
            additional_info=report_data.additionalInfo,
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        # Handle IntegrityError (duplicate report)
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reported this container",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report",
        ) from e


@router.get(
    "/containers/{container_id}/report/status",
    summary="Get user's report status for a container",
    description="Check if the current user has reported this container.",
)
async def get_report_status(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> dict[str, bool]:
    """Check if current user has reported a container.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Dictionary with hasReported boolean
    """
    has_reported = await service.get_user_report_status(
        container_id=container_id,
        user_id=current_user.id,
    )
    return {"hasReported": has_reported}


@router.delete(
    "/containers/{container_id}/report",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Withdraw a report",
    description="Withdraw (delete) the current user's report for a container.",
)
async def withdraw_report(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Withdraw the current user's report for a container.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If report not found
    """
    deleted = await service.withdraw_report(
        container_id=container_id,
        user_id=current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )


@router.get(
    "/me/limits",
    response_model=UserLimitsResponse,
    summary="Get user account limits and usage",
)
async def get_user_limits(
    current_user: CurrentUser,
    service: GearServiceDep,
    db: AsyncSession = Depends(get_db),
) -> UserLimitsResponse:
    """Get user account limits and current usage.

    Args:
        current_user: Authenticated user
        service: Gear service instance
        db: Database session

    Returns:
        User limits and usage information
    """
    # Get billing service for limits
    try:
        from app.modules.billing.dependencies import (
            get_billing_service,
            get_stripe_client,
        )
        from app.modules.billing.repository import BillingRepository

        billing_repo = BillingRepository(db)
        stripe_client = get_stripe_client()
        billing_service = get_billing_service(billing_repo, stripe_client)
        limits = await billing_service.get_subscription_limits(current_user.id)
    except Exception:
        # Fallback to free tier if billing service unavailable
        from app.modules.billing.schemas import SubscriptionLimitsResponse

        limits = SubscriptionLimitsResponse(
            planTier="free",
            aiMonthlyTokenLimit=0,
            storageLimit=100 * 1024 * 1024,
            canExportData=True,
            canUseAdvancedFeatures=False,
            requiresByok=True,
            itemsLimit=2000,  # Updated to match new free tier limits
            containersLimit=100,  # Updated to match new free tier limits
        )

    # Get current usage
    items_count = await service.repository.count_user_items(current_user.id)
    containers_count = await service.repository.count_user_containers(current_user.id)

    return UserLimitsResponse(
        tier=limits.planTier,
        limits={
            "items": limits.itemsLimit,
            "containers": limits.containersLimit,
        },
        usage={
            "items": items_count,
            "containers": containers_count,
        },
        percentage={
            "items": (
                (items_count / limits.itemsLimit * 100)
                if limits.itemsLimit > 0
                else 0.0
            ),
            "containers": (
                (containers_count / limits.containersLimit * 100)
                if limits.containersLimit > 0
                else 0.0
            ),
        },
    )
