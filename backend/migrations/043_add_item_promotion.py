"""Migration: Add item promotion to catalogue.

This migration adds the promote_count field to gear_items table and creates
the item_promotions table for tracking item promotions to the global catalogue.

Usage:
    python migrations/043_add_item_promotion.py upgrade
    python migrations/043_add_item_promotion.py downgrade
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
    """Add promote_count field and create item_promotions table."""
    print("Adding item promotion support...")

    async with engine.begin() as conn:
        # Check if gear_items table exists
        items_exist = await table_exists(conn, "gear_items")

        if not items_exist:
            print("gear_items table does not exist, skipping migration...")
            print(
                "Note: Table will be created with promote_count field when created from models"
            )
            return

        # Add promote_count column to gear_items if it doesn't exist
        if not await column_exists(conn, "gear_items", "promote_count"):
            print("Adding promote_count column to gear_items table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items
                    ADD COLUMN promote_count INTEGER NOT NULL DEFAULT 0;
                """
                )
            )
            print("✓ Added promote_count column to gear_items table")
        else:
            print("promote_count column already exists, skipping...")

        # Create item_promotions table if it doesn't exist
        promotions_exist = await table_exists(conn, "item_promotions")

        if promotions_exist:
            print("item_promotions table already exists, skipping migration...")
            return

        print("Creating item_promotions table...")
        await conn.execute(
            text(
                """
                CREATE TABLE item_promotions (
                    id VARCHAR(36) PRIMARY KEY,
                    item_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_item_promotions_item_id
                        FOREIGN KEY (item_id)
                        REFERENCES gear_items(id)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_item_promotions_user_id
                        FOREIGN KEY (user_id)
                        REFERENCES users(id)
                        ON DELETE CASCADE,
                    CONSTRAINT unique_item_user_promotion
                        UNIQUE (item_id, user_id)
                );
            """
            ),
        )

        # Create indexes
        print("Creating indexes...")
        await conn.execute(
            text("CREATE INDEX ix_item_promotions_item_id ON item_promotions(item_id);")
        )
        await conn.execute(
            text("CREATE INDEX ix_item_promotions_user_id ON item_promotions(user_id);")
        )

        print("✓ Created item_promotions table with indexes")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove promote_count field and drop item_promotions table."""
    print("Removing item promotion support...")

    async with engine.begin() as conn:
        # Drop item_promotions table
        promotions_exist = await table_exists(conn, "item_promotions")
        if promotions_exist:
            print("Dropping item_promotions table...")
            await conn.execute(text("DROP TABLE IF EXISTS item_promotions CASCADE;"))
            print("✓ Dropped item_promotions table")
        else:
            print("item_promotions table does not exist, skipping...")

        # Remove promote_count column from gear_items
        if await column_exists(conn, "gear_items", "promote_count"):
            print("Removing promote_count column from gear_items table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items
                    DROP COLUMN IF EXISTS promote_count;
                """
                )
            )
            print("✓ Removed promote_count column from gear_items table")
        else:
            print("promote_count column does not exist, skipping...")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add item promotion migration")
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
