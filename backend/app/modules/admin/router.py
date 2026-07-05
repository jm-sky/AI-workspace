"""FastAPI router for admin endpoints.

This module provides admin-only endpoints for managing users, containers, and items.
All endpoints require admin authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.repositories import (
    UserRepository as AuthUserRepository,
    get_user_repository as get_auth_user_repository,
)
from app.modules.auth.dependencies import AdminOrOwnerUser, AdminUser
from app.modules.users.repositories import UserRepository, get_user_repository
from app.modules.users.schemas import UserUpdate

from .repository import AdminRepository
from .schemas import AdminUserResponse, AdminContainerResponse, AdminItemResponse
from .service import AdminService

# Import gear service for content reports
from app.modules.gear.repository import GearRepository
from app.modules.gear.service import GearService
from app.modules.gear.schemas import (
    ContentReportListResponse,
    ContentReportResponse,
    ContentReportUpdate,
    ReportStatus,
    ContainerUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_repository(db: AsyncSession = Depends(get_db)) -> AdminRepository:
    """Dependency to get admin repository instance."""
    return AdminRepository(db)


def get_admin_service(
    repository: AdminRepository = Depends(get_admin_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    auth_user_repository: AuthUserRepository = Depends(get_auth_user_repository),
) -> AdminService:
    """Dependency to get admin service instance."""
    return AdminService(repository, user_repository, auth_user_repository)


def get_gear_repository(db: AsyncSession = Depends(get_db)) -> GearRepository:
    """Dependency to get gear repository instance."""
    return GearRepository(db)


def get_gear_service(
    repository: GearRepository = Depends(get_gear_repository),
) -> GearService:
    """Dependency to get gear service instance."""
    return GearService(repository)


# Users endpoints
@router.get(
    "/users",
    response_model=list[AdminUserResponse],
    summary="Get all users (admin only)",
    description="Get list of all users with pagination",
)
async def get_all_users(
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[AdminUserResponse]:
    """Get all users (admin only)."""
    return await service.get_all_users(skip=skip, limit=limit)


@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Get user by ID (admin only)",
    description="Get a specific user by their ID",
)
async def get_user_by_id(
    user_id: str,
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminUserResponse:
    """Get user by ID (admin only)."""
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
        )
    return user


@router.patch(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Update user (admin only)",
    description="Update user information",
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminUserResponse:
    """Update user (admin or owner only)."""
    user = await service.update_user(user_id, user_data, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
        )
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (admin only)",
    description="Delete a user (soft delete - sets isActive to false)",
)
async def delete_user(
    user_id: str,
    current_user: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> None:
    """Delete user (admin or owner only)."""
    success = await service.delete_user(user_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
        )


# Containers endpoints
@router.get(
    "/containers",
    response_model=list[AdminContainerResponse],
    summary="Get all containers (admin only)",
    description="Get list of all containers from all users",
)
async def get_all_containers(
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[AdminContainerResponse]:
    """Get all containers (admin only)."""
    return await service.get_all_containers(skip=skip, limit=limit)


@router.get(
    "/containers/{container_id}",
    response_model=AdminContainerResponse,
    summary="Get container by ID (admin only)",
    description="Get a specific container by its ID",
)
async def get_container_by_id(
    container_id: str,
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminContainerResponse:
    """Get container by ID (admin only)."""
    container = await service.get_container_by_id(container_id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )
    return container


@router.patch(
    "/containers/{container_id}",
    response_model=AdminContainerResponse,
    summary="Update container (admin only)",
    description="Update a container (admin only)",
)
async def update_container(
    container_id: str,
    data: ContainerUpdate,
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminContainerResponse:
    """Update container (admin only)."""
    update_data = data.model_dump(exclude_unset=True)
    container = await service.update_container(container_id, update_data)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )
    return container


@router.delete(
    "/containers/{container_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete container (admin only)",
    description="Delete a container and all its items",
)
async def delete_container(
    container_id: str,
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> None:
    """Delete container (admin only)."""
    success = await service.delete_container(container_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )


# Items endpoints
@router.get(
    "/items",
    response_model=list[AdminItemResponse],
    summary="Get all items (admin only)",
    description="Get list of all items from all containers",
)
async def get_all_items(
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[AdminItemResponse]:
    """Get all items (admin only)."""
    return await service.get_all_items(skip=skip, limit=limit)


@router.get(
    "/items/{item_id}",
    response_model=AdminItemResponse,
    summary="Get item by ID (admin only)",
    description="Get a specific item by its ID",
)
async def get_item_by_id(
    item_id: str,
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminItemResponse:
    """Get item by ID (admin only)."""
    item = await service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )
    return item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item (admin only)",
    description="Delete an item",
)
async def delete_item(
    item_id: str,
    _: AdminOrOwnerUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> None:
    """Delete item (admin only)."""
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )


# Content reports endpoints
@router.get(
    "/reports",
    response_model=ContentReportListResponse,
    summary="Get content reports (admin only)",
    description="Get list of content reports with optional filters",
)
async def get_reports(
    admin_user: AdminUser,
    gear_service: Annotated[GearService, Depends(get_gear_service)],
    status: ReportStatus | None = Query(None, description="Filter by report status"),
    container_id: str | None = Query(None, description="Filter by container ID"),
    limit: int = Query(default=50, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
) -> ContentReportListResponse:
    """Get content reports (admin only).

    Args:
        admin_user: Authenticated admin user
        gear_service: Gear service instance
        status: Filter by report status
        container_id: Filter by container ID
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        List of reports with pagination info
    """
    return await gear_service.get_reports(
        status=status,
        container_id=container_id,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/reports/{report_id}",
    response_model=ContentReportResponse,
    summary="Update report status (admin only)",
    description="Update the status of a content report",
)
async def update_report_status(
    report_id: str,
    update_data: ContentReportUpdate,
    admin_user: AdminUser,
    gear_service: Annotated[GearService, Depends(get_gear_service)],
) -> ContentReportResponse:
    """Update report status (admin only).

    Args:
        report_id: Report ID
        update_data: Update data (status)
        admin_user: Authenticated admin user
        gear_service: Gear service instance

    Returns:
        Updated report

    Raises:
        HTTPException: If report not found
    """
    report = await gear_service.update_report_status(
        report_id=report_id,
        status=update_data.status,
        reviewer_id=admin_user.id,
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )
    return report
