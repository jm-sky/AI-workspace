"""Migration: Add shops field to global_catalogue_items table.

This migration adds shops field to the global_catalogue_items table
to support multiple shop links for catalogue items.

Usage:
    python migrations/035_add_shops_to_catalogue.py upgrade
    python migrations/035_add_shops_to_catalogue.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


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
    """Add shops column to global_catalogue_items table."""
    print("Adding shops field to global_catalogue_items table...")

    async with engine.begin() as conn:
        shops_exists = await column_exists(conn, "global_catalogue_items", "shops")

        if shops_exists:
            print("shops column already exists, skipping migration...")
            return

        print("Adding shops column...")
        await conn.execute(
            text(
                """
                ALTER TABLE global_catalogue_items
                ADD COLUMN shops JSONB NOT NULL DEFAULT '[]'::JSONB;
            """
            ),
        )

        print("✓ Added shops field to global_catalogue_items table")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove shops column from global_catalogue_items table."""
    print("Removing shops field from global_catalogue_items table...")

    async with engine.begin() as conn:
        shops_exists = await column_exists(conn, "global_catalogue_items", "shops")

        if not shops_exists:
            print("shops column does not exist, skipping downgrade...")
            return

        print("Removing shops column...")
        await conn.execute(
            text(
                """
                ALTER TABLE global_catalogue_items
                DROP COLUMN shops;
            """
            ),
        )

        print("✓ Removed shops field from global_catalogue_items table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add shops to global_catalogue_items migration"
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
