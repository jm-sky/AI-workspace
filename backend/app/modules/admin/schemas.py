"""Pydantic schemas for admin endpoints."""

from datetime import datetime

from pydantic import BaseModel


class AdminUserResponse(BaseModel):
    """Response schema for admin user data."""

    id: str
    name: str
    email: str
    avatarUrl: str | None = None
    isActive: bool
    isAdmin: bool
    isOwner: bool = False
    isPremium: bool = False
    isEmailVerified: bool
    emailVerifiedAt: str | None = None
    createdAt: str
    updatedAt: str


class AdminContainerResponse(BaseModel):
    """Response schema for admin container data."""

    id: str
    name: str
    description: str | None = None
    type: str
    color: str | None = None
    isPublic: bool
    authorId: str | None = None
    authorName: str | None = None
    itemCount: int
    createdAt: str
    updatedAt: str


class AdminItemResponse(BaseModel):
    """Response schema for admin item data."""

    id: str
    name: str
    category: str
    quantity: int
    weight: float
    weightUnit: str
    status: str
    priority: str
    containerId: str
    containerName: str | None = None
    authorId: str | None = None
    authorName: str | None = None
    createdAt: str
    updatedAt: str
