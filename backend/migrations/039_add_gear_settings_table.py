"""Migration: Add gear_settings table.

This migration creates a table for storing user-specific gear settings including:
- Custom categories
- Custom container types
- Custom brands
- Preferred weight unit
- Default currency

Usage:
    python migrations/039_add_gear_settings_table.py upgrade
    python migrations/039_add_gear_settings_table.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database (PostgreSQL compatible)."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Create gear_settings table."""
    print("Creating gear_settings table...")

    async with engine.begin() as conn:
        # Check if table already exists
        if await table_exists(conn, "gear_settings"):
            print("gear_settings table already exists, skipping migration...")
            return

        # Create gear_settings table
        print("Creating gear_settings table...")
        await conn.execute(
            text(
                """
                CREATE TABLE gear_settings (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL UNIQUE,
                    custom_categories JSON NOT NULL DEFAULT '[]',
                    custom_container_types JSON NOT NULL DEFAULT '[]',
                    custom_brands JSON NOT NULL DEFAULT '[]',
                    preferred_weight_unit VARCHAR(5),
                    default_currency VARCHAR(10),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """
            )
        )
        await conn.execute(
            text("CREATE INDEX ix_gear_settings_user_id ON gear_settings(user_id)")
        )
        print("✓ Created gear_settings table")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Drop gear_settings table."""
    print("Dropping gear_settings table...")

    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS gear_settings CASCADE"))
        print("✓ Dropped gear_settings table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add gear_settings table migration")
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
