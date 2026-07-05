"""Migration: Add show_item_images field to gear_containers table.

This migration adds the show_item_images field to gear_containers table for controlling
whether item images should be displayed in container view (only items with primary image).

Usage:
    python migrations/019_add_show_item_images_field.py upgrade
    python migrations/019_add_show_item_images_field.py downgrade
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
    """Add show_item_images field to gear_containers table."""
    print("Adding show_item_images field to gear_containers table...")

    async with engine.begin() as conn:
        containers_exist = await table_exists(conn, "gear_containers")

        if not containers_exist:
            print("gear_containers table does not exist, skipping migration...")
            print(
                "Note: Table will be created with show_item_images field when created from models"
            )
            return

        show_item_images_exists = await column_exists(
            conn, "gear_containers", "show_item_images"
        )

        if show_item_images_exists:
            print("show_item_images column already exists, skipping migration...")
            return

        print("gear_containers table exists, adding show_item_images field...")
        # Add show_item_images field to gear_containers
        await conn.execute(
            text(
                """
                ALTER TABLE gear_containers 
                ADD COLUMN show_item_images BOOLEAN NOT NULL DEFAULT FALSE;
            """
            )
        )
        print("✓ Added show_item_images field to gear_containers table")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove show_item_images field from gear_containers table."""
    print("Removing show_item_images field from gear_containers table...")

    async with engine.begin() as conn:
        # Remove show_item_images field from gear_containers
        await conn.execute(
            text(
                """
                ALTER TABLE gear_containers 
                DROP COLUMN IF EXISTS show_item_images;
            """
            )
        )
        print("✓ Removed show_item_images field from gear_containers table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add show_item_images field migration")
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
