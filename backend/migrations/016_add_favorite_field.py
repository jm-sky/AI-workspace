"""Migration: Add favorite field to gear_containers table.

This migration adds the favorite field to gear_containers table for marking favorite containers.

Usage:
    python migrations/016_add_favorite_field.py upgrade
    python migrations/016_add_favorite_field.py downgrade
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
    """Add favorite field to gear_containers table."""
    print("Adding favorite field to gear_containers table...")

    async with engine.begin() as conn:
        containers_exist = await table_exists(conn, "gear_containers")

        if not containers_exist:
            print("gear_containers table does not exist, skipping migration...")
            print(
                "Note: Table will be created with favorite field when created from models"
            )
            return

        favorite_exists = await column_exists(conn, "gear_containers", "favorite")

        if favorite_exists:
            print("favorite column already exists, skipping migration...")
            return

        print("gear_containers table exists, adding favorite field...")
        # Add favorite field to gear_containers
        await conn.execute(
            text(
                """
                ALTER TABLE gear_containers 
                ADD COLUMN favorite BOOLEAN NOT NULL DEFAULT FALSE;
            """
            )
        )
        print("✓ Added favorite field to gear_containers table")

        # Add index for better query performance
        await conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_gear_containers_favorite 
                ON gear_containers(favorite);
            """
            )
        )
        print("✓ Added index on favorite field")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove favorite field from gear_containers table."""
    print("Removing favorite field from gear_containers table...")

    async with engine.begin() as conn:
        # Remove index first
        await conn.execute(
            text(
                """
                DROP INDEX IF EXISTS ix_gear_containers_favorite;
            """
            )
        )
        print("✓ Removed index on favorite field")

        # Remove favorite field from gear_containers
        await conn.execute(
            text(
                """
                ALTER TABLE gear_containers 
                DROP COLUMN IF EXISTS favorite;
            """
            )
        )
        print("✓ Removed favorite field from gear_containers table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add favorite field migration")
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
