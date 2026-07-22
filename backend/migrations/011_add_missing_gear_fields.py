"""Migration: Add missing fields to gear_containers and gear_items tables.

This migration adds the following fields:
- gear_containers: hide_when_nested, weight, weight_unit, max_weight, max_weight_unit, url
- gear_items: linked_item_id, wearable, consumable

Usage:
    python migrations/003_add_missing_gear_fields.py upgrade
    python migrations/003_add_missing_gear_fields.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine
from app.modules.gear.db_models import GearContainerDB, GearItemDB  # noqa: F401


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    # Use SQL query to check if table exists (works with async)
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Add missing fields to gear tables."""
    print("Adding missing fields to gear tables...")

    async with engine.begin() as conn:
        # Check if tables exist, if not create them with all fields (using SQLAlchemy models)
        containers_exist = await table_exists(conn, "gear_containers")
        items_exist = await table_exists(conn, "gear_items")

        if not containers_exist:
            print("gear_containers table does not exist, creating it with all fields...")
            await conn.run_sync(GearContainerDB.metadata.create_all)
            print("✓ gear_containers table created with all fields")
        else:
            print("gear_containers table exists, adding missing fields...")
            # Add fields to gear_containers
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS hide_when_nested BOOLEAN DEFAULT FALSE;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS weight FLOAT;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS weight_unit VARCHAR(5);
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS max_weight FLOAT;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS max_weight_unit VARCHAR(5);
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS url TEXT;
            """))

        if not items_exist:
            print("gear_items table does not exist, creating it with all fields...")
            await conn.run_sync(GearItemDB.metadata.create_all)
            print("✓ gear_items table created with all fields")
        else:
            print("gear_items table exists, adding missing fields...")
            # Add fields to gear_items
            await conn.execute(text("""
                ALTER TABLE gear_items
                ADD COLUMN IF NOT EXISTS linked_item_id VARCHAR(36);
            """))
            await conn.execute(text("""
                ALTER TABLE gear_items
                ADD COLUMN IF NOT EXISTS wearable BOOLEAN DEFAULT FALSE;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_items
                ADD COLUMN IF NOT EXISTS consumable BOOLEAN DEFAULT FALSE;
            """))

        # Add foreign key for linked_item_id (only if table exists and was modified, not created)
        if items_exist:
            # Check if constraint already exists using SQL
            try:
                result = await conn.execute(text("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints
                            WHERE constraint_schema = 'public'
                            AND table_name = 'gear_items'
                            AND constraint_name = 'fk_gear_items_linked_item_id'
                        );
                    """))
                constraint_exists = result.scalar() is True

                if not constraint_exists:
                    await conn.execute(text("""
                        ALTER TABLE gear_items
                        ADD CONSTRAINT fk_gear_items_linked_item_id
                        FOREIGN KEY (linked_item_id) REFERENCES gear_items(id) ON DELETE SET NULL;
                    """))
                    print("✓ Added foreign key constraint for linked_item_id")
                else:
                    print("✓ Foreign key constraint for linked_item_id already exists")
            except Exception as e:
                print(f"Note: Could not add foreign key constraint: {e}")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove added fields from gear tables."""
    print("Removing added fields from gear tables...")

    async with engine.begin() as conn:
        # Remove foreign key first
        try:
            await conn.execute(text("""
                ALTER TABLE gear_items
                DROP CONSTRAINT IF EXISTS fk_gear_items_linked_item_id;
            """))
        except Exception:
            pass

        # Remove fields from gear_items
        await conn.execute(text("""
            ALTER TABLE gear_items
            DROP COLUMN IF EXISTS consumable;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_items
            DROP COLUMN IF EXISTS wearable;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_items
            DROP COLUMN IF EXISTS linked_item_id;
        """))

        # Remove fields from gear_containers
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS url;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS max_weight_unit;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS max_weight;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS weight_unit;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS weight;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS hide_when_nested;
        """))

    print("✓ Removed added fields from gear_items")
    print("✓ Removed added fields from gear_containers")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add missing gear fields migration")
    parser.add_argument(
        "action",
        choices=["upgrade", "downgrade"],
        help="Migration action (upgrade or downgrade)",
    )
    args = parser.parse_args()

    if args.action == "upgrade":
        await upgrade()
    elif args.action == "downgrade":
        await downgrade()

    # Close database connections
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
