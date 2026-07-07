"""Pydantic schemas for team endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=512)


class TeamResponse(BaseModel):
    id: str
    tenantId: str
    name: str
    description: str | None = None
    role: str
    createdAt: datetime


class TeamListResponse(BaseModel):
    teams: list[TeamResponse]
