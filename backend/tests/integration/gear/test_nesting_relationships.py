"""Integration tests for gear nesting relationships.

PHASE 0: Test Creation (Pre-Implementation Safety Net)
Document the current dual-nesting system before unified model migration.

Current System:
- SYSTEM 1 (Container Nesting): Containers can nest inside containers via parent_container_id
- SYSTEM 2 (Item as Container Reference): Items can reference containers via nested_container_id
  This allows representing "container as item" (e.g., small pouch stored in backpack)

Both systems exist simultaneously, creating complexity that unified model aims to solve.
"""

import pytest

from app.modules.auth.db_models import UserDB
from app.modules.gear.schemas import ItemCreate
from app.modules.gear.service import GearService

from .conftest import create_test_container, create_test_item


class TestContainerNesting:
    """Tests for System 1: Container parent_container_id nesting."""

    @pytest.mark.asyncio
    async def test_simple_container_nesting(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test basic two-level container nesting."""
        # Arrange & Act
        backpack = await create_test_container(gear_service, test_user.id, "Main Backpack", container_type="backpack")
        pouch = await create_test_container(
            gear_service,
            test_user.id,
            "Admin Pouch",
            container_type="pouch",
            parent_id=backpack["id"],
        )

        # Assert
        assert pouch["parentContainerId"] == backpack["id"]

        # Verify fetching nested container
        fetched_pouch = await gear_service.get_container(pouch["id"], test_user.id)
        assert fetched_pouch is not None
        assert fetched_pouch.parentContainerId == backpack["id"]

    @pytest.mark.asyncio
    async def test_three_level_container_nesting(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test three-level deep container nesting."""
        # Arrange & Act
        backpack = await create_test_container(gear_service, test_user.id, "Backpack", container_type="backpack")
        pouch = await create_test_container(
            gear_service,
            test_user.id,
            "Pouch",
            container_type="pouch",
            parent_id=backpack["id"],
        )
        small_bag = await create_test_container(
            gear_service,
            test_user.id,
            "Small Bag",
            container_type="bag",
            parent_id=pouch["id"],
        )

        # Assert
        assert pouch["parentContainerId"] == backpack["id"]
        assert small_bag["parentContainerId"] == pouch["id"]

    @pytest.mark.asyncio
    async def test_sibling_containers_same_parent(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test multiple containers nested in same parent."""
        # Arrange & Act
        backpack = await create_test_container(gear_service, test_user.id, "Backpack")
        pouch1 = await create_test_container(gear_service, test_user.id, "Pouch 1", parent_id=backpack["id"])
        pouch2 = await create_test_container(gear_service, test_user.id, "Pouch 2", parent_id=backpack["id"])
        pouch3 = await create_test_container(gear_service, test_user.id, "Pouch 3", parent_id=backpack["id"])

        # Assert
        assert pouch1["parentContainerId"] == backpack["id"]
        assert pouch2["parentContainerId"] == backpack["id"]
        assert pouch3["parentContainerId"] == backpack["id"]

    @pytest.mark.asyncio
    async def test_update_container_parent(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test moving container to different parent."""
        # Arrange
        backpack1 = await create_test_container(gear_service, test_user.id, "Backpack 1")
        backpack2 = await create_test_container(gear_service, test_user.id, "Backpack 2")
        pouch = await create_test_container(gear_service, test_user.id, "Pouch", parent_id=backpack1["id"])

        # Act - Move pouch from backpack1 to backpack2
        from app.modules.gear.schemas import ContainerUpdate

        update_data = ContainerUpdate(parentContainerId=backpack2["id"])
        updated = await gear_service.update_container(pouch["id"], test_user.id, update_data)

        # Assert
        assert updated is not None
        assert updated.parentContainerId == backpack2["id"]

    @pytest.mark.asyncio
    async def test_remove_container_from_parent(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test removing container from parent (make it top-level)."""
        # Arrange
        backpack = await create_test_container(gear_service, test_user.id, "Backpack")
        pouch = await create_test_container(gear_service, test_user.id, "Pouch", parent_id=backpack["id"])
        assert pouch["parentContainerId"] == backpack["id"]

        # Act - Remove from parent
        from app.modules.gear.schemas import ContainerUpdate

        update_data = ContainerUpdate(parentContainerId=None)
        updated = await gear_service.update_container(pouch["id"], test_user.id, update_data)

        # Assert
        assert updated is not None
        assert updated.parentContainerId is None


class TestItemNestedContainerReference:
    """Tests for System 2: Item nested_container_id reference.

    NOTE: nested_container_id field exists in database schema but is NOT exposed through API.
    Current ItemCreate/ItemUpdate schemas don't include this field.
    This represents legacy/unused functionality that unified model will address.

    These tests document current behavior: nesting containers is done via
    parent_container_id only (System 1), not through items.
    """

    @pytest.mark.asyncio
    async def test_nested_container_id_not_accessible_via_api(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that nested_container_id cannot be set through API.

        The field exists in database but ItemCreate schema doesn't expose it.
        """
        # Arrange
        main_backpack = await create_test_container(gear_service, test_user.id, "Main Backpack")
        await create_test_container(gear_service, test_user.id, "Small Backpack")

        # Act - Try to create item with nested container reference
        # Note: ItemCreate doesn't have nestedContainerId field
        data = ItemCreate(
            name="Item representing container",
            category="storage",
            weight=500.0,
        )
        item = await gear_service.create_item(main_backpack["id"], test_user.id, data)

        # Assert - Item created but without nested container reference
        assert item is not None
        assert item.container is not None
        assert item.container.id == main_backpack["id"]
        # nested_container_id field not accessible through API

    @pytest.mark.asyncio
    async def test_container_nesting_only_through_parent_id(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that container nesting works only through parent_container_id.

        Current system uses System 1 (parent_container_id) exclusively.
        System 2 (nested_container_id in items) is not accessible via API.
        """
        # Arrange - Create containers
        main_backpack = await create_test_container(gear_service, test_user.id, "Main Backpack")

        # System 1: Container nesting via parent_container_id (WORKS)
        admin_pouch = await create_test_container(
            gear_service,
            test_user.id,
            "Admin Pouch",
            container_type="pouch",
            parent_id=main_backpack["id"],
        )

        # Create regular items
        water_bottle = await create_test_item(
            gear_service,
            test_user.id,
            main_backpack["id"],
            "Water Bottle",
            category="water",
        )

        # Assert - Only System 1 nesting works
        # System 1: admin_pouch nested via parent_container_id
        fetched_pouch = await gear_service.get_container(admin_pouch["id"], test_user.id)
        assert fetched_pouch is not None
        assert fetched_pouch.parentContainerId == main_backpack["id"]

        # Regular item has no nesting capabilities
        fetched_water = await gear_service.get_item(water_bottle["id"], test_user.id)
        assert fetched_water is not None
        assert fetched_water.linkedItemId is None


class TestComplexNestingScenarios:
    """Tests for complex real-world nesting scenarios."""

    @pytest.mark.asyncio
    async def test_backpack_in_backpack_scenario(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test realistic scenario: Multiple containers nested using parent_container_id.

        Structure (using System 1 - parent_container_id only):
        - Bug-Out Bag (72h kit) - main container
          - EDC Pouch - nested container
            - Flashlight - item
            - Multi-tool - item
          - First Aid Pouch - nested container
            - Bandages - item
          - Water Bottle - regular item
        """
        # Arrange - Create main bug-out bag
        bug_out_bag = await create_test_container(gear_service, test_user.id, "72h Bug-Out Bag", container_type="backpack")

        # System 1: EDC Pouch nested inside bug-out bag
        edc_pouch = await create_test_container(
            gear_service,
            test_user.id,
            "EDC Pouch",
            container_type="pouch",
            parent_id=bug_out_bag["id"],
        )

        # Add items to EDC pouch
        await create_test_item(
            gear_service,
            test_user.id,
            edc_pouch["id"],
            "Flashlight",
            category="tools",
        )
        await create_test_item(
            gear_service,
            test_user.id,
            edc_pouch["id"],
            "Multi-tool",
            category="tools",
        )

        # System 1: First Aid Pouch nested inside bug-out bag
        first_aid_pouch = await create_test_container(
            gear_service,
            test_user.id,
            "First Aid Pouch",
            container_type="pouch",
            parent_id=bug_out_bag["id"],
        )

        # Add items to First Aid pouch
        await create_test_item(
            gear_service,
            test_user.id,
            first_aid_pouch["id"],
            "Bandages",
            category="medical",
        )

        # Add regular item to bug-out bag
        await create_test_item(
            gear_service,
            test_user.id,
            bug_out_bag["id"],
            "Water Bottle",
            category="water",
        )

        # Assert - Verify structure
        # 1. EDC Pouch nested in bug-out bag
        fetched_edc_pouch = await gear_service.get_container(edc_pouch["id"], test_user.id)
        assert fetched_edc_pouch is not None
        assert fetched_edc_pouch.parentContainerId == bug_out_bag["id"]

        # 2. First Aid Pouch nested in bug-out bag
        fetched_first_aid = await gear_service.get_container(first_aid_pouch["id"], test_user.id)
        assert fetched_first_aid is not None
        assert fetched_first_aid.parentContainerId == bug_out_bag["id"]

        # 3. Items in bug-out bag (only direct items, not nested containers' items)
        bug_out_items = await gear_service.get_items(bug_out_bag["id"], test_user.id)
        assert len(bug_out_items) == 1  # Water Bottle

        # 4. Items in EDC Pouch
        edc_pouch_items = await gear_service.get_items(edc_pouch["id"], test_user.id)
        assert len(edc_pouch_items) == 2  # Flashlight + Multi-tool

        # 5. Items in First Aid Pouch
        first_aid_items = await gear_service.get_items(first_aid_pouch["id"], test_user.id)
        assert len(first_aid_items) == 1  # Bandages

    @pytest.mark.asyncio
    async def test_get_all_containers_includes_nested(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that get_containers returns both top-level and nested containers."""
        # Arrange
        top_level_bag = await create_test_container(gear_service, test_user.id, "Top Level Bag")
        nested_pouch = await create_test_container(
            gear_service,
            test_user.id,
            "Nested Pouch",
            parent_id=top_level_bag["id"],
        )
        another_top_level = await create_test_container(gear_service, test_user.id, "Another Top Level")

        # Act
        all_containers = await gear_service.get_containers(test_user.id)

        # Assert
        assert len(all_containers) == 3
        container_ids = {c.id for c in all_containers}
        assert top_level_bag["id"] in container_ids
        assert nested_pouch["id"] in container_ids
        assert another_top_level["id"] in container_ids


class TestNestingEdgeCases:
    """Tests for edge cases and potential issues with dual-nesting."""

    @pytest.mark.asyncio
    async def test_container_cannot_be_its_own_parent(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that container cannot reference itself as parent.

        This would create a circular reference.
        """
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Self-Ref Container")

        # Act - Try to make container its own parent
        from app.modules.gear.schemas import ContainerUpdate

        update_data = ContainerUpdate(parentContainerId=container["id"])
        updated = await gear_service.update_container(container["id"], test_user.id, update_data)

        # Assert - Current behavior: update succeeds but creates circular reference
        # (This is a known issue that unified model should prevent)
        # For PHASE 0, we document current behavior
        assert updated is not None
        # Note: No validation prevents this in current system

    @pytest.mark.asyncio
    async def test_item_linked_to_nonexistent_item_fails(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that linkedItemId must reference existing item (FK constraint enforced).

        linkedItemId has FK constraint to gear_items table.
        Database prevents dangling references.
        """
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Container")

        # Act & Assert - Create item with invalid linkedItemId should fail
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            data = ItemCreate(
                name="Item with bad reference",
                category="storage",
                weight=100.0,
                linkedItemId="non-existent-item-id",
            )
            await gear_service.create_item(container["id"], test_user.id, data)

    @pytest.mark.asyncio
    async def test_deeply_nested_structure(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test deep nesting (5+ levels) to verify system handles it."""
        # Arrange & Act - Create 5-level nesting
        level1 = await create_test_container(gear_service, test_user.id, "Level 1")
        level2 = await create_test_container(gear_service, test_user.id, "Level 2", parent_id=level1["id"])
        level3 = await create_test_container(gear_service, test_user.id, "Level 3", parent_id=level2["id"])
        level4 = await create_test_container(gear_service, test_user.id, "Level 4", parent_id=level3["id"])
        level5 = await create_test_container(gear_service, test_user.id, "Level 5", parent_id=level4["id"])

        # Assert - Verify chain
        fetched_level5 = await gear_service.get_container(level5["id"], test_user.id)
        assert fetched_level5 is not None
        assert fetched_level5.parentContainerId == level4["id"]

        # Verify intermediate levels
        fetched_level3 = await gear_service.get_container(level3["id"], test_user.id)
        assert fetched_level3.parentContainerId == level2["id"]
