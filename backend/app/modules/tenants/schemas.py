"""Pydantic schemas for tenant endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=512)


class TenantResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    role: str
    createdAt: datetime


class TenantListResponse(BaseModel):
    tenants: list[TenantResponse]
