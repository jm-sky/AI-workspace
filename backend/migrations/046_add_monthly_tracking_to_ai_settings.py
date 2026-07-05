"""Migration: Add monthly tracking columns to ai_user_settings.

This migration adds the missing monthly usage tracking columns to the
ai_user_settings table that were never added in the initial migration.

Columns added:
- monthly_token_limit: Optional limit for monthly token usage
- monthly_tokens_used: Counter for tokens used this month
- monthly_cost_limit: Optional limit for monthly costs (in USD)
- monthly_cost_used: Counter for costs incurred this month (in USD)

Usage:
    python migrations/046_add_monthly_tracking_to_ai_settings.py upgrade
    python migrations/046_add_monthly_tracking_to_ai_settings.py downgrade
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
    """Add monthly tracking columns to ai_user_settings table."""
    print("Adding monthly tracking columns to ai_user_settings...")

    async with engine.begin() as conn:
        columns_to_add = [
            ("monthly_token_limit", "INTEGER NULL"),
            ("monthly_tokens_used", "INTEGER NOT NULL DEFAULT 0"),
            ("monthly_cost_limit", "REAL NULL"),
            ("monthly_cost_used", "REAL NOT NULL DEFAULT 0.0"),
        ]

        for column_name, column_def in columns_to_add:
            exists = await column_exists(conn, "ai_user_settings", column_name)
            if not exists:
                print(f"Adding column {column_name}...")
                await conn.execute(
                    text(
                        f"ALTER TABLE ai_user_settings ADD COLUMN {column_name} {column_def}"
                    )
                )
                print(f"✓ Added column {column_name}")
            else:
                print(f"Column {column_name} already exists, skipping...")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove monthly tracking columns from ai_user_settings table."""
    print("Removing monthly tracking columns from ai_user_settings...")

    async with engine.begin() as conn:
        columns_to_drop = [
            "monthly_token_limit",
            "monthly_tokens_used",
            "monthly_cost_limit",
            "monthly_cost_used",
        ]

        for column_name in columns_to_drop:
            exists = await column_exists(conn, "ai_user_settings", column_name)
            if exists:
                print(f"Dropping column {column_name}...")
                await conn.execute(
                    text(f"ALTER TABLE ai_user_settings DROP COLUMN {column_name}")
                )
                print(f"✓ Dropped column {column_name}")
            else:
                print(f"Column {column_name} does not exist, skipping...")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add monthly tracking to ai_user_settings migration"
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
