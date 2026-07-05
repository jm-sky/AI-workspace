"""Migration: Add max_tokens and temperature fields to ai_user_settings table.

This migration adds the following fields to ai_user_settings:
- max_tokens (INTEGER, nullable)
- temperature (REAL, NOT NULL, default 1.0)

Usage:
    python migrations/037_add_max_tokens_and_temperature_to_ai_settings.py upgrade
    python migrations/037_add_max_tokens_and_temperature_to_ai_settings.py downgrade
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
    """Add max_tokens and temperature columns to ai_user_settings table."""
    print("Adding max_tokens and temperature fields to ai_user_settings table...")

    async with engine.begin() as conn:
        # Add max_tokens column if it doesn't exist
        if not await column_exists(conn, "ai_user_settings", "max_tokens"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE ai_user_settings
                    ADD COLUMN max_tokens INTEGER NULL;
                """
                )
            )
            print("✓ Added max_tokens field to ai_user_settings table")
        else:
            print("max_tokens column already exists, skipping...")

        # Add temperature column if it doesn't exist
        if not await column_exists(conn, "ai_user_settings", "temperature"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE ai_user_settings
                    ADD COLUMN temperature REAL NOT NULL DEFAULT 1.0;
                """
                )
            )
            print("✓ Added temperature field to ai_user_settings table")
        else:
            print("temperature column already exists, skipping...")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove max_tokens and temperature columns from ai_user_settings table."""
    print("Removing max_tokens and temperature fields from ai_user_settings table...")

    async with engine.begin() as conn:
        # Remove temperature column if it exists
        if await column_exists(conn, "ai_user_settings", "temperature"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE ai_user_settings
                    DROP COLUMN temperature;
                """
                )
            )
            print("✓ Removed temperature field from ai_user_settings table")
        else:
            print("temperature column does not exist, skipping downgrade...")

        # Remove max_tokens column if it exists
        if await column_exists(conn, "ai_user_settings", "max_tokens"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE ai_user_settings
                    DROP COLUMN max_tokens;
                """
                )
            )
            print("✓ Removed max_tokens field from ai_user_settings table")
        else:
            print("max_tokens column does not exist, skipping downgrade...")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add max_tokens and temperature to ai_user_settings migration"
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
