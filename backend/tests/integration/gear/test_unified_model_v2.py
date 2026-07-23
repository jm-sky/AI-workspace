"""Integration tests for unified gear model (V2).

PHASE 4: Testing
These tests verify the unified model where containers are items with item_type='container'.

Test Coverage:
- CRUD operations for containers (itemType='container')
- CRUD operations for items (itemType='item')
- Nesting relationships (parentItemId)
- Batch order updates
- Move item operations
- Filters and queries
"""

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models_v2 import GearItemDBV2
from app.modules.gear.repository_v2 import GearRepositoryV2
from app.modules.gear.schemas_v2 import GearItemCreateV2, GearItemUpdateV2
from app.modules.gear.service_v2 import GearServiceV2


@pytest_asyncio.fixture
async def gear_repository_v2(async_db_session: AsyncSession) -> GearRepositoryV2:
    """Fixture to create GearRepositoryV2 instance."""
    return GearRepositoryV2(async_db_session)


@pytest_asyncio.fixture
async def gear_service_v2(gear_repository_v2: GearRepositoryV2) -> GearServiceV2:
    """Fixture to create GearServiceV2 instance."""
    return GearServiceV2(gear_repository_v2)


async def get_item_count(db: AsyncSession, user_id: str, item_type: str | None = None) -> int:
    """Helper to get item count for a user."""
    stmt = select(GearItemDBV2).where(GearItemDBV2.user_id == user_id)
    if item_type:
        stmt = stmt.where(GearItemDBV2.item_type == item_type)
    result = await db.execute(stmt)
    return len(result.scalars().all())


