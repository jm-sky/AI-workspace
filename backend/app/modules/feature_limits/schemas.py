"""Pydantic schemas for feature limits endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FeatureLimitBase(BaseModel):
    """Base schema for feature limits."""

    role: str = Field(..., description="User role", pattern="^(user|premium|admin|owner)$")
    ai_limit: float | None = Field(None, description="AI usage limit in USD (null = unlimited)")
    storage_limit_bytes: int = Field(..., description="Storage limit in bytes", gt=0)
    description: str | None = Field(None, description="Optional description")

    @field_validator("ai_limit")
    @classmethod
    def validate_ai_limit(cls, v: float | None) -> float | None:
        """Validate AI limit is non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError("AI limit must be non-negative")
        return v


class FeatureLimitCreate(FeatureLimitBase):
    """Schema for creating a feature limit."""

    pass


class FeatureLimitUpdate(BaseModel):
    """Schema for updating a feature limit."""

    ai_limit: float | None = Field(None, description="AI usage limit in USD (null = unlimited)")
    storage_limit_bytes: int | None = Field(None, description="Storage limit in bytes", gt=0)
    description: str | None = Field(None, description="Optional description")

    @field_validator("ai_limit")
    @classmethod
    def validate_ai_limit(cls, v: float | None) -> float | None:
        """Validate AI limit is non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError("AI limit must be non-negative")
        return v


class FeatureLimitResponse(BaseModel):
    """Schema for feature limit response."""

    id: UUID = Field(..., description="Limit ID")
    role: str = Field(..., description="User role")
    ai_limit: float | None = Field(None, description="AI usage limit in USD (null = unlimited)")
    storage_limit_bytes: int = Field(..., description="Storage limit in bytes")
    description: str | None = Field(None, description="Optional description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True, "populate_by_name": True}

    @classmethod
    def from_db(cls, db_model: "FeatureLimitDB") -> "FeatureLimitResponse":
        """Convert DB model to response schema."""
        return cls(
            id=db_model.id,
            role=db_model.role,
            ai_limit=(float(db_model.ai_limit) if db_model.ai_limit is not None else None),
            storage_limit_bytes=db_model.storage_limit_bytes,
            description=db_model.description,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )


# Forward reference
from app.modules.feature_limits.db_models import FeatureLimitDB  # noqa: E402

FeatureLimitResponse.model_rebuild()
