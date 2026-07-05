"""Migration: Add public containers and default containers public setting.

This migration adds the following fields:
- gear_containers: is_public (boolean, default False, indexed)
- user_settings: default_containers_public (boolean, default False)

Usage:
    python migrations/013_add_public_containers_and_settings.py upgrade
    python migrations/013_add_public_containers_and_settings.py downgrade
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
    """Add public containers and default containers public setting."""
    print("Adding public containers and default containers public setting...")

    async with engine.begin() as conn:
        # Add is_public to gear_containers
        containers_exist = await table_exists(conn, "gear_containers")
        if containers_exist:
            is_public_exists = await column_exists(conn, "gear_containers", "is_public")
            if not is_public_exists:
                print("Adding is_public column to gear_containers...")
                await conn.execute(
                    text(
                        """
                    ALTER TABLE gear_containers 
                    ADD COLUMN is_public BOOLEAN DEFAULT FALSE NOT NULL;
                """
                    )
                )
                # Create index for better query performance
                await conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS ix_gear_containers_is_public 
                    ON gear_containers(is_public);
                """
                    )
                )
                print("✓ Added is_public column to gear_containers")
            else:
                print("✓ is_public column already exists in gear_containers")
        else:
            print("gear_containers table does not exist, skipping...")

        # Add default_containers_public to user_settings
        settings_exist = await table_exists(conn, "user_settings")
        if settings_exist:
            default_public_exists = await column_exists(
                conn, "user_settings", "default_containers_public"
            )
            if not default_public_exists:
                print("Adding default_containers_public column to user_settings...")
                await conn.execute(
                    text(
                        """
                    ALTER TABLE user_settings 
                    ADD COLUMN default_containers_public BOOLEAN DEFAULT FALSE NOT NULL;
                """
                    )
                )
                print("✓ Added default_containers_public column to user_settings")
            else:
                print(
                    "✓ default_containers_public column already exists in user_settings"
                )
        else:
            print("user_settings table does not exist, skipping...")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove public containers and default containers public setting."""
    print("Removing public containers and default containers public setting...")

    async with engine.begin() as conn:
        # Remove is_public from gear_containers
        containers_exist = await table_exists(conn, "gear_containers")
        if containers_exist:
            is_public_exists = await column_exists(conn, "gear_containers", "is_public")
            if is_public_exists:
                # Drop index first
                await conn.execute(
                    text(
                        """
                    DROP INDEX IF EXISTS ix_gear_containers_is_public;
                """
                    )
                )
                # Drop column
                await conn.execute(
                    text(
                        """
                    ALTER TABLE gear_containers 
                    DROP COLUMN IF EXISTS is_public;
                """
                    )
                )
                print("✓ Removed is_public column from gear_containers")
            else:
                print("✓ is_public column does not exist in gear_containers")

        # Remove default_containers_public from user_settings
        settings_exist = await table_exists(conn, "user_settings")
        if settings_exist:
            default_public_exists = await column_exists(
                conn, "user_settings", "default_containers_public"
            )
            if default_public_exists:
                await conn.execute(
                    text(
                        """
                    ALTER TABLE user_settings 
                    DROP COLUMN IF EXISTS default_containers_public;
                """
                    )
                )
                print("✓ Removed default_containers_public column from user_settings")
            else:
                print(
                    "✓ default_containers_public column does not exist in user_settings"
                )

    print("✓ Migration downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add public containers and settings migration"
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
