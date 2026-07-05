"""Migration: Add show_on_container field to gear_items table.

This migration adds the show_on_container field to gear_items table for controlling
whether item images should be displayed in container view gallery.

Usage:
    python migrations/018_add_show_on_container_field.py upgrade
    python migrations/018_add_show_on_container_field.py downgrade
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
    """Add show_on_container field to gear_items table."""
    print("Adding show_on_container field to gear_items table...")

    async with engine.begin() as conn:
        items_exist = await table_exists(conn, "gear_items")

        if not items_exist:
            print("gear_items table does not exist, skipping migration...")
            print(
                "Note: Table will be created with show_on_container field when created from models"
            )
            return

        show_on_container_exists = await column_exists(
            conn, "gear_items", "show_on_container"
        )

        if show_on_container_exists:
            print("show_on_container column already exists, skipping migration...")
            return

        print("gear_items table exists, adding show_on_container field...")
        # Add show_on_container field to gear_items
        await conn.execute(
            text(
                """
                ALTER TABLE gear_items 
                ADD COLUMN show_on_container BOOLEAN NOT NULL DEFAULT FALSE;
            """
            )
        )
        print("✓ Added show_on_container field to gear_items table")

        # Add index for better query performance
        await conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_gear_items_show_on_container 
                ON gear_items(show_on_container);
            """
            )
        )
        print("✓ Added index on show_on_container field")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove show_on_container field from gear_items table."""
    print("Removing show_on_container field from gear_items table...")

    async with engine.begin() as conn:
        # Remove index first
        await conn.execute(
            text(
                """
                DROP INDEX IF EXISTS ix_gear_items_show_on_container;
            """
            )
        )
        print("✓ Removed index on show_on_container field")

        # Remove show_on_container field from gear_items
        await conn.execute(
            text(
                """
                ALTER TABLE gear_items 
                DROP COLUMN IF EXISTS show_on_container;
            """
            )
        )
        print("✓ Removed show_on_container field from gear_items table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add show_on_container field migration"
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
