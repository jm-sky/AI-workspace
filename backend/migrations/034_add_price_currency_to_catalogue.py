"""Migration: Add price and currency fields to global_catalogue_items table.

This migration adds price and currency fields to the global_catalogue_items table
to support price information in catalogue items.

Usage:
    python migrations/034_add_price_currency_to_catalogue.py upgrade
    python migrations/034_add_price_currency_to_catalogue.py downgrade
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
    """Add price and currency columns to global_catalogue_items table."""
    print("Adding price and currency fields to global_catalogue_items table...")

    async with engine.begin() as conn:
        price_exists = await column_exists(conn, "global_catalogue_items", "price")
        currency_exists = await column_exists(
            conn, "global_catalogue_items", "currency"
        )

        if price_exists and currency_exists:
            print("price and currency columns already exist, skipping migration...")
            return

        if not price_exists:
            print("Adding price column...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE global_catalogue_items
                    ADD COLUMN price FLOAT;
                """
                ),
            )

        if not currency_exists:
            print("Adding currency column...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE global_catalogue_items
                    ADD COLUMN currency VARCHAR(10);
                """
                ),
            )

        print("✓ Added price and currency fields to global_catalogue_items table")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove price and currency columns from global_catalogue_items table."""
    print("Removing price and currency fields from global_catalogue_items table...")

    async with engine.begin() as conn:
        price_exists = await column_exists(conn, "global_catalogue_items", "price")
        currency_exists = await column_exists(
            conn, "global_catalogue_items", "currency"
        )

        if not price_exists and not currency_exists:
            print("price and currency columns do not exist, skipping downgrade...")
            return

        if price_exists:
            print("Removing price column...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE global_catalogue_items
                    DROP COLUMN price;
                """
                ),
            )

        if currency_exists:
            print("Removing currency column...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE global_catalogue_items
                    DROP COLUMN currency;
                """
                ),
            )

        print("✓ Removed price and currency fields from global_catalogue_items table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add price and currency to global_catalogue_items migration"
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