class TestContainerCreateV2:
    """Tests for creating containers in unified model."""

    @pytest.mark.asyncio
    async def test_create_container_minimal(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test creating a container with minimal required fields."""
        # Arrange
        data = GearItemCreateV2(
            itemType="container",
            name="Bug-out Bag",
            containerType="backpack",
        )

        # Act
        item = await gear_service_v2.create_item(test_user.id, data)

        # Assert
        assert item.id is not None
        assert item.item_type == "container"
        assert item.name == "Bug-out Bag"
        assert item.container_type == "backpack"
        assert item.parent_item_id is None
        # Container should have category as None (item-specific field)
        assert item.category is None
        assert await get_item_count(async_db_session, test_user.id, "container") == 1

    @pytest.mark.asyncio
    async def test_create_container_full_data(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test creating a container with all fields populated."""
        # Arrange
        data = GearItemCreateV2(
            itemType="container",
            name="Premium Backpack",
            containerType="backpack",
            description="High-quality tactical backpack",
            brand="Mystery Ranch",
            price=450.00,
            currency="USD",
            weight=1500,
            weightUnit="g",
            maxWeight=20,
            maxWeightUnit="kg",
            color="coyote",
            isPublic=False,
            favorite=True,
            showItemImages=True,
        )

        # Act
        item = await gear_service_v2.create_item(test_user.id, data)

        # Assert
        assert item.name == "Premium Backpack"
        assert item.container_type == "backpack"
        assert item.description == "High-quality tactical backpack"
        assert item.brand == "Mystery Ranch"
        assert item.price == 450.00
        assert item.currency == "USD"
        assert item.weight == 1500
        assert item.weight_unit == "g"
        assert item.max_weight == 20
        assert item.max_weight_unit == "kg"
        assert item.color == "coyote"
        assert item.is_public is False
        assert item.favorite is True
        assert item.show_item_images is True

    @pytest.mark.asyncio
    async def test_create_nested_container(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test creating a nested container (container inside container)."""
        # Arrange: Create parent container
        parent_data = GearItemCreateV2(
            itemType="container",
            name="Main Backpack",
            containerType="backpack",
        )
        parent = await gear_service_v2.create_item(test_user.id, parent_data)

        # Act: Create nested container
        nested_data = GearItemCreateV2(
            itemType="container",
            name="First Aid Pouch",
            containerType="pouch",
            parentItemId=parent.id,
        )
        nested = await gear_service_v2.create_item(test_user.id, nested_data)

        # Assert
        assert nested.parent_item_id == parent.id
        assert nested.item_type == "container"
        assert nested.container_type == "pouch"

    @pytest.mark.asyncio
    async def test_create_container_validation_error(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test that validation prevents invalid container creation."""
        # Arrange: Try to create container without containerType
        # This should be caught by Pydantic validation
        with pytest.raises(ValidationError):
            GearItemCreateV2(
                itemType="container",
                name="Invalid Container",
                # Missing containerType - should raise validation error
            )


class TestItemCreateV2:
    """Tests for creating items in unified model."""

    @pytest.mark.asyncio
    async def test_create_item_minimal(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test creating an item with minimal required fields."""
        # Arrange: Create parent container first
        container_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        # Act: Create item
        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
        )
        item = await gear_service_v2.create_item(test_user.id, item_data)

        # Assert
        assert item.id is not None
        assert item.item_type == "item"
        assert item.name == "Water Bottle"
        assert item.category == "water"
        assert item.parent_item_id == container.id
        # Item should have container_type as None (container-specific field)
        assert item.container_type is None
        assert await get_item_count(async_db_session, test_user.id, "item") == 1

    @pytest.mark.asyncio
    async def test_create_item_full_data(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test creating an item with all fields populated."""
        # Arrange: Create parent container
        container_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        # Act: Create item with all fields
        item_data = GearItemCreateV2(
            itemType="item",
            name="Nalgene Water Bottle",
            category="water",
            parentItemId=container.id,
            description="1L wide-mouth bottle",
            brand="Nalgene",
            price=12.99,
            currency="USD",
            weight=175,
            weightUnit="g",
            quantity=1,
            status="owned",
            priority="high",
            quality="high",
            wearable=False,
            consumable=False,
            orderIndex=0,
        )
        item = await gear_service_v2.create_item(test_user.id, item_data)

        # Assert
        assert item.name == "Nalgene Water Bottle"
        assert item.category == "water"
        assert item.description == "1L wide-mouth bottle"
        assert item.brand == "Nalgene"
        assert item.price == 12.99
        assert item.currency == "USD"
        assert item.weight == 175
        assert item.weight_unit == "g"
        assert item.quantity == 1
        assert item.status == "owned"
        assert item.priority == "high"
        assert item.quality == "high"
        assert item.wearable is False
        assert item.consumable is False
        assert item.order_index == 0


class TestReadOperationsV2:
    """Tests for reading items in unified model."""

    @pytest.mark.asyncio
    async def test_get_all_items(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test getting all items (containers + items)."""
        # Arrange: Create container and items
        container_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item1_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
        )
        await gear_service_v2.create_item(test_user.id, item1_data)

        item2_data = GearItemCreateV2(
            itemType="item",
            name="First Aid Kit",
            category="firstAid",
            parentItemId=container.id,
        )
        await gear_service_v2.create_item(test_user.id, item2_data)

        # Act
        all_items = await gear_service_v2.get_items(test_user.id)

        # Assert
        assert len(all_items) == 3  # 1 container + 2 items

    @pytest.mark.asyncio
    async def test_get_containers_only(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test getting only containers."""
        # Arrange
        container1_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        await gear_service_v2.create_item(test_user.id, container1_data)

        container2_data = GearItemCreateV2(
            itemType="container",
            name="Pouch",
            containerType="pouch",
        )
        await gear_service_v2.create_item(test_user.id, container2_data)

        # Act
        containers = await gear_service_v2.get_items(test_user.id, item_type="container")

        # Assert
        assert len(containers) == 2
        assert all(item.item_type == "container" for item in containers)

    @pytest.mark.asyncio
    async def test_get_items_only(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test getting only regular items."""
        # Arrange
        container_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
        )
        await gear_service_v2.create_item(test_user.id, item_data)

        # Act
        items = await gear_service_v2.get_items(test_user.id, item_type="item")

        # Assert
        assert len(items) == 1
        assert all(item.item_type == "item" for item in items)

    @pytest.mark.asyncio
    async def test_get_children(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test getting children of a parent item."""
        # Arrange: Create parent container with items
        container_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item1_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
        )
        await gear_service_v2.create_item(test_user.id, item1_data)

        item2_data = GearItemCreateV2(
            itemType="item",
            name="First Aid Kit",
            category="firstAid",
            parentItemId=container.id,
        )
        await gear_service_v2.create_item(test_user.id, item2_data)

        # Act
        children = await gear_service_v2.get_children(container.id, test_user.id)

        # Assert
        assert len(children) == 2
        assert all(child.parent_item_id == container.id for child in children)


class TestUpdateOperationsV2:
    """Tests for updating items in unified model."""

    @pytest.mark.asyncio
    async def test_update_container(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test updating a container."""
        # Arrange: Create container
        create_data = GearItemCreateV2(
            itemType="container",
            name="Old Name",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, create_data)

        # Act: Update container
        update_data = GearItemUpdateV2(
            name="New Name",
            favorite=True,
        )
        updated = await gear_service_v2.update_item(container.id, test_user.id, update_data)

        # Assert
        assert updated.name == "New Name"
        assert updated.favorite is True
        assert updated.container_type == "backpack"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_item(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test updating an item."""
        # Arrange: Create container and item
        container_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
            status="owned",
        )
        item = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Update item
        update_data = GearItemUpdateV2(
            status="missing",
            priority="critical",
        )
        updated = await gear_service_v2.update_item(item.id, test_user.id, update_data)

        # Assert
        assert updated.status == "missing"
        assert updated.priority == "critical"
        assert updated.name == "Water Bottle"  # Unchanged

    @pytest.mark.asyncio
    async def test_batch_update_order(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test batch updating order_index for multiple items."""
        # Arrange: Create container with items
        container_data = GearItemCreateV2(
            itemType="container",
            name="Backpack",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item1_data = GearItemCreateV2(
            itemType="item",
            name="Item 1",
            category="water",
            parentItemId=container.id,
            orderIndex=0,
        )
        item1 = await gear_service_v2.create_item(test_user.id, item1_data)

        item2_data = GearItemCreateV2(
            itemType="item",
            name="Item 2",
            category="food",
            parentItemId=container.id,
            orderIndex=1,
        )
        item2 = await gear_service_v2.create_item(test_user.id, item2_data)

        # Act: Swap order
        batch_updates = [
            {"id": item1.id, "orderIndex": 1},
            {"id": item2.id, "orderIndex": 0},
        ]
        updated_items = await gear_service_v2.batch_update_order(batch_updates, test_user.id)

        # Assert
        assert len(updated_items) == 2
        item1_updated = next(i for i in updated_items if i.id == item1.id)
        item2_updated = next(i for i in updated_items if i.id == item2.id)
        assert item1_updated.order_index == 1
        assert item2_updated.order_index == 0


class TestMoveOperationsV2:
    """Tests for moving items between containers."""

    @pytest.mark.asyncio
    async def test_move_item_to_different_container(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test moving an item to a different container."""
        # Arrange: Create two containers and an item
        container1_data = GearItemCreateV2(
            itemType="container",
            name="Container 1",
            containerType="backpack",
        )
        container1 = await gear_service_v2.create_item(test_user.id, container1_data)

        container2_data = GearItemCreateV2(
            itemType="container",
            name="Container 2",
            containerType="pouch",
        )
        container2 = await gear_service_v2.create_item(test_user.id, container2_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container1.id,
        )
        item = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Move item to container2
        moved = await gear_service_v2.move_item(item.id, test_user.id, container2.id)

        # Assert
        assert moved.parent_item_id == container2.id
        assert moved.id == item.id
        assert moved.name == "Water Bottle"

    @pytest.mark.asyncio
    async def test_move_item_to_root(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test moving an item to root (no parent)."""
        # Arrange: Create container and item
        container_data = GearItemCreateV2(
            itemType="container",
            name="Container",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
        )
        item = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Move item to root
        moved = await gear_service_v2.move_item(item.id, test_user.id, None)

        # Assert
        assert moved.parent_item_id is None

    @pytest.mark.asyncio
    async def test_move_to_invalid_target_fails(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
    ) -> None:
        """Test that moving to non-existent target fails."""
        # Arrange: Create container and item
        container_data = GearItemCreateV2(
            itemType="container",
            name="Container",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
        )
        item = await gear_service_v2.create_item(test_user.id, item_data)

        # Act & Assert: Move to non-existent container
        with pytest.raises(ValueError, match="Target parent not found"):
            await gear_service_v2.move_item(item.id, test_user.id, "non-existent-id")


class TestDeleteOperationsV2:
    """Tests for deleting items in unified model."""

    @pytest.mark.asyncio
    async def test_delete_item(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test deleting an item."""
        # Arrange: Create container and item
        container_data = GearItemCreateV2(
            itemType="container",
            name="Container",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            parentItemId=container.id,
        )
        item = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Delete item
        deleted = await gear_service_v2.delete_item(item.id, test_user.id)

        # Assert
        assert deleted is True
        assert await get_item_count(async_db_session, test_user.id, "item") == 0

    @pytest.mark.asyncio
    async def test_delete_container_cascades_to_children(
        self,
        gear_service_v2: GearServiceV2,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test that deleting a container also deletes its children."""
        # Arrange: Create container with items
        container_data = GearItemCreateV2(
            itemType="container",
            name="Container",
            containerType="backpack",
        )
        container = await gear_service_v2.create_item(test_user.id, container_data)

        item1_data = GearItemCreateV2(
            itemType="item",
            name="Item 1",
            category="water",
            parentItemId=container.id,
        )
        await gear_service_v2.create_item(test_user.id, item1_data)

        item2_data = GearItemCreateV2(
            itemType="item",
            name="Item 2",
            category="food",
            parentItemId=container.id,
        )
        await gear_service_v2.create_item(test_user.id, item2_data)

        # Act: Delete container
        deleted = await gear_service_v2.delete_item(container.id, test_user.id)

        # Assert
        assert deleted is True
        assert await get_item_count(async_db_session, test_user.id) == 0  # All deleted
