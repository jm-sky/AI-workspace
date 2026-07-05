"""Pydantic schemas for gear settings endpoints.

This module defines request and response models for the gear settings API,
using camelCase for JSON field names to match frontend conventions.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.gear.schemas import GearWeightUnit


class UserCategory(BaseModel):
    """Schema for a custom category."""

    id: str
    key: str
    label: str
    createdAt: datetime
    updatedAt: datetime

    model_config = {"populate_by_name": True}


class UserContainerType(BaseModel):
    """Schema for a custom container type."""

    id: str
    key: str
    label: str
    createdAt: datetime
    updatedAt: datetime

    model_config = {"populate_by_name": True}


class UserBrand(BaseModel):
    """Schema for a custom brand."""

    id: str
    key: str
    label: str
    createdAt: datetime
    updatedAt: datetime

    model_config = {"populate_by_name": True}


class GearSettingsResponse(BaseModel):
    """Schema for gear settings response."""

    customCategories: list[UserCategory] = Field(
        default_factory=list, alias="customCategories"
    )
    customContainerTypes: list[UserContainerType] = Field(
        default_factory=list, alias="customContainerTypes"
    )
    customBrands: list[UserBrand] = Field(default_factory=list, alias="customBrands")
    preferredWeightUnit: GearWeightUnit | None = Field(
        None, alias="preferredWeightUnit"
    )
    defaultCurrency: str | None = Field(None, alias="defaultCurrency")

    model_config = {"from_attributes": True, "populate_by_name": True}


class GearSettingsUpdate(BaseModel):
    """Schema for updating gear settings."""

    customCategories: list[UserCategory] | None = Field(None, alias="customCategories")
    customContainerTypes: list[UserContainerType] | None = Field(
        None, alias="customContainerTypes"
    )
    customBrands: list[UserBrand] | None = Field(None, alias="customBrands")
    preferredWeightUnit: GearWeightUnit | None = Field(
        None, alias="preferredWeightUnit"
    )
    defaultCurrency: str | None = Field(None, alias="defaultCurrency")

    model_config = {"populate_by_name": True}
