"""Migration: Remove subscription_history event_type constraint.

The constraint was too restrictive and didn't allow dynamic event types
like 'admin_cancel_plan_tier', 'subscription_activated', etc.

Usage:
    python migrations/048_remove_subscription_history_event_type_constraint.py upgrade
    python migrations/048_remove_subscription_history_event_type_constraint.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if table exists (PostgreSQL compatible)."""
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


async def constraint_exists(conn, table_name: str, constraint_name: str) -> bool:
    """Check if constraint exists."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.table_constraints
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND constraint_name = :constraint_name
            );
        """
        ),
        {"table_name": table_name, "constraint_name": constraint_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Remove event_type constraint from subscription_history table."""
    print("Removing subscription_history event_type constraint...")

    async with engine.begin() as conn:
        if await table_exists(conn, "subscription_history"):
            if await constraint_exists(
                conn, "subscription_history", "valid_event_type"
            ):
                await conn.execute(
                    text(
                        """
                        ALTER TABLE subscription_history
                        DROP CONSTRAINT valid_event_type
                    """
                    )
                )
                print("✓ Removed valid_event_type constraint")
            else:
                print("✓ Constraint already removed")
        else:
            print("⚠ Table subscription_history does not exist")

    print("✅ Migration completed successfully")


async def downgrade() -> None:
    """Re-add event_type constraint (with original values only)."""
    print("Re-adding subscription_history event_type constraint...")

    async with engine.begin() as conn:
        if await table_exists(conn, "subscription_history"):
            # Drop constraint if exists (idempotent)
            await conn.execute(
                text(
                    """
                    ALTER TABLE subscription_history
                    DROP CONSTRAINT IF EXISTS valid_event_type
                """
                )
            )

            # Re-add original constraint
            await conn.execute(
                text(
                    """
                    ALTER TABLE subscription_history
                    ADD CONSTRAINT valid_event_type
                    CHECK (event_type IN ('created', 'updated', 'canceled', 'renewed', 'payment_failed'))
                """
                )
            )
            print("✓ Re-added valid_event_type constraint")
        else:
            print("⚠ Table subscription_history does not exist")

    print("✅ Rollback completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove subscription_history event_type constraint"
    )
    parser.add_argument("action", choices=["upgrade", "downgrade"])
    args = parser.parse_args()

    if args.action == "upgrade":
        await upgrade()
    elif args.action == "downgrade":
        await downgrade()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
