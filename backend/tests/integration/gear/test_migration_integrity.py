"""Migration integrity tests for V1 to V2 unified model.

PHASE 4: Migration Testing
These tests verify that the V2 unified model works correctly with nested data.
Tests create data using V2 API and verify correct behavior.

Test Coverage:
- Container nesting works in V2
- Item-container relationships work in V2
- Field mappings correct
- Type-specific fields properly isolated
"""

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models import GearContainerDB, GearItemDB
from app.modules.gear.db_models_v2 import GearItemDBV2
from app.modules.gear.schemas_v2 import GearItemCreateV2
from app.modules.gear.service_v2 import GearServiceV2


class TestMigrationIntegrity:
    """Tests to verify V2 unified model behavior."""

    @pytest.mark.asyncio
    async def test_all_containers_migrated(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
    ) -> None:
        """Verify all V1 containers exist in V2 with itemType='container'."""
        # Get counts
        v1_stmt = select(func.count()).select_from(GearContainerDB).where(GearContainerDB.user_id == test_user.id)
        v1_result = await async_db_session.execute(v1_stmt)
        v1_count = v1_result.scalar()

        v2_stmt = (
            select(func.count())
            .select_from(GearItemDBV2)
            .where(
                GearItemDBV2.user_id == test_user.id,
                GearItemDBV2.item_type == "container",
            )
        )
        v2_result = await async_db_session.execute(v2_stmt)
        v2_count = v2_result.scalar()

        # Assert
        assert v2_count == v1_count, f"Container count mismatch: V1 has {v1_count}, V2 has {v2_count}"

    @pytest.mark.asyncio
    async def test_all_items_migrated(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
    ) -> None:
        """Verify all V1 items exist in V2 with itemType='item'."""
        # Get counts
        v1_stmt = select(func.count()).select_from(GearItemDB).join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id).where(GearContainerDB.user_id == test_user.id)
        v1_result = await async_db_session.execute(v1_stmt)
        v1_count = v1_result.scalar()

        v2_stmt = (
            select(func.count())
            .select_from(GearItemDBV2)
            .where(
                GearItemDBV2.user_id == test_user.id,
                GearItemDBV2.item_type == "item",
            )
        )
        v2_result = await async_db_session.execute(v2_stmt)
        v2_count = v2_result.scalar()

        # Assert
        assert v2_count == v1_count, f"Item count mismatch: V1 has {v1_count}, V2 has {v2_count}"

    @pytest.mark.asyncio
    async def test_total_count_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
    ) -> None:
        """Verify total row count: V2 = V1_containers + V1_items."""
        # Get V1 counts
        v1_containers_stmt = select(func.count()).select_from(GearContainerDB).where(GearContainerDB.user_id == test_user.id)
        v1_containers_result = await async_db_session.execute(v1_containers_stmt)
        v1_containers_count = v1_containers_result.scalar()

        v1_items_stmt = select(func.count()).select_from(GearItemDB).join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id).where(GearContainerDB.user_id == test_user.id)
        v1_items_result = await async_db_session.execute(v1_items_stmt)
        v1_items_count = v1_items_result.scalar()

        # Get V2 count
        v2_stmt = select(func.count()).select_from(GearItemDBV2).where(GearItemDBV2.user_id == test_user.id)
        v2_result = await async_db_session.execute(v2_stmt)
        v2_count = v2_result.scalar()

        expected_count = v1_containers_count + v1_items_count

        # Assert
        assert v2_count == expected_count, f"Total count mismatch: expected {expected_count} " f"({v1_containers_count} containers + {v1_items_count} items), " f"got {v2_count}"

    @pytest.mark.asyncio
    async def test_container_nesting_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify container nesting works in V2: parentItemId."""
        # Arrange: Create nested containers using V2 API
        parent_data = GearItemCreateV2(
            itemType="container",
            name="Parent Container",
            containerType="backpack",
        )
        parent_v2 = await gear_service_v2.create_item(test_user.id, parent_data)

        child_data = GearItemCreateV2(
            itemType="container",
            name="Child Container",
            containerType="pouch",
            parentItemId=parent_v2.id,
        )
        child_v2 = await gear_service_v2.create_item(test_user.id, child_data)

        # Act: Refresh from DB
        await async_db_session.refresh(parent_v2)
        await async_db_session.refresh(child_v2)

        # Assert
        assert parent_v2.parent_item_id is None  # Root container
        assert child_v2.parent_item_id == parent_v2.id  # Nested under parent
        assert parent_v2.item_type == "container"
        assert child_v2.item_type == "container"

    @pytest.mark.asyncio
    async def test_item_container_relationship_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify item-container relationship works in V2: parentItemId."""
        # Arrange: Create container and item using V2 API
        container_data = GearItemCreateV2(
            itemType="container",
            name="Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            quantity=1,
            weight=200,
            weightUnit="g",
            priority="medium",
            status="owned",
            parentItemId=container_v2.id,
        )
        item_v2 = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Refresh from DB
        await async_db_session.refresh(container_v2)
        await async_db_session.refresh(item_v2)

        # Assert
        assert item_v2.parent_item_id == container_v2.id  # Item nested under container
        assert container_v2.item_type == "container"
        assert item_v2.item_type == "item"

    @pytest.mark.asyncio
    async def test_container_fields_mapped_correctly(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify container fields are stored correctly in V2."""
        # Arrange: Create container with all fields using V2 API
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            description="Test Description",
            containerType="backpack",
            color="coyote",
            brand="Mystery Ranch",
            price=450.00,
            weight=1500,
            weightUnit="g",
            maxWeight=20,
            maxWeightUnit="kg",
            isPublic=True,
            favorite=True,
            showItemImages=True,
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Act: Refresh from DB
        await async_db_session.refresh(container_v2)

        # Assert field mappings
        assert container_v2.name == "Test Container"
        assert container_v2.description == "Test Description"
        assert container_v2.container_type == "backpack"
        assert container_v2.color == "coyote"
        assert container_v2.brand == "Mystery Ranch"
        assert container_v2.price == 450.00
        assert container_v2.weight == 1500
        assert container_v2.weight_unit == "g"
        assert container_v2.max_weight == 20
        assert container_v2.max_weight_unit == "kg"
        assert container_v2.is_public is True
        assert container_v2.favorite is True
        assert container_v2.show_item_images is True

    @pytest.mark.asyncio
    async def test_item_fields_mapped_correctly(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify item fields are stored correctly in V2."""
        # Arrange: Create container first
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Create item with all fields using V2 API
        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            quantity=2,
            weight=250,
            weightUnit="g",
            priority="high",
            status="owned",
            quality="high",
            brand="Nalgene",
            price=20.00,
            currency="USD",
            wearable=False,
            consumable=False,
            parentItemId=container_v2.id,
        )
        item_v2 = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Refresh from DB
        await async_db_session.refresh(item_v2)

        # Assert field mappings
        assert item_v2.name == "Water Bottle"
        assert item_v2.category == "water"
        assert item_v2.quantity == 2
        assert item_v2.weight == 250
        assert item_v2.weight_unit == "g"
        assert item_v2.priority == "high"
        assert item_v2.status == "owned"
        assert item_v2.quality == "high"
        assert item_v2.brand == "Nalgene"
        assert item_v2.price == 20.00
        assert item_v2.currency == "USD"
        assert item_v2.wearable is False
        assert item_v2.consumable is False
        assert item_v2.parent_item_id == container_v2.id

    @pytest.mark.asyncio
    async def test_container_has_no_item_fields(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify containers don't have item-specific fields populated."""
        # Arrange: Create container using V2 API
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Act: Refresh from DB
        await async_db_session.refresh(container_v2)

        # Assert item-specific fields are NULL/default for containers
        # Note: Some fields have DB defaults (quantity=1, status='owned', priority='medium')
        # This is acceptable as long as containers don't expose these in API
        assert container_v2.category is None  # Category is the key discriminator
        assert container_v2.quantity is None or container_v2.quantity == 1  # Default
        assert container_v2.status is None or container_v2.status == "owned"  # Default
        assert container_v2.priority is None or container_v2.priority == "medium"  # Default
        assert container_v2.expiration_date is None
        assert container_v2.quality is None
        assert container_v2.wearable is None or container_v2.wearable is False  # Default
        assert container_v2.consumable is None or container_v2.consumable is False  # Default

    @pytest.mark.asyncio
    async def test_item_has_no_container_fields(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify items don't have container-specific fields populated."""
        # Arrange: Create container first
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Create item using V2 API
        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            quantity=1,
            parentItemId=container_v2.id,
        )
        item_v2 = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Refresh from DB
        await async_db_session.refresh(item_v2)

        # Assert container-specific fields are NULL/default for items
        assert item_v2.container_type is None
        assert item_v2.max_weight is None
        assert item_v2.max_weight_unit is None
        assert item_v2.hide_when_nested is None or item_v2.hide_when_nested is False  # Default
        assert item_v2.is_public is None or item_v2.is_public is False  # Default
        assert item_v2.favorite is None or item_v2.favorite is False  # Default
        assert item_v2.show_item_images is None or item_v2.show_item_images is False  # Default
