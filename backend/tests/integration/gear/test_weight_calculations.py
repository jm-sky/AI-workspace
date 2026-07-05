"""Integration tests for weight calculation functionality.

PHASE 0: Test Creation (Pre-Implementation Safety Net)
Document current weight calculation behavior before unified model migration.

Current System:
- calculate_container_weight() sums item weights (with unit conversion)
- Does NOT include container's own weight
- Does NOT include nested containers' weights (recursive calculation missing)
- Units supported: g (grams), kg (kilograms), oz (ounces), lb (pounds)
"""

import pytest

from app.modules.auth.db_models import UserDB
from app.modules.gear.schemas import ItemCreate
from app.modules.gear.service import GearService

from .conftest import create_test_container, create_test_item


class TestBasicWeightCalculations:
    """Tests for basic weight calculation functionality."""

    @pytest.mark.asyncio
    async def test_calculate_empty_container_weight(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation for empty container."""
        # Arrange
        container = await create_test_container(
            gear_service, test_user.id, "Empty Backpack", weight=500.0, weight_unit="g"
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # Note: Container's own weight is NOT included in calculation
        assert weights["grams"] == 0.0
        assert weights["kilograms"] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_single_item_weight_grams(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with single item in grams."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Water Bottle",
            weight=300.0,
            weight_unit="g",
            quantity=1,
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        assert weights["grams"] == 300.0
        assert weights["kilograms"] == 0.3

    @pytest.mark.asyncio
    async def test_calculate_multiple_items_same_unit(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with multiple items (same unit)."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Water Bottle",
            weight=300.0,
            weight_unit="g",
        )
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Food",
            weight=500.0,
            weight_unit="g",
        )
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "First Aid Kit",
            weight=200.0,
            weight_unit="g",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        assert weights["grams"] == 1000.0
        assert weights["kilograms"] == 1.0


class TestWeightUnitConversions:
    """Tests for weight unit conversions in calculations."""

    @pytest.mark.asyncio
    async def test_calculate_weight_kilograms_to_grams(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with kilogram units."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Sleeping Bag",
            weight=1.5,
            weight_unit="kg",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # 1.5 kg = 1500 g
        assert weights["grams"] == 1500.0
        assert weights["kilograms"] == 1.5

    @pytest.mark.asyncio
    async def test_calculate_weight_ounces_to_grams(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with ounce units."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        # 1 oz = 28.3495 g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Energy Bar",
            weight=2.0,
            weight_unit="oz",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # 2 oz = 56.699 g
        assert weights["grams"] == pytest.approx(56.699, rel=1e-3)
        assert weights["kilograms"] == pytest.approx(0.056699, rel=1e-3)

    @pytest.mark.asyncio
    async def test_calculate_weight_pounds_to_grams(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with pound units."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        # 1 lb = 453.592 g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Tent",
            weight=3.0,
            weight_unit="lb",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # 3 lb = 1360.776 g
        assert weights["grams"] == pytest.approx(1360.776, rel=1e-3)
        assert weights["kilograms"] == pytest.approx(1.360776, rel=1e-3)

    @pytest.mark.asyncio
    async def test_calculate_weight_mixed_units(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with mixed units."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        # 500g item
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Water",
            weight=500.0,
            weight_unit="g",
        )
        # 1kg item = 1000g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Food",
            weight=1.0,
            weight_unit="kg",
        )
        # 10oz item = 283.495g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Snacks",
            weight=10.0,
            weight_unit="oz",
        )
        # 1lb item = 453.592g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Gear",
            weight=1.0,
            weight_unit="lb",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # Total: 500 + 1000 + 283.495 + 453.592 = 2237.087g
        assert weights["grams"] == pytest.approx(2237.087, rel=1e-3)
        assert weights["kilograms"] == pytest.approx(2.237087, rel=1e-3)


class TestWeightWithQuantity:
    """Tests for weight calculations with item quantities."""

    @pytest.mark.asyncio
    async def test_calculate_weight_with_quantity(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that weight calculation multiplies by quantity."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Energy Bars",
            weight=50.0,
            weight_unit="g",
            quantity=5,
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # 50g * 5 = 250g
        assert weights["grams"] == 250.0
        assert weights["kilograms"] == 0.25

    @pytest.mark.asyncio
    async def test_calculate_weight_multiple_items_with_quantities(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with multiple items having different quantities."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        # 100g x 3 = 300g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Batteries",
            weight=100.0,
            weight_unit="g",
            quantity=3,
        )
        # 50g x 10 = 500g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Energy Bars",
            weight=50.0,
            weight_unit="g",
            quantity=10,
        )
        # 200g x 1 = 200g
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "First Aid Kit",
            weight=200.0,
            weight_unit="g",
            quantity=1,
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # Total: 300 + 500 + 200 = 1000g
        assert weights["grams"] == 1000.0
        assert weights["kilograms"] == 1.0


class TestWeightCalculationLimitations:
    """Tests documenting current limitations of weight calculation.

    These tests document that current implementation does NOT:
    - Include container's own weight
    - Include nested containers' weights
    - Calculate recursively through nesting hierarchy
    """

    @pytest.mark.asyncio
    async def test_container_own_weight_not_included(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that container's own weight is NOT included in calculation.

        LIMITATION: Container weight field exists but is not used in calculations.
        """
        # Arrange - Container with its own weight specified
        container = await create_test_container(
            gear_service,
            test_user.id,
            "Backpack",
            weight=500.0,  # Container weighs 500g
            weight_unit="g",
        )
        # Add 300g item
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Water Bottle",
            weight=300.0,
            weight_unit="g",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        # Current implementation: Only item weight (300g), container weight ignored
        # Expected future: 500g (container) + 300g (item) = 800g
        assert weights["grams"] == 300.0  # NOT 800.0
        assert weights["kilograms"] == 0.3  # NOT 0.8

        # Verify container weight is stored but not used
        assert fetched.weight == 500.0
        assert fetched.weightUnit == "g"

    @pytest.mark.asyncio
    async def test_nested_containers_weight_not_included(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that nested containers' weights are NOT included in calculation.

        LIMITATION: No recursive weight calculation through nesting hierarchy.
        """
        # Arrange - Create nested structure
        main_backpack = await create_test_container(
            gear_service, test_user.id, "Main Backpack"
        )

        # Nested pouch with items
        pouch = await create_test_container(
            gear_service,
            test_user.id,
            "Pouch",
            parent_id=main_backpack["id"],
            weight=100.0,  # Pouch weighs 100g
            weight_unit="g",
        )

        # Add 200g item to pouch
        await create_test_item(
            gear_service,
            test_user.id,
            pouch["id"],
            "Flashlight",
            weight=200.0,
            weight_unit="g",
        )

        # Add 500g item to main backpack
        await create_test_item(
            gear_service,
            test_user.id,
            main_backpack["id"],
            "Water Bottle",
            weight=500.0,
            weight_unit="g",
        )

        # Act
        fetched_main = await gear_service.get_container(
            main_backpack["id"], test_user.id
        )
        assert fetched_main is not None
        main_weights = gear_service.calculate_container_weight(fetched_main)

        # Assert
        # Current implementation: Only direct items (500g water bottle)
        # Does NOT include: nested pouch (100g) + pouch items (200g)
        # Expected future: 500g + 100g + 200g = 800g
        assert main_weights["grams"] == 500.0  # NOT 800.0
        assert main_weights["kilograms"] == 0.5  # NOT 0.8

        # Verify pouch calculation is separate
        fetched_pouch = await gear_service.get_container(pouch["id"], test_user.id)
        assert fetched_pouch is not None
        pouch_weights = gear_service.calculate_container_weight(fetched_pouch)
        assert pouch_weights["grams"] == 200.0  # Only flashlight, not pouch weight

    @pytest.mark.asyncio
    async def test_no_recursive_weight_calculation(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that weight calculation is NOT recursive through nesting levels.

        LIMITATION: Each container's weight is calculated independently.
        """
        # Arrange - Create 3-level nesting
        level1 = await create_test_container(
            gear_service, test_user.id, "Level 1", weight=100.0, weight_unit="g"
        )
        level2 = await create_test_container(
            gear_service,
            test_user.id,
            "Level 2",
            parent_id=level1["id"],
            weight=50.0,
            weight_unit="g",
        )
        level3 = await create_test_container(
            gear_service,
            test_user.id,
            "Level 3",
            parent_id=level2["id"],
            weight=25.0,
            weight_unit="g",
        )

        # Add items to each level
        await create_test_item(
            gear_service,
            test_user.id,
            level1["id"],
            "Item L1",
            weight=300.0,
            weight_unit="g",
        )
        await create_test_item(
            gear_service,
            test_user.id,
            level2["id"],
            "Item L2",
            weight=200.0,
            weight_unit="g",
        )
        await create_test_item(
            gear_service,
            test_user.id,
            level3["id"],
            "Item L3",
            weight=100.0,
            weight_unit="g",
        )

        # Act - Calculate each level independently
        fetched_l1 = await gear_service.get_container(level1["id"], test_user.id)
        fetched_l2 = await gear_service.get_container(level2["id"], test_user.id)
        fetched_l3 = await gear_service.get_container(level3["id"], test_user.id)

        assert fetched_l1 is not None
        assert fetched_l2 is not None
        assert fetched_l3 is not None

        weights_l1 = gear_service.calculate_container_weight(fetched_l1)
        weights_l2 = gear_service.calculate_container_weight(fetched_l2)
        weights_l3 = gear_service.calculate_container_weight(fetched_l3)

        # Assert - Each level calculated independently
        # L1: Only direct item (300g), not nested containers or their items
        assert weights_l1["grams"] == 300.0  # NOT 300+200+100=600
        # L2: Only direct item (200g)
        assert weights_l2["grams"] == 200.0  # NOT 200+100=300
        # L3: Only direct item (100g)
        assert weights_l3["grams"] == 100.0

        # Manual recursive calculation would be:
        # Total = 100 (L1 container) + 300 (L1 item) +
        #         50 (L2 container) + 200 (L2 item) +
        #         25 (L3 container) + 100 (L3 item) = 775g
        # But current implementation doesn't support this


class TestWeightCalculationEdgeCases:
    """Tests for edge cases in weight calculations."""

    @pytest.mark.asyncio
    async def test_calculate_weight_zero_items(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with no items returns zero."""
        # Arrange
        container = await create_test_container(
            gear_service, test_user.id, "Empty Backpack"
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        assert weights["grams"] == 0.0
        assert weights["kilograms"] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_weight_zero_weight_items(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with zero-weight items."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        # Documents can have zero weight
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Important Document",
            weight=0.0,
            weight_unit="g",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        assert weights["grams"] == 0.0
        assert weights["kilograms"] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_weight_large_numbers(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test weight calculation with large weight values."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        # Very heavy item (e.g., full water reservoir)
        await create_test_item(
            gear_service,
            test_user.id,
            container["id"],
            "Water Reservoir",
            weight=5.0,
            weight_unit="kg",
        )

        # Act
        fetched = await gear_service.get_container(container["id"], test_user.id)
        assert fetched is not None
        weights = gear_service.calculate_container_weight(fetched)

        # Assert
        assert weights["grams"] == 5000.0
        assert weights["kilograms"] == 5.0
