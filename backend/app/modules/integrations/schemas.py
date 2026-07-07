"""Pydantic schemas for integration token endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IntegrationTokenStoreRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    accessToken: str = Field(min_length=1)
    refreshToken: str | None = None
    expiresAt: datetime | None = None
    scopes: str | None = None
    providerMetadata: dict[str, Any] | None = None


class IntegrationConnectionResponse(BaseModel):
    provider: str
    expiresAt: datetime | None = None
    scopes: str | None = None
    hasRefreshToken: bool = False


class IntegrationConnectionsListResponse(BaseModel):
    connections: list[IntegrationConnectionResponse]
