"""Migration: Add order field to gear_items table.

This migration adds the order field to gear_items table for manual item ordering.

Usage:
    python migrations/015_add_order_field.py upgrade
    python migrations/015_add_order_field.py downgrade
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


async def upgrade() -> None:
    """Add order field to gear_items table."""
    print("Adding order field to gear_items table...")

    async with engine.begin() as conn:
        items_exist = await table_exists(conn, "gear_items")

        if not items_exist:
            print("gear_items table does not exist, skipping migration...")
            print(
                "Note: Table will be created with order field when created from models"
            )
            return

        print("gear_items table exists, adding order field...")
        # Add order field to gear_items
        await conn.execute(
            text(
                """
                ALTER TABLE gear_items 
                ADD COLUMN IF NOT EXISTS "order" INTEGER;
            """
            )
        )
        print("✓ Added order field to gear_items table")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove order field from gear_items table."""
    print("Removing order field from gear_items table...")

    async with engine.begin() as conn:
        # Remove order field from gear_items
        await conn.execute(
            text(
                """
                ALTER TABLE gear_items 
                DROP COLUMN IF EXISTS "order";
            """
            )
        )
        print("✓ Removed order field from gear_items table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add order field migration")
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
