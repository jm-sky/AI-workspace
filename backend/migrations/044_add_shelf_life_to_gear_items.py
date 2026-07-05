"""Migration: Add shelf_life field to gear_items table.

This migration adds the shelf_life field (JSONB) to gear_items table for storing
shelf life period information (e.g., {value: 10, unit: 'years'}).

Usage:
    python migrations/044_add_shelf_life_to_gear_items.py upgrade
    python migrations/044_add_shelf_life_to_gear_items.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database.

    Args:
        conn: Database connection
        table_name: Name of the table to check

    Returns:
        True if table exists, False otherwise
    """
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
    """Check if a column exists in a table (PostgreSQL compatible).

    Args:
        conn: Database connection
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        True if column exists, False otherwise
    """
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
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
    """Add shelf_life field to gear_items table."""
    print("Adding shelf_life field to gear_items table...")

    async with engine.begin() as conn:
        # Check if gear_items table exists
        items_exist = await table_exists(conn, "gear_items")

        if not items_exist:
            print("gear_items table does not exist, skipping migration...")
            print(
                "Note: Table will be created with shelf_life field when created from models"
            )
            return

        # Add shelf_life column to gear_items if it doesn't exist
        if not await column_exists(conn, "gear_items", "shelf_life"):
            print("Adding shelf_life column to gear_items table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items
                    ADD COLUMN shelf_life JSONB;
                """
                )
            )
            print("✓ Added shelf_life column to gear_items table")
        else:
            print("shelf_life column already exists, skipping...")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove shelf_life field from gear_items table."""
    print("Removing shelf_life field from gear_items table...")

    async with engine.begin() as conn:
        # Remove shelf_life column from gear_items
        if await column_exists(conn, "gear_items", "shelf_life"):
            print("Removing shelf_life column from gear_items table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items
                    DROP COLUMN IF EXISTS shelf_life;
                """
                )
            )
            print("✓ Removed shelf_life column from gear_items table")
        else:
            print("shelf_life column does not exist, skipping...")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add shelf_life to gear_items migration"
    )
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
