"""Migration: Increase preferred_weight_unit column length.

This migration increases the preferred_weight_unit column length from VARCHAR(5) to VARCHAR(10)
to support new auto weight unit options (auto-g-kg, auto-oz-lb).

Usage:
    python migrations/042_increase_preferred_weight_unit_length.py upgrade
    python migrations/042_increase_preferred_weight_unit_length.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table (PostgreSQL compatible)."""
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
    """Increase preferred_weight_unit column length from VARCHAR(5) to VARCHAR(10)."""
    print("Increasing preferred_weight_unit column length...")

    async with engine.begin() as conn:
        # Check if column exists
        if not await column_exists(conn, "gear_settings", "preferred_weight_unit"):
            print("preferred_weight_unit column does not exist, skipping migration...")
            return

        # Alter column to increase length
        print("Altering preferred_weight_unit column...")
        await conn.execute(
            text(
                """
                ALTER TABLE gear_settings
                ALTER COLUMN preferred_weight_unit TYPE VARCHAR(10);
            """
            )
        )
        print("✓ Increased preferred_weight_unit column length to VARCHAR(10)")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Decrease preferred_weight_unit column length from VARCHAR(10) to VARCHAR(5)."""
    print("Decreasing preferred_weight_unit column length...")

    async with engine.begin() as conn:
        # Check if column exists
        if not await column_exists(conn, "gear_settings", "preferred_weight_unit"):
            print("preferred_weight_unit column does not exist, skipping downgrade...")
            return

        # Check if there are any values longer than 5 characters
        result = await conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM gear_settings
                WHERE preferred_weight_unit IS NOT NULL
                AND LENGTH(preferred_weight_unit) > 5;
            """
            )
        )
        long_values_count = result.scalar() or 0

        if long_values_count > 0:
            print(
                f"⚠ Warning: {long_values_count} rows have preferred_weight_unit values longer than 5 characters."
            )
            print("These values will be truncated. Consider updating them first.")
            # Truncate values longer than 5 characters
            await conn.execute(
                text(
                    """
                    UPDATE gear_settings
                    SET preferred_weight_unit = LEFT(preferred_weight_unit, 5)
                    WHERE preferred_weight_unit IS NOT NULL
                    AND LENGTH(preferred_weight_unit) > 5;
                """
                )
            )
            print("✓ Truncated values longer than 5 characters")

        # Alter column to decrease length
        print("Altering preferred_weight_unit column...")
        await conn.execute(
            text(
                """
                ALTER TABLE gear_settings
                ALTER COLUMN preferred_weight_unit TYPE VARCHAR(5);
            """
            )
        )
        print("✓ Decreased preferred_weight_unit column length to VARCHAR(5)")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Increase preferred_weight_unit column length migration"
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
