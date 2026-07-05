"""Migration: Fix nullable constraints on gear_items_v2 table.

This migration ensures all item-specific and container-specific fields are properly
nullable in the gear_items_v2 table. This fixes issues where Base.metadata.create_all()
may have created columns with incorrect NOT NULL constraints.

Background:
- When item_type='container', all item-specific fields must be NULL
- When item_type='item', all container-specific fields must be NULL
- Some fields were incorrectly created with NOT NULL constraints

This migration:
- Removes NOT NULL constraints from all type-specific fields
- Ensures database schema matches model definitions
- Safe to run multiple times (idempotent)

Usage:
    python migrations/054_fix_nullable_constraints_v2.py upgrade
    python migrations/054_fix_nullable_constraints_v2.py downgrade
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


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Fix nullable constraints on gear_items_v2 table."""
    print("Fixing nullable constraints on gear_items_v2 table...")

    async with engine.begin() as conn:
        items_v2_exist = await table_exists(conn, "gear_items_v2")
        if not items_v2_exist:
            print("✓ gear_items_v2 table does not exist, skipping...")
            return

        print("Removing NOT NULL constraints from container-specific fields...")

        # Container-specific fields (must be NULL when item_type='item')
        container_fields = [
            "container_type",
            "max_weight",
            "max_weight_unit",
            "hide_when_nested",
            "is_public",
            "is_hidden_by_reports",
            "favorite",
            "show_item_images",
        ]

        for field in container_fields:
            if await column_exists(conn, "gear_items_v2", field):
                await conn.execute(
                    text(
                        f"ALTER TABLE gear_items_v2 ALTER COLUMN {field} DROP NOT NULL;"
                    )
                )
                print(f"✓ Dropped NOT NULL constraint on {field}")
            else:
                print(f"⚠ Column {field} does not exist, skipping...")

        print("Removing NOT NULL constraints from item-specific fields...")

        # Item-specific fields (must be NULL when item_type='container')
        item_fields = [
            "category",
            "quantity",
            "status",
            "priority",
            "expiration_date",
            "shelf_life",
            "quality",
            "wearable",
            "consumable",
            "order_index",
            "show_on_container",
            "promote_count",
        ]

        for field in item_fields:
            if await column_exists(conn, "gear_items_v2", field):
                await conn.execute(
                    text(
                        f"ALTER TABLE gear_items_v2 ALTER COLUMN {field} DROP NOT NULL;"
                    )
                )
                print(f"✓ Dropped NOT NULL constraint on {field}")
            else:
                print(f"⚠ Column {field} does not exist, skipping...")

        print("✓ All nullable constraints fixed successfully")


async def downgrade() -> None:
    """Reverse the nullable constraint fixes.

    WARNING: This will ADD NOT NULL constraints, which may fail if there are NULL values.
    Only run this if you're certain all values conform to the constraints.
    """
    print("WARNING: Downgrade will add NOT NULL constraints back.")
    print(
        "This migration is intentionally a no-op for downgrade to prevent data issues."
    )
    print("✓ Downgrade skipped (no changes made)")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print(
            "Usage: python migrations/054_fix_nullable_constraints_v2.py [upgrade|downgrade]"
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
            "Usage: python migrations/054_fix_nullable_constraints_v2.py [upgrade|downgrade]"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
