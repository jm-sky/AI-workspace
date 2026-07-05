"""Migration: Add currency field to gear_items table.

This migration adds the currency field to gear_items table for storing
currency code (PLN, USD, EUR, GBP, etc.) alongside item prices.

Usage:
    python migrations/026_add_currency_to_gear_items.py upgrade
    python migrations/026_add_currency_to_gear_items.py downgrade
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
    """Add currency field to gear_items table."""
    print("Adding currency field to gear_items table...")

    async with engine.begin() as conn:
        items_exist = await table_exists(conn, "gear_items")

        if not items_exist:
            print("gear_items table does not exist, skipping migration...")
            print(
                "Note: Table will be created with currency field when created from models"
            )
            return

        currency_exists = await column_exists(conn, "gear_items", "currency")

        if currency_exists:
            print("currency column already exists, skipping migration...")
            return

        print("gear_items table exists, adding currency field...")
        # Add currency field to gear_items
        await conn.execute(
            text(
                """
                ALTER TABLE gear_items 
                ADD COLUMN currency VARCHAR(10);
            """
            )
        )
        print("✓ Added currency field to gear_items table")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove currency field from gear_items table."""
    print("Removing currency field from gear_items table...")

    async with engine.begin() as conn:
        items_exist = await table_exists(conn, "gear_items")

        if not items_exist:
            print("gear_items table does not exist, skipping downgrade...")
            return

        currency_exists = await column_exists(conn, "gear_items", "currency")

        if not currency_exists:
            print("currency column does not exist, skipping downgrade...")
            return

        print("gear_items table exists, removing currency field...")
        # Remove currency field from gear_items
        await conn.execute(
            text(
                """
                ALTER TABLE gear_items 
                DROP COLUMN currency;
            """
            )
        )
        print("✓ Removed currency field from gear_items table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add currency field migration")
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
