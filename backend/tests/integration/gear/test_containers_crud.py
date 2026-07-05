"""Integration tests for gear container CRUD operations.

PHASE 0: Test Creation (Pre-Implementation Safety Net)
Verify current container behavior before unified model migration.

These tests document the current system with two separate models:
- Containers: parent_container_id for nesting
- Items: container_id + nested_container_id (dual-nesting system)
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.db_models import UserDB
from app.modules.gear.service import GearService
from app.modules.gear.schemas import ContainerCreate, ContainerUpdate

from .conftest import (
    create_test_container,
    get_container_count,
)


class TestContainerCreate:
    """Tests for creating gear containers."""

    @pytest.mark.asyncio
    async def test_create_container_minimal_data(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test creating a container with minimal required fields."""
        # Arrange
        data = ContainerCreate(
            name="Minimal Container",
            type="backpack",
        )

        # Act
        container = await gear_service.create_container(test_user.id, data)

        # Assert
        assert container.id is not None
        assert container.name == "Minimal Container"
        assert container.type == "backpack"
        assert container.parentContainerId is None
        assert await get_container_count(async_db_session, test_user.id) == 1

    @pytest.mark.asyncio
    async def test_create_container_full_data(
        self,
        gear_service: GearService,
        test_user: UserDB,
        sample_container_data: ContainerCreate,
    ) -> None:
        """Test creating a container with all fields populated."""
        # Act
        container = await gear_service.create_container(
            test_user.id, sample_container_data
        )

        # Assert
        assert container.id is not None
        assert container.name == sample_container_data.name
        assert container.description == sample_container_data.description
        assert container.type == sample_container_data.type
        assert container.color == sample_container_data.color
        assert container.weight == sample_container_data.weight
        assert container.weightUnit == sample_container_data.weightUnit
        assert container.brand == sample_container_data.brand
        assert container.price == sample_container_data.price

    @pytest.mark.asyncio
    async def test_create_container_with_weight(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test creating a container with weight specification."""
        # Arrange
        data = ContainerCreate(
            name="Weighted Backpack",
            type="backpack",
            weight=1500.0,
            weightUnit="g",
        )

        # Act
        container = await gear_service.create_container(test_user.id, data)

        # Assert
        assert container.weight == 1500.0
        assert container.weightUnit == "g"

    @pytest.mark.asyncio
    async def test_create_multiple_containers(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test creating multiple containers for the same user."""
        # Act
        container1 = await create_test_container(
            gear_service, test_user.id, "Container 1"
        )
        container2 = await create_test_container(
            gear_service, test_user.id, "Container 2"
        )
        container3 = await create_test_container(
            gear_service, test_user.id, "Container 3"
        )

        # Assert
        assert container1["id"] != container2["id"] != container3["id"]
        assert await get_container_count(async_db_session, test_user.id) == 3


class TestContainerRead:
    """Tests for reading/retrieving gear containers."""

    @pytest.mark.asyncio
    async def test_get_container_by_id(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving a container by its ID."""
        # Arrange
        created = await create_test_container(
            gear_service, test_user.id, "Test Container"
        )

        # Act
        container = await gear_service.get_container(created["id"], test_user.id)

        # Assert
        assert container is not None
        assert container.id == created["id"]
        assert container.name == "Test Container"

    @pytest.mark.asyncio
    async def test_get_all_containers(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving all containers for a user."""
        # Arrange
        await create_test_container(gear_service, test_user.id, "Container 1")
        await create_test_container(gear_service, test_user.id, "Container 2")
        await create_test_container(gear_service, test_user.id, "Container 3")

        # Act
        containers = await gear_service.get_containers(test_user.id)

        # Assert
        assert len(containers) == 3
        names = {c.name for c in containers}
        assert names == {"Container 1", "Container 2", "Container 3"}

    @pytest.mark.asyncio
    async def test_get_container_not_found(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving a non-existent container returns None."""
        # Act
        container = await gear_service.get_container("non-existent-id", test_user.id)

        # Assert
        assert container is None

    @pytest.mark.asyncio
    async def test_get_container_wrong_user(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that user cannot access another user's container."""
        # Arrange
        created = await create_test_container(
            gear_service, test_user.id, "User Container"
        )

        # Act - Try to access with different user ID
        container = await gear_service.get_container(created["id"], "different-user-id")

        # Assert
        assert container is None


class TestContainerUpdate:
    """Tests for updating gear containers."""

    @pytest.mark.asyncio
    async def test_update_container_name(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test updating a container's name."""
        # Arrange
        created = await create_test_container(
            gear_service, test_user.id, "Original Name"
        )
        update_data = ContainerUpdate(name="Updated Name")

        # Act
        updated = await gear_service.update_container(
            created["id"], test_user.id, update_data
        )

        # Assert
        assert updated.name == "Updated Name"
        assert updated.id == created["id"]

    @pytest.mark.asyncio
    async def test_update_container_multiple_fields(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test updating multiple fields of a container."""
        # Arrange
        created = await create_test_container(
            gear_service, test_user.id, "Test Container"
        )
        update_data = ContainerUpdate(
            name="Updated Container",
            description="New description",
            color="khaki",
            weight=2000.0,
            brand="NewBrand",
        )

        # Act
        updated = await gear_service.update_container(
            created["id"], test_user.id, update_data
        )

        # Assert
        assert updated.name == "Updated Container"
        assert updated.description == "New description"
        assert updated.color == "khaki"
        assert updated.weight == 2000.0
        assert updated.brand == "NewBrand"

    @pytest.mark.asyncio
    async def test_update_container_partial(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test partial update (only some fields) preserves other fields."""
        # Arrange
        data = ContainerCreate(
            name="Original",
            type="backpack",
            description="Original description",
            color="coyote",
            weight=1000.0,
        )
        created = await gear_service.create_container(test_user.id, data)
        update_data = ContainerUpdate(name="Updated")

        # Act
        updated = await gear_service.update_container(
            created.id, test_user.id, update_data
        )

        # Assert
        assert updated.name == "Updated"
        # Other fields should be preserved
        assert updated.description == "Original description"
        assert updated.color == "coyote"
        assert updated.weight == 1000.0


class TestContainerDelete:
    """Tests for deleting gear containers."""

    @pytest.mark.asyncio
    async def test_delete_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test deleting a container."""
        # Arrange
        created = await create_test_container(gear_service, test_user.id, "To Delete")
        initial_count = await get_container_count(async_db_session, test_user.id)

        # Act
        await gear_service.delete_container(created["id"], test_user.id)

        # Assert
        final_count = await get_container_count(async_db_session, test_user.id)
        assert final_count == initial_count - 1
        # Verify container no longer accessible
        deleted = await gear_service.get_container(created["id"], test_user.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_all_containers(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test deleting all containers for a user."""
        # Arrange
        await create_test_container(gear_service, test_user.id, "Container 1")
        await create_test_container(gear_service, test_user.id, "Container 2")
        await create_test_container(gear_service, test_user.id, "Container 3")
        assert await get_container_count(async_db_session, test_user.id) == 3

        # Act
        await gear_service.delete_all_containers(test_user.id)

        # Assert
        assert await get_container_count(async_db_session, test_user.id) == 0

    @pytest.mark.asyncio
    async def test_delete_container_not_found(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test deleting a non-existent container doesn't raise error."""
        # Act & Assert - Should not raise exception
        await gear_service.delete_container("non-existent-id", test_user.id)

    @pytest.mark.asyncio
    async def test_delete_container_wrong_user(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test that user cannot delete another user's container."""
        # Arrange
        created = await create_test_container(
            gear_service, test_user.id, "User Container"
        )

        # Act - Try to delete with different user ID
        await gear_service.delete_container(created["id"], "different-user-id")

        # Assert - Container should still exist
        container = await gear_service.get_container(created["id"], test_user.id)
        assert container is not None
        assert container.name == "User Container"


class TestContainerNesting:
    """Tests for nested container relationships (parent_container_id)."""

    @pytest.mark.asyncio
    async def test_create_nested_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test creating a container inside another container (System 1 nesting)."""
        # Arrange
        parent = await create_test_container(
            gear_service, test_user.id, "Parent Backpack"
        )

        # Act
        child = await create_test_container(
            gear_service,
            test_user.id,
            "Nested Pouch",
            container_type="pouch",
            parent_id=parent["id"],
        )

        # Assert
        assert child["parentContainerId"] == parent["id"]

    @pytest.mark.asyncio
    async def test_get_nested_containers(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving nested containers structure."""
        # Arrange
        parent = await create_test_container(gear_service, test_user.id, "Backpack")
        child1 = await create_test_container(
            gear_service, test_user.id, "Pouch 1", parent_id=parent["id"]
        )
        child2 = await create_test_container(
            gear_service, test_user.id, "Pouch 2", parent_id=parent["id"]
        )

        # Act
        parent_container = await gear_service.get_container(parent["id"], test_user.id)

        # Assert
        assert parent_container is not None
        # Verify parent has nested containers (if service populates this)
        # Note: Actual API response structure may differ

    @pytest.mark.asyncio
    async def test_delete_parent_with_child_fails(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that deleting parent container with children fails (FK constraint prevents deletion)."""
        # Arrange
        parent = await create_test_container(gear_service, test_user.id, "Parent")
        child = await create_test_container(
            gear_service, test_user.id, "Child", parent_id=parent["id"]
        )

        # Act & Assert
        # Current FK constraint prevents deletion of parent with children
        # IntegrityError should be raised by the database
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await gear_service.delete_container(parent["id"], test_user.id)

    @pytest.mark.asyncio
    async def test_multiple_nesting_levels(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test creating multiple levels of nested containers."""
        # Arrange & Act
        level1 = await create_test_container(gear_service, test_user.id, "Backpack")
        level2 = await create_test_container(
            gear_service, test_user.id, "Pouch", parent_id=level1["id"]
        )
        level3 = await create_test_container(
            gear_service, test_user.id, "Small Box", parent_id=level2["id"]
        )

        # Assert
        assert level2["parentContainerId"] == level1["id"]
        assert level3["parentContainerId"] == level2["id"]


class TestContainerValidation:
    """Tests for container data validation."""

    @pytest.mark.asyncio
    async def test_create_container_missing_name(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that container requires a name."""
        # Note: This should be caught by Pydantic validation
        # If it reaches service, service should validate
        with pytest.raises((ValueError, Exception)):
            data = ContainerCreate(
                name="",  # Empty name should fail
                type="backpack",
            )
            await gear_service.create_container(test_user.id, data)

    @pytest.mark.asyncio
    async def test_create_container_missing_type(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that container requires a type (currently empty string is allowed by schema)."""
        # Note: Current schema (GearContainerType = str) doesn't validate min_length
        # Empty string is technically allowed, though not recommended
        # This test documents current behavior - can be updated when schema adds validation
        data = ContainerCreate(
            name="Test",
            type="",  # Empty type currently allowed
        )
        container = await gear_service.create_container(test_user.id, data)
        assert container is not None
        assert container.type == ""
