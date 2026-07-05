"""Pydantic schemas for catalogue item image API."""

from datetime import datetime

from pydantic import BaseModel, Field


class CatalogueItemImageResponse(BaseModel):
    """Response schema for catalogue item image."""

    id: str
    catalogueItemId: str = Field(alias="catalogueItemId")
    userId: str = Field(alias="userId")
    url: str
    fileName: str = Field(alias="fileName")
    fileSize: int = Field(alias="fileSize")
    mimeType: str = Field(alias="mimeType")
    width: int | None
    height: int | None
    isPrimary: bool = Field(alias="isPrimary")
    order: int
    createdAt: str = Field(alias="createdAt")
    updatedAt: str = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class CatalogueItemImageFromUrlRequest(BaseModel):
    """Request schema for creating catalogue image from external URL."""

    url: str = Field(..., description="External image URL")
    isPrimary: bool = Field(False, alias="isPrimary")
    hostLocally: bool = Field(
        True,
        alias="hostLocally",
        description="If True, download and store image. If False, only save external URL.",
    )

    model_config = {"populate_by_name": True}


class CatalogueImageOrderUpdate(BaseModel):
    """Schema for updating catalogue image order."""

    id: str
    order: int


class CatalogueImageOrdersUpdate(BaseModel):
    """Schema for batch updating catalogue image orders."""

    imageOrders: list[CatalogueImageOrderUpdate] = Field(alias="imageOrders")

    model_config = {"populate_by_name": True}
