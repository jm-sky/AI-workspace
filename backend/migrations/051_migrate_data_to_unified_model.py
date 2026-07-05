"""Migration: Migrate data from gear_containers and gear_items to gear_items_v2.

This migration performs the actual data migration to the unified model:
1. Migrates all containers to gear_items_v2 with item_type='container'
2. Migrates all items to gear_items_v2 with item_type='item'
3. Verifies data integrity (row counts must match)

Field Mapping:
- GearContainerDB.id → gear_items_v2.id (preserved)
- GearContainerDB.parent_container_id → gear_items_v2.parent_item_id
- GearContainerDB.type → gear_items_v2.container_type
- GearItemDB.id → gear_items_v2.id (preserved)
- GearItemDB.container_id → gear_items_v2.parent_item_id
- GearItemDB.order → gear_items_v2.order_index
- GearItemDB.nested_container_id → REMOVED (legacy, unused in API)

Usage:
    python migrations/042_migrate_data_to_unified_model.py upgrade
    python migrations/042_migrate_data_to_unified_model.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def get_row_count(conn, table_name: str) -> int:
    """Get row count for a table."""
    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
    return result.scalar() or 0


async def upgrade() -> None:
    """Migrate data from gear_containers and gear_items to gear_items_v2."""
    print("Migrating data to unified gear_items_v2 table...")

    async with engine.begin() as conn:
        # Verify tables exist
        containers_exist = await table_exists(conn, "gear_containers")
        items_exist = await table_exists(conn, "gear_items")
        items_v2_exist = await table_exists(conn, "gear_items_v2")

        if not items_v2_exist:
            print(
                "❌ Error: gear_items_v2 table does not exist. Run migration 041 first."
            )
            sys.exit(1)

        if not containers_exist or not items_exist:
            print("⚠️  Warning: Source tables do not exist. Skipping migration.")
            return

        # Get source row counts
        container_count = await get_row_count(conn, "gear_containers")
        item_count = await get_row_count(conn, "gear_items")
        print(f"Source data: {container_count} containers, {item_count} items")

        # Check if already migrated
        v2_count = await get_row_count(conn, "gear_items_v2")
        if v2_count > 0:
            print(
                f"⚠️  Warning: gear_items_v2 already contains {v2_count} rows. Skipping migration."
            )
            return

        # Step 1: Migrate containers → gear_items_v2 (item_type='container')
        print("Step 1: Migrating containers...")
        await conn.execute(
            text(
                """
                INSERT INTO gear_items_v2 (
                    id, user_id, item_type, parent_item_id,
                    name, description, brand, price, weight, weight_unit, url, color,
                    container_type, max_weight, max_weight_unit, hide_when_nested,
                    is_public, favorite, show_item_images,
                    category, quantity, status, priority, expiration_date, quality,
                    wearable, consumable, order_index, show_on_container,
                    created_at, updated_at
                )
                SELECT
                    id,
                    user_id,
                    'container' AS item_type,
                    parent_container_id AS parent_item_id,
                    name,
                    description,
                    brand,
                    price,
                    weight,
                    weight_unit,
                    url,
                    color,
                    type AS container_type,
                    max_weight,
                    max_weight_unit,
                    hide_when_nested,
                    is_public,
                    favorite,
                    show_item_images,
                    NULL AS category,
                    NULL AS quantity,
                    NULL AS status,
                    NULL AS priority,
                    NULL AS expiration_date,
                    NULL AS quality,
                    NULL AS wearable,
                    NULL AS consumable,
                    NULL AS order_index,
                    NULL AS show_on_container,
                    created_at,
                    updated_at
                FROM gear_containers;
            """
            )
        )
        print(f"✓ Migrated {container_count} containers")

        # Step 2: Migrate items → gear_items_v2 (item_type='item')
        print("Step 2: Migrating items...")
        await conn.execute(
            text(
                """
                INSERT INTO gear_items_v2 (
                    id, user_id, item_type, parent_item_id,
                    name, brand, price, currency, weight, weight_unit, url, color, notes,
                    category, quantity, status, priority, expiration_date, quality,
                    wearable, consumable, order_index, show_on_container,
                    linked_item_id, catalogue_item_id,
                    container_type, max_weight, max_weight_unit, hide_when_nested,
                    is_public, favorite, show_item_images,
                    created_at, updated_at
                )
                SELECT
                    gi.id,
                    gc.user_id,
                    'item' AS item_type,
                    gi.container_id AS parent_item_id,
                    gi.name,
                    gi.brand,
                    gi.price,
                    gi.currency,
                    gi.weight,
                    gi.weight_unit,
                    gi.url,
                    gi.color,
                    gi.notes,
                    gi.category,
                    gi.quantity,
                    gi.status,
                    gi.priority,
                    gi.expiration_date,
                    gi.quality,
                    gi.wearable,
                    gi.consumable,
                    gi."order" AS order_index,
                    gi.show_on_container,
                    gi.linked_item_id,
                    gi.catalogue_item_id,
                    NULL AS container_type,
                    NULL AS max_weight,
                    NULL AS max_weight_unit,
                    NULL AS hide_when_nested,
                    NULL AS is_public,
                    NULL AS favorite,
                    NULL AS show_item_images,
                    gi.created_at,
                    gi.updated_at
                FROM gear_items gi
                JOIN gear_containers gc ON gi.container_id = gc.id;
            """
            )
        )
        print(f"✓ Migrated {item_count} items")

        # Step 3: Verify migration integrity
        print("Step 3: Verifying migration integrity...")
        v2_count = await get_row_count(conn, "gear_items_v2")
        expected_count = container_count + item_count

        if v2_count != expected_count:
            print(f"❌ Error: Migration failed!")
            print(f"   Expected: {expected_count} rows")
            print(f"   Got: {v2_count} rows")
            raise Exception(
                f"Migration integrity check failed: expected {expected_count} rows, got {v2_count}"
            )

        # Verify containers
        v2_container_count = await conn.execute(
            text("SELECT COUNT(*) FROM gear_items_v2 WHERE item_type = 'container';")
        )
        v2_container_count = v2_container_count.scalar()
        if v2_container_count != container_count:
            print(f"❌ Error: Container count mismatch!")
            print(f"   Expected: {container_count} containers")
            print(f"   Got: {v2_container_count} containers")
            raise Exception(
                f"Container migration failed: expected {container_count}, got {v2_container_count}"
            )

        # Verify items
        v2_item_count = await conn.execute(
            text("SELECT COUNT(*) FROM gear_items_v2 WHERE item_type = 'item';")
        )
        v2_item_count = v2_item_count.scalar()
        if v2_item_count != item_count:
            print(f"❌ Error: Item count mismatch!")
            print(f"   Expected: {item_count} items")
            print(f"   Got: {v2_item_count} items")
            raise Exception(
                f"Item migration failed: expected {item_count}, got {v2_item_count}"
            )

        print(
            f"✓ Migration verified: {v2_container_count} containers + {v2_item_count} items = {v2_count} total rows"
        )
        print("✓ Data migration completed successfully!")


async def downgrade() -> None:
    """Remove all data from gear_items_v2."""
    print("Clearing gear_items_v2 table...")

    async with engine.begin() as conn:
        items_v2_exist = await table_exists(conn, "gear_items_v2")
        if items_v2_exist:
            v2_count = await get_row_count(conn, "gear_items_v2")
            if v2_count > 0:
                print(f"Deleting {v2_count} rows from gear_items_v2...")
                await conn.execute(text("DELETE FROM gear_items_v2;"))
                print(f"✓ Deleted {v2_count} rows from gear_items_v2")
            else:
                print("✓ gear_items_v2 table is already empty")
        else:
            print("✓ gear_items_v2 table does not exist")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print(
            "Usage: python migrations/042_migrate_data_to_unified_model.py [upgrade|downgrade]"
        )
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        await upgrade()
    elif command == "downgrade":
        await downgrade()
    else:
        print(f"Unknown command: {command}")
        print(
            "Usage: python migrations/042_migrate_data_to_unified_model.py [upgrade|downgrade]"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
