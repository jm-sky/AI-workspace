"""Business logic service for gear settings."""

from typing import Any, cast

from app.modules.gear.schemas import GearWeightUnit

from .db_models import GearSettingsDB
from .repository import GearSettingsRepository
from .schemas import (
    GearSettingsResponse,
    GearSettingsUpdate,
    UserBrand,
    UserCategory,
    UserContainerType,
)


class GearSettingsService:
    """Service for gear settings business logic."""

    def __init__(self, repository: GearSettingsRepository):
        """Initialize service with repository.

        Args:
            repository: Gear settings repository instance
        """
        self.repository = repository

    def _map_to_response(self, settings: GearSettingsDB) -> GearSettingsResponse:
        """Map database model to response schema.

        Args:
            settings: Database settings model

        Returns:
            Settings response schema
        """
        # Convert dict lists to Pydantic models
        custom_categories = [
            UserCategory(**item) for item in settings.custom_categories
        ]
        custom_container_types = [
            UserContainerType(**item) for item in settings.custom_container_types
        ]
        custom_brands = [UserBrand(**item) for item in settings.custom_brands]

        # Convert preferred_weight_unit to GearWeightUnit if not None
        preferred_weight_unit: GearWeightUnit | None = None
        if settings.preferred_weight_unit is not None:
            preferred_weight_unit = cast(GearWeightUnit, settings.preferred_weight_unit)

        return GearSettingsResponse(
            customCategories=custom_categories,
            customContainerTypes=custom_container_types,
            customBrands=custom_brands,
            preferredWeightUnit=preferred_weight_unit,
            defaultCurrency=settings.default_currency,
        )

    async def get_settings(self, user_id: str) -> GearSettingsResponse:
        """Get gear settings for user.

        Args:
            user_id: User ID

        Returns:
            Gear settings response
        """
        settings = await self.repository.get_or_create(user_id)
        return self._map_to_response(settings)

    async def update_settings(
        self, user_id: str, updates: GearSettingsUpdate
    ) -> GearSettingsResponse:
        """Update gear settings for user.

        Args:
            user_id: User ID
            updates: Settings updates

        Returns:
            Updated gear settings response
        """
        settings = await self.repository.get_or_create(user_id)

        if updates.customCategories is not None:
            settings.custom_categories = [
                item.model_dump() for item in updates.customCategories
            ]
        if updates.customContainerTypes is not None:
            settings.custom_container_types = [
                item.model_dump() for item in updates.customContainerTypes
            ]
        if updates.customBrands is not None:
            settings.custom_brands = [
                item.model_dump() for item in updates.customBrands
            ]
        if updates.preferredWeightUnit is not None:
            settings.preferred_weight_unit = updates.preferredWeightUnit
        if updates.defaultCurrency is not None:
            settings.default_currency = updates.defaultCurrency

        updated = await self.repository.update(settings)
        return self._map_to_response(updated)
