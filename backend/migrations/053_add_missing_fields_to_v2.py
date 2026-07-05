"""Migration: Add missing fields to gear_items_v2 table.

This migration adds three fields to gear_items_v2 table:
- is_hidden_by_reports (Boolean) - for containers (content reporting system)
- promote_count (Integer) - for items (promotion to catalogue)
- shelf_life (JSONB) - for items (shelf life tracking)

These fields were added to V1 models after V2 was created, so they need to be backported.

Usage:
    python migrations/049_add_missing_fields_to_v2.py upgrade
    python migrations/049_add_missing_fields_to_v2.py downgrade
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


async def index_exists(conn, index_name: str) -> bool:
    """Check if an index exists in the database.

    Args:
        conn: Database connection
        index_name: Name of the index

    Returns:
        True if index exists, False otherwise
    """
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND indexname = :index_name
            );
        """
        ),
        {"index_name": index_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Add missing fields to gear_items_v2 table."""
    print("Adding missing fields to gear_items_v2 table...")

    async with engine.begin() as conn:
        # Check if gear_items_v2 table exists
        v2_exists = await table_exists(conn, "gear_items_v2")

        if not v2_exists:
            print("gear_items_v2 table does not exist, skipping migration...")
            print(
                "Note: Table will be created with all fields when created from models"
            )
            return

        # Add is_hidden_by_reports column (container-specific)
        if not await column_exists(conn, "gear_items_v2", "is_hidden_by_reports"):
            print("Adding is_hidden_by_reports column to gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items_v2
                    ADD COLUMN is_hidden_by_reports BOOLEAN DEFAULT FALSE;
                """
                )
            )
            print("✓ Added is_hidden_by_reports column")
        else:
            print("is_hidden_by_reports column already exists, skipping...")

        # Create index on is_hidden_by_reports
        if not await index_exists(conn, "ix_gear_items_v2_is_hidden_by_reports"):
            print("Creating index on is_hidden_by_reports...")
            await conn.execute(
                text(
                    """
                    CREATE INDEX ix_gear_items_v2_is_hidden_by_reports
                    ON gear_items_v2 (is_hidden_by_reports);
                """
                )
            )
            print("✓ Created index on is_hidden_by_reports")
        else:
            print("Index on is_hidden_by_reports already exists, skipping...")

        # Add promote_count column (item-specific)
        if not await column_exists(conn, "gear_items_v2", "promote_count"):
            print("Adding promote_count column to gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items_v2
                    ADD COLUMN promote_count INTEGER DEFAULT 0;
                """
                )
            )
            print("✓ Added promote_count column")
        else:
            print("promote_count column already exists, skipping...")

        # Add shelf_life column (item-specific)
        if not await column_exists(conn, "gear_items_v2", "shelf_life"):
            print("Adding shelf_life column to gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items_v2
                    ADD COLUMN shelf_life JSONB;
                """
                )
            )
            print("✓ Added shelf_life column")
        else:
            print("shelf_life column already exists, skipping...")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove missing fields from gear_items_v2 table."""
    print("Removing fields from gear_items_v2 table...")

    async with engine.begin() as conn:
        # Remove shelf_life column
        if await column_exists(conn, "gear_items_v2", "shelf_life"):
            print("Removing shelf_life column from gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items_v2
                    DROP COLUMN IF EXISTS shelf_life;
                """
                )
            )
            print("✓ Removed shelf_life column")
        else:
            print("shelf_life column does not exist, skipping...")

        # Remove promote_count column
        if await column_exists(conn, "gear_items_v2", "promote_count"):
            print("Removing promote_count column from gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items_v2
                    DROP COLUMN IF EXISTS promote_count;
                """
                )
            )
            print("✓ Removed promote_count column")
        else:
            print("promote_count column does not exist, skipping...")

        # Drop index on is_hidden_by_reports
        if await index_exists(conn, "ix_gear_items_v2_is_hidden_by_reports"):
            print("Dropping index on is_hidden_by_reports...")
            await conn.execute(
                text(
                    """
                    DROP INDEX IF EXISTS ix_gear_items_v2_is_hidden_by_reports;
                """
                )
            )
            print("✓ Dropped index on is_hidden_by_reports")
        else:
            print("Index on is_hidden_by_reports does not exist, skipping...")

        # Remove is_hidden_by_reports column
        if await column_exists(conn, "gear_items_v2", "is_hidden_by_reports"):
            print("Removing is_hidden_by_reports column from gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    ALTER TABLE gear_items_v2
                    DROP COLUMN IF EXISTS is_hidden_by_reports;
                """
                )
            )
            print("✓ Removed is_hidden_by_reports column")
        else:
            print("is_hidden_by_reports column does not exist, skipping...")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add missing fields to gear_items_v2 migration"
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
