"""Pydantic schemas for integration token endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.modules.integrations.types import (
    DEFAULT_GITHUB_SCOPES,
    IntegrationVisibilityScope,
)


class IntegrationTokenStoreRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    accessToken: str = Field(min_length=1)
    refreshToken: str | None = None
    expiresAt: datetime | None = None
    scopes: str | None = None
    providerMetadata: dict[str, Any] | None = None
    visibilityScope: IntegrationVisibilityScope = IntegrationVisibilityScope.USER
    teamId: str | None = None


class IntegrationAuthUrlRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    scopes: list[str] = Field(default_factory=lambda: list(DEFAULT_GITHUB_SCOPES))
    visibilityScope: IntegrationVisibilityScope = IntegrationVisibilityScope.USER
    teamId: str | None = None

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, value: list[str]) -> list[str]:
        cleaned = [scope.strip() for scope in value if scope.strip()]
        if not cleaned:
            raise ValueError("At least one scope is required")
        return cleaned


class IntegrationAuthUrlResponse(BaseModel):
    authUrl: str
    state: str


class IntegrationOAuthCallbackRequest(BaseModel):
    code: str = Field(min_length=1)
    state: str = Field(min_length=1)


class IntegrationScopeOptionResponse(BaseModel):
    id: str
    labelKey: str
    descriptionKey: str
    required: bool = False


class IntegrationProviderSetupResponse(BaseModel):
    id: str
    enabled: bool
    kind: str = "oauth_app"
    scopes: list[IntegrationScopeOptionResponse] = Field(default_factory=list)


class IntegrationSetupResponse(BaseModel):
    tenantId: str
    tenantRole: str
    canManageShared: bool
    teams: list[dict[str, str]]
    providers: list[IntegrationProviderSetupResponse]


class IntegrationConnectionResponse(BaseModel):
    id: str
    provider: str
    visibilityScope: IntegrationVisibilityScope
    tenantId: str | None = None
    teamId: str | None = None
    teamName: str | None = None
    ownerUserId: str
    isOwner: bool
    expiresAt: datetime | None = None
    scopes: str | None = None
    hasRefreshToken: bool = False
    providerMetadata: dict[str, Any] | None = None
    canManage: bool = False


class IntegrationConnectionsListResponse(BaseModel):
    connections: list[IntegrationConnectionResponse]


class IntegrationConnectionUpdateRequest(BaseModel):
    visibilityScope: IntegrationVisibilityScope
    teamId: str | None = None
