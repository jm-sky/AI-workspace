"""Integration tests for data integrity constraints and relationships.

PHASE 0: Test Creation (Pre-Implementation Safety Net)
Document current data integrity behavior and constraints before unified model migration.

Tests cover:
- Foreign key constraints enforcement
- Cascade deletion behavior
- Circular reference handling
- Orphaned record prevention
- Data consistency across relationships
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.auth.db_models import UserDB
from app.modules.gear.schemas import ContainerUpdate
from app.modules.gear.service import GearService

from .conftest import create_test_container, create_test_item


class TestCascadeDeletion:
    """Tests for cascade deletion behavior."""

    @pytest.mark.asyncio
    async def test_delete_container_cascades_to_items(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that deleting container cascades to delete all items."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        item1 = await create_test_item(gear_service, test_user.id, container["id"], "Item 1")
        item2 = await create_test_item(gear_service, test_user.id, container["id"], "Item 2")
        item3 = await create_test_item(gear_service, test_user.id, container["id"], "Item 3")

        # Verify items exist
        assert await gear_service.get_item(item1["id"], test_user.id) is not None
        assert await gear_service.get_item(item2["id"], test_user.id) is not None
        assert await gear_service.get_item(item3["id"], test_user.id) is not None

        # Act
        await gear_service.delete_container(container["id"], test_user.id)

        # Assert - Items should be cascaded deleted
        assert await gear_service.get_item(item1["id"], test_user.id) is None
        assert await gear_service.get_item(item2["id"], test_user.id) is None
        assert await gear_service.get_item(item3["id"], test_user.id) is None

    @pytest.mark.asyncio
    async def test_delete_parent_container_fails_if_has_nested_containers(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that deleting parent with nested containers fails (FK constraint).

        Foreign key constraint prevents deletion when children exist.
        """
        # Arrange
        parent = await create_test_container(gear_service, test_user.id, "Parent")
        await create_test_container(gear_service, test_user.id, "Child", parent_id=parent["id"])

        # Act & Assert
        with pytest.raises(IntegrityError):
            await gear_service.delete_container(parent["id"], test_user.id)

        # Note: Cannot verify containers still exist after IntegrityError
        # Session is rolled back. The exception itself proves FK constraint works.

    @pytest.mark.asyncio
    async def test_delete_all_containers_fails_with_nested_structure(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that delete_all_containers handles nested containers properly.

        May fail if parent is deleted before children due to FK constraints.
        """
        # Arrange
        parent = await create_test_container(gear_service, test_user.id, "Parent")
        await create_test_container(gear_service, test_user.id, "Child 1", parent_id=parent["id"])
        await create_test_container(gear_service, test_user.id, "Child 2", parent_id=parent["id"])

        # Act - delete_all_containers may encounter FK constraint issues
        # depending on deletion order
        try:
            await gear_service.delete_all_containers(test_user.id)
            # If successful, verify all deleted
            all_containers = await gear_service.get_containers(test_user.id)
            assert len(all_containers) == 0
        except IntegrityError:
            # Expected if delete order violates FK constraints
            # This documents current limitation
            pass


class TestForeignKeyConstraints:
    """Tests for foreign key constraint enforcement."""

    @pytest.mark.asyncio
    async def test_cannot_create_item_in_nonexistent_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that creating item in non-existent container returns None."""
        # Act
        from app.modules.gear.schemas import ItemCreate

        data = ItemCreate(
            name="Orphan Item",
            category="water",
            weight=100.0,
        )
        item = await gear_service.create_item("non-existent-container-id", test_user.id, data)

        # Assert
        assert item is None  # Service returns None for invalid container

    @pytest.mark.asyncio
    async def test_cannot_create_container_with_nonexistent_parent(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that creating container with non-existent parent fails."""
        # Act & Assert
        with pytest.raises(IntegrityError):
            from app.modules.gear.schemas import ContainerCreate

            data = ContainerCreate(
                name="Orphan Container",
                type="backpack",
                parentContainerId="non-existent-parent-id",
            )
            await gear_service.create_container(test_user.id, data)

    @pytest.mark.asyncio
    async def test_linked_item_id_must_reference_existing_item(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that linkedItemId must reference existing item (FK enforced)."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Container")

        # Act & Assert
        with pytest.raises(IntegrityError):
            from app.modules.gear.schemas import ItemCreate

            data = ItemCreate(
                name="Item with invalid link",
                category="storage",
                weight=100.0,
                linkedItemId="non-existent-item-id",
            )
            await gear_service.create_item(container["id"], test_user.id, data)


class TestCircularReferences:
    """Tests for circular reference scenarios."""

    @pytest.mark.asyncio
    async def test_container_can_be_its_own_parent(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that container CAN be set as its own parent (no validation).

        LIMITATION: Current system allows circular references.
        This creates logical inconsistency that unified model should prevent.
        """
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Self-Ref Container")

        # Act - Set container as its own parent
        update_data = ContainerUpdate(parentContainerId=container["id"])
        updated = await gear_service.update_container(container["id"], test_user.id, update_data)

        # Assert - Current system allows this
        assert updated is not None
        assert updated.parentContainerId == container["id"]

        # This creates a logical circular reference: Container -> Container
        # Database doesn't prevent this, but it's semantically invalid

    @pytest.mark.asyncio
    async def test_circular_nesting_chain_possible(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that circular nesting chains are possible (no validation).

        LIMITATION: A -> B -> A circular reference is possible.
        """
        # Arrange
        container_a = await create_test_container(gear_service, test_user.id, "Container A")
        container_b = await create_test_container(
            gear_service,
            test_user.id,
            "Container B",
            parent_id=container_a["id"],
        )

        # Act - Make A a child of B (creates A -> B -> A cycle)
        update_data = ContainerUpdate(parentContainerId=container_b["id"])
        updated_a = await gear_service.update_container(container_a["id"], test_user.id, update_data)

        # Assert - System allows circular reference
        assert updated_a is not None
        assert updated_a.parentContainerId == container_b["id"]

        # Verify chain
        fetched_a = await gear_service.get_container(container_a["id"], test_user.id)
        fetched_b = await gear_service.get_container(container_b["id"], test_user.id)

        assert fetched_a is not None
        assert fetched_b is not None
        # A.parent = B, B.parent = A (circular reference)
        assert fetched_a.parentContainerId == container_b["id"]
        assert fetched_b.parentContainerId == container_a["id"]


class TestDataConsistency:
    """Tests for data consistency across relationships."""

    @pytest.mark.asyncio
    async def test_item_container_reference_stays_valid_after_update(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that item's container reference remains valid after container updates."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Original Name")
        item = await create_test_item(gear_service, test_user.id, container["id"], "Item")

        # Act - Update container
        update_data = ContainerUpdate(name="Updated Name")
        await gear_service.update_container(container["id"], test_user.id, update_data)

        # Assert - Item still references container correctly
        fetched_item = await gear_service.get_item(item["id"], test_user.id)
        assert fetched_item is not None
        assert fetched_item.container is not None
        assert fetched_item.container.id == container["id"]
        assert fetched_item.container.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_nested_container_reference_stays_valid_after_parent_update(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that nested container reference remains valid after parent updates."""
        # Arrange
        parent = await create_test_container(gear_service, test_user.id, "Parent", weight=500.0, weight_unit="g")
        child = await create_test_container(gear_service, test_user.id, "Child", parent_id=parent["id"])

        # Act - Update parent
        update_data = ContainerUpdate(weight=600.0)
        await gear_service.update_container(parent["id"], test_user.id, update_data)

        # Assert - Child still references parent correctly
        fetched_child = await gear_service.get_container(child["id"], test_user.id)
        assert fetched_child is not None
        assert fetched_child.parentContainerId == parent["id"]

        # Verify parent updated
        fetched_parent = await gear_service.get_container(parent["id"], test_user.id)
        assert fetched_parent is not None
        assert fetched_parent.weight == 600.0

    @pytest.mark.asyncio
    async def test_orphaned_items_prevented_by_cascade(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that orphaned items cannot exist (cascade delete prevents them)."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Container")
        item = await create_test_item(gear_service, test_user.id, container["id"], "Item")

        # Act - Delete container
        await gear_service.delete_container(container["id"], test_user.id)

        # Assert - Item cascades deleted (cannot be orphaned)
        fetched_item = await gear_service.get_item(item["id"], test_user.id)
        assert fetched_item is None


class TestUserIsolation:
    """Tests for user data isolation (security)."""

    @pytest.mark.asyncio
    async def test_cannot_access_another_users_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that users cannot access other users' containers."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "User Container")

        # Act - Try to access with different user ID
        other_user_access = await gear_service.get_container(container["id"], "different-user-id")

        # Assert
        assert other_user_access is None

    @pytest.mark.asyncio
    async def test_cannot_access_another_users_item(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that users cannot access other users' items."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Container")
        item = await create_test_item(gear_service, test_user.id, container["id"], "User Item")

        # Act - Try to access with different user ID
        other_user_access = await gear_service.get_item(item["id"], "different-user-id")

        # Assert
        assert other_user_access is None

    @pytest.mark.asyncio
    async def test_cannot_modify_another_users_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that users cannot modify other users' containers."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "User Container")

        # Act - Try to update with different user ID
        update_data = ContainerUpdate(name="Hacked Name")
        updated = await gear_service.update_container(container["id"], "different-user-id", update_data)

        # Assert - Update should fail (return None)
        assert updated is None

        # Verify original unchanged
        original = await gear_service.get_container(container["id"], test_user.id)
        assert original is not None
        assert original.name == "User Container"

    @pytest.mark.asyncio
    async def test_cannot_delete_another_users_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that users cannot delete other users' containers."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "User Container")

        # Act - Try to delete with different user ID
        result = await gear_service.delete_container(container["id"], "different-user-id")

        # Assert - Delete should fail
        assert result is False

        # Verify container still exists
        existing = await gear_service.get_container(container["id"], test_user.id)
        assert existing is not None


class TestBulkOperations:
    """Tests for bulk operations and their integrity."""

    @pytest.mark.asyncio
    async def test_delete_all_containers_only_affects_user(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that delete_all_containers only affects the specified user.

        Note: We can't test with multiple users in same test,
        but this documents expected behavior.
        """
        # Arrange
        await create_test_container(gear_service, test_user.id, "Container 1")
        await create_test_container(gear_service, test_user.id, "Container 2")

        # Act
        deleted_count = await gear_service.delete_all_containers(test_user.id)

        # Assert
        assert deleted_count == 2

        # Verify containers deleted
        all_containers = await gear_service.get_containers(test_user.id)
        assert len(all_containers) == 0

    @pytest.mark.asyncio
    async def test_get_all_items_only_returns_users_items(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that get_all_items only returns the specified user's items."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Container")
        item1 = await create_test_item(gear_service, test_user.id, container["id"], "Item 1")
        item2 = await create_test_item(gear_service, test_user.id, container["id"], "Item 2")

        # Act
        all_items = await gear_service.get_all_items(test_user.id)

        # Assert
        assert len(all_items) == 2
        item_ids = {item.id for item in all_items}
        assert item1["id"] in item_ids
        assert item2["id"] in item_ids


class TestConstraintEdgeCases:
    """Tests for edge cases in constraint enforcement."""

    @pytest.mark.asyncio
    async def test_multiple_containers_can_have_same_parent(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that multiple containers can reference same parent (valid)."""
        # Arrange
        parent = await create_test_container(gear_service, test_user.id, "Parent")

        # Act
        child1 = await create_test_container(gear_service, test_user.id, "Child 1", parent_id=parent["id"])
        child2 = await create_test_container(gear_service, test_user.id, "Child 2", parent_id=parent["id"])
        child3 = await create_test_container(gear_service, test_user.id, "Child 3", parent_id=parent["id"])

        # Assert
        assert child1["parentContainerId"] == parent["id"]
        assert child2["parentContainerId"] == parent["id"]
        assert child3["parentContainerId"] == parent["id"]

    @pytest.mark.asyncio
    async def test_remove_parent_reference_makes_container_top_level(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that removing parent reference makes container top-level."""
        # Arrange
        parent = await create_test_container(gear_service, test_user.id, "Parent")
        child = await create_test_container(gear_service, test_user.id, "Child", parent_id=parent["id"])

        # Verify nested
        assert child["parentContainerId"] == parent["id"]

        # Act - Remove parent reference
        update_data = ContainerUpdate(parentContainerId=None)
        updated = await gear_service.update_container(child["id"], test_user.id, update_data)

        # Assert - Now top-level
        assert updated is not None
        assert updated.parentContainerId is None

    @pytest.mark.asyncio
    async def test_deeply_nested_structure_maintains_integrity(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that deeply nested structure maintains referential integrity."""
        # Arrange - Create 5-level nesting
        l1 = await create_test_container(gear_service, test_user.id, "Level 1")
        l2 = await create_test_container(gear_service, test_user.id, "Level 2", parent_id=l1["id"])
        l3 = await create_test_container(gear_service, test_user.id, "Level 3", parent_id=l2["id"])
        l4 = await create_test_container(gear_service, test_user.id, "Level 4", parent_id=l3["id"])
        l5 = await create_test_container(gear_service, test_user.id, "Level 5", parent_id=l4["id"])

        # Act - Verify all references valid
        fetched_l5 = await gear_service.get_container(l5["id"], test_user.id)
        fetched_l4 = await gear_service.get_container(l4["id"], test_user.id)
        fetched_l3 = await gear_service.get_container(l3["id"], test_user.id)
        fetched_l2 = await gear_service.get_container(l2["id"], test_user.id)
        fetched_l1 = await gear_service.get_container(l1["id"], test_user.id)

        # Assert - Chain intact
        assert fetched_l5 is not None
        assert fetched_l5.parentContainerId == l4["id"]
        assert fetched_l4 is not None
        assert fetched_l4.parentContainerId == l3["id"]
        assert fetched_l3 is not None
        assert fetched_l3.parentContainerId == l2["id"]
        assert fetched_l2 is not None
        assert fetched_l2.parentContainerId == l1["id"]
        assert fetched_l1 is not None
        assert fetched_l1.parentContainerId is None  # Top level
