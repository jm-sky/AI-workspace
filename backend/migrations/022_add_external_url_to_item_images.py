"""Migration: Add external_url field to item_images table.

This migration adds the external_url field to support storing external image URLs
without downloading them to storage.

Usage:
    python migrations/022_add_external_url_to_item_images.py upgrade
    python migrations/022_add_external_url_to_item_images.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


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
    """Add external_url column to item_images table."""
    print("Adding external_url column to item_images table...")

    async with engine.begin() as conn:
        # Check if column already exists
        if await column_exists(conn, "item_images", "external_url"):
            print("external_url column already exists, skipping migration...")
            return

        # Add external_url column
        await conn.execute(
            text(
                """
                ALTER TABLE item_images
                ADD COLUMN external_url VARCHAR(1000) NULL;
            """
            )
        )
        print("✓ Added external_url column")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove external_url column from item_images table."""
    print("Removing external_url column from item_images table...")

    async with engine.begin() as conn:
        # Check if column exists
        if not await column_exists(conn, "item_images", "external_url"):
            print("external_url column does not exist, skipping downgrade...")
            return

        # Drop column
        await conn.execute(
            text(
                """
                ALTER TABLE item_images
                DROP COLUMN external_url;
            """
            )
        )
        print("✓ Removed external_url column")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add external_url to item_images migration"
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
