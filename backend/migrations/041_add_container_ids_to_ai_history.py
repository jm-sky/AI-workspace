"""Migration: Add container_ids column to ai_history table.

This migration adds a container_ids column to ai_history table:
- Adds: container_ids JSONB column (nullable)
- Populates: container_ids from input_data.context keys (container IDs)

Usage:
    python migrations/041_add_container_ids_to_ai_history.py upgrade
    python migrations/041_add_container_ids_to_ai_history.py downgrade
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
    """Add container_ids column to ai_history table."""
    print("Adding container_ids column to ai_history table...")

    async with engine.begin() as conn:
        # Check if table exists
        table_exists_result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'ai_history'
                );
            """
            )
        )
        if not table_exists_result.scalar():
            print("ai_history table does not exist, skipping migration...")
            return

        # Check if column already exists
        if await column_exists(conn, "ai_history", "container_ids"):
            print("container_ids column already exists, skipping migration...")
            return

        # Step 1: Add column
        print("  Adding container_ids column...")
        await conn.execute(
            text("ALTER TABLE ai_history ADD COLUMN container_ids JSONB")
        )

        # Step 2: Populate container_ids from input_data.context keys
        print("  Populating container_ids from input_data.context...")
        # Extract keys from input_data.context object (these are container IDs)
        # input_data structure: {"message": "...", "context": {"container-id-1": {...}, "container-id-2": {...}}}
        await conn.execute(
            text(
                """
                UPDATE ai_history
                SET container_ids = (
                    SELECT COALESCE(jsonb_agg(key), '[]'::jsonb)
                    FROM jsonb_each(input_data->'context')
                    WHERE input_data->'context' IS NOT NULL
                      AND jsonb_typeof(input_data->'context') = 'object'
                )
                WHERE input_data->'context' IS NOT NULL
                  AND jsonb_typeof(input_data->'context') = 'object'
                  AND container_ids IS NULL
            """
            )
        )

        print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove container_ids column from ai_history table."""
    print("Removing container_ids column from ai_history table...")

    async with engine.begin() as conn:
        # Check if table exists
        table_exists_result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'ai_history'
                );
            """
            )
        )
        if not table_exists_result.scalar():
            print("ai_history table does not exist, skipping downgrade...")
            return

        # Check if column exists
        if not await column_exists(conn, "ai_history", "container_ids"):
            print("container_ids column does not exist, skipping downgrade...")
            return

        # Drop column
        print("  Dropping container_ids column...")
        await conn.execute(text("ALTER TABLE ai_history DROP COLUMN container_ids"))

        print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add container_ids column to ai_history table"
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
