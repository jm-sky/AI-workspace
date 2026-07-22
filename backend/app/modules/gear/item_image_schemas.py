"""Pydantic schemas for item image API."""

from pydantic import BaseModel, Field


class ItemImageResponse(BaseModel):
    """Response schema for item image."""

    id: str
    item_id: str = Field(alias="itemId")
    user_id: str = Field(alias="userId")
    url: str
    file_name: str = Field(alias="fileName")
    file_size: int = Field(alias="fileSize")
    mime_type: str = Field(alias="mimeType")
    width: int | None
    height: int | None
    is_primary: bool = Field(alias="isPrimary")
    order: int
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class ItemImageFromUrlRequest(BaseModel):
    """Request schema for creating image from external URL."""

    url: str = Field(..., description="External image URL")
    is_primary: bool = Field(False, alias="isPrimary")
    host_locally: bool = Field(
        True,
        alias="hostLocally",
        description="If True, download and store image. If False, only save external URL.",
    )

    model_config = {"populate_by_name": True}


class ImageOrderUpdate(BaseModel):
    """Schema for updating image order."""

    id: str
    order: int


class ImageOrdersUpdate(BaseModel):
    """Schema for batch updating image orders."""

    image_orders: list[ImageOrderUpdate] = Field(alias="imageOrders")

    model_config = {"populate_by_name": True}
