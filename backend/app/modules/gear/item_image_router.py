"""API router for item image uploads."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import PremiumOrHigherUser
from app.modules.gear.image_upload_service import ImageUploadService
from app.modules.gear.item_image_schemas import (
    ImageOrdersUpdate,
    ItemImageFromUrlRequest,
    ItemImageResponse,
)

router = APIRouter(prefix="/items", tags=["item-images"])


@router.post("/{item_id}/images", response_model=dict)
async def upload_item_image(
    item_id: str,
    current_user: PremiumOrHigherUser,
    file: UploadFile = File(...),
    is_primary: bool = Query(
        False, description="Whether this should be the primary image"
    ),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Upload image for item (admin only).

    Args:
        item_id: Item ID
        file: Image file to upload
        is_primary: Whether this should be the primary image
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Image metadata
    """
    service = ImageUploadService(db)

    # Validate upload
    await service.validate_upload(file, item_id, current_user.id)

    # Upload and process
    result = await service.upload_image(file, item_id, current_user.id, is_primary)

    return result


@router.get("/{item_id}/images", response_model=list[ItemImageResponse])
async def get_item_images(
    item_id: str, db: AsyncSession = Depends(get_db)
) -> list[ItemImageResponse]:
    """
    Get all images for an item.

    Args:
        item_id: Item ID
        db: Database session

    Returns:
        List of images with URLs
    """
    service = ImageUploadService(db)
    images = await service.get_item_images(item_id)
    return images


@router.delete("/images/{image_id}")
async def delete_item_image(
    image_id: str,
    current_user: PremiumOrHigherUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete item image (admin only).

    Args:
        image_id: Image ID
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Success message
    """
    service = ImageUploadService(db)
    success = await service.delete_image(image_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    return {"message": "Image deleted successfully"}


@router.put("/{item_id}/images/reorder")
async def reorder_item_images(
    item_id: str,
    data: ImageOrdersUpdate,
    current_user: PremiumOrHigherUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Reorder images for item (admin only).

    Args:
        item_id: Item ID
        data: Image order updates
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Success message
    """
    service = ImageUploadService(db)
    image_orders = [{"id": item.id, "order": item.order} for item in data.image_orders]
    await service.reorder_images(item_id, image_orders)
    return {"message": "Images reordered successfully"}


@router.put("/{item_id}/images/{image_id}/primary")
async def toggle_primary_image(
    item_id: str,
    image_id: str,
    current_user: PremiumOrHigherUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Toggle primary status for image (set if not primary, unset if already primary).

    Args:
        item_id: Item ID
        image_id: Image ID to toggle primary status
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Success message with is_primary status
    """
    service = ImageUploadService(db)
    is_primary = await service.toggle_primary_image(item_id, image_id)
    return {
        "message": "Primary image toggled successfully",
        "is_primary": is_primary,
    }


@router.post("/{item_id}/images/from-url", response_model=dict)
async def upload_item_image_from_url(
    item_id: str,
    current_user: PremiumOrHigherUser,
    data: ItemImageFromUrlRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Create image for item from external URL (admin only).

    Args:
        item_id: Item ID
        data: URL payload
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Image metadata
    """
    service = ImageUploadService(db)
    result = await service.upload_image_from_url(
        data.url, item_id, current_user.id, data.is_primary, data.host_locally
    )
    return result
