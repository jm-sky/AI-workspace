"""Migration: Add catalogue_item_id to gear_items table.

This migration adds the catalogue_item_id column to gear_items table
to track which items were added from the global catalogue.

Usage:
    python migrations/030_add_catalogue_item_id_to_gear_items.py upgrade
    python migrations/030_add_catalogue_item_id_to_gear_items.py downgrade
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


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table.

    Args:
        conn: Database connection
        table_name: Name of the table
        column_name: Name of the column to check

    Returns:
        True if column exists, False otherwise
    """
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Add catalogue_item_id column to gear_items table."""
    print("Adding catalogue_item_id column to gear_items table...")

    async with engine.begin() as conn:
        column_exist = await column_exists(conn, "gear_items", "catalogue_item_id")

        if column_exist:
            print("catalogue_item_id column already exists, skipping migration...")
            return

        # Check if referenced table exists
        table_exist = await table_exists(conn, "global_catalogue_items")
        if not table_exist:
            raise RuntimeError("Table 'global_catalogue_items' does not exist. " "Please run migration 029 (add_global_catalogue_items) first.")

        print("Adding catalogue_item_id column...")
        await conn.execute(
            text("""
                ALTER TABLE gear_items
                ADD COLUMN catalogue_item_id VARCHAR(36);
            """),
        )

        print("Adding foreign key constraint...")
        await conn.execute(
            text("""
                ALTER TABLE gear_items
                ADD CONSTRAINT fk_gear_items_catalogue_item_id
                    FOREIGN KEY (catalogue_item_id)
                    REFERENCES global_catalogue_items(id)
                    ON DELETE SET NULL;
            """),
        )

        # Create index for better query performance
        print("Creating index...")
        await conn.execute(text("CREATE INDEX ix_gear_items_catalogue_item_id ON gear_items(catalogue_item_id);"))

        print("✓ Added catalogue_item_id column with foreign key and index")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove catalogue_item_id column from gear_items table."""
    print("Removing catalogue_item_id column from gear_items table...")

    async with engine.begin() as conn:
        column_exist = await column_exists(conn, "gear_items", "catalogue_item_id")

        if not column_exist:
            print("catalogue_item_id column does not exist, skipping downgrade...")
            return

        # Drop index
        print("Dropping index...")
        await conn.execute(text("DROP INDEX IF EXISTS ix_gear_items_catalogue_item_id;"))

        # Drop foreign key constraint
        print("Dropping foreign key constraint...")
        await conn.execute(text("ALTER TABLE gear_items DROP CONSTRAINT IF EXISTS fk_gear_items_catalogue_item_id;"))

        # Drop column
        print("Dropping column...")
        await conn.execute(text("ALTER TABLE gear_items DROP COLUMN IF EXISTS catalogue_item_id;"))

        print("✓ Removed catalogue_item_id column")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add catalogue_item_id to gear_items table migration")
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
