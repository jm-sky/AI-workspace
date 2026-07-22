"""API router for catalogue item image uploads."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import AdminOrOwnerUser
from app.modules.gear.catalogue_item_image_schemas import (
    CatalogueImageOrdersUpdate,
    CatalogueItemImageFromUrlRequest,
    CatalogueItemImageResponse,
)
from app.modules.gear.catalogue_item_image_upload_service import (
    CatalogueItemImageUploadService,
)

router = APIRouter(prefix="/catalogue/items", tags=["catalogue-item-images"])


@router.post("/{catalogue_item_id}/images", response_model=CatalogueItemImageResponse)
async def upload_catalogue_item_image(
    catalogue_item_id: str,
    current_user: AdminOrOwnerUser,
    file: UploadFile = File(...),
    is_primary: bool = Query(False, description="Whether this should be the primary image"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CatalogueItemImageUploadService(db)
    await service.validate_upload(file, catalogue_item_id, current_user.id)
    return await service.upload_image(file, catalogue_item_id, current_user.id, is_primary)


@router.get("/{catalogue_item_id}/images", response_model=list[CatalogueItemImageResponse])
async def get_catalogue_item_images(
    catalogue_item_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    service = CatalogueItemImageUploadService(db)
    return await service.get_images(catalogue_item_id)


@router.delete("/images/{image_id}")
async def delete_catalogue_item_image(
    image_id: str,
    current_user: AdminOrOwnerUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CatalogueItemImageUploadService(db)
    success = await service.delete_image(image_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return {"message": "Image deleted successfully"}


@router.put("/{catalogue_item_id}/images/reorder")
async def reorder_catalogue_item_images(
    catalogue_item_id: str,
    data: CatalogueImageOrdersUpdate,
    current_user: AdminOrOwnerUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CatalogueItemImageUploadService(db)
    image_orders = [{"id": item.id, "order": item.order} for item in data.imageOrders]
    await service.reorder_images(catalogue_item_id, image_orders)
    return {"message": "Images reordered successfully"}


@router.put("/{catalogue_item_id}/images/{image_id}/primary")
async def toggle_catalogue_primary_image(
    catalogue_item_id: str,
    image_id: str,
    current_user: AdminOrOwnerUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CatalogueItemImageUploadService(db)
    is_primary = await service.toggle_primary_image(catalogue_item_id, image_id)
    return {"message": "Primary image toggled successfully", "is_primary": is_primary}


@router.post("/{catalogue_item_id}/images/from-url", response_model=CatalogueItemImageResponse)
async def upload_catalogue_item_image_from_url(
    catalogue_item_id: str,
    current_user: AdminOrOwnerUser,
    data: CatalogueItemImageFromUrlRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = CatalogueItemImageUploadService(db)
    return await service.upload_image_from_url(data.url, catalogue_item_id, current_user.id, data.isPrimary, data.hostLocally)
