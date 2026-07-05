"""Pydantic schemas for stats endpoints."""

from pydantic import BaseModel


class UserStatsResponse(BaseModel):
    """Response schema for user statistics."""

    total: int
    newThisMonth: int


class ContainerStatsResponse(BaseModel):
    """Response schema for container statistics."""

    total: int
    newThisMonth: int


class ItemStatsResponse(BaseModel):
    """Response schema for item statistics."""

    total: int
    newThisMonth: int
