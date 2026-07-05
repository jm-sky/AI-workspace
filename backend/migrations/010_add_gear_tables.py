"""Migration: Add gear_containers and gear_items tables.

This migration creates the tables for gear management system.

Usage:
    python migrations/002_add_gear_tables.py upgrade
    python migrations/002_add_gear_tables.py downgrade

Note:
    If using `init_db()` from database.py, this migration is not needed
    as the tables will be created automatically from the SQLAlchemy models.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, engine
from app.modules.gear.db_models import GearContainerDB, GearItemDB  # noqa: F401


async def upgrade() -> None:
    """Create gear_containers and gear_items tables."""
    print("Creating gear tables...")

    async with engine.begin() as conn:
        # Create gear tables
        await conn.run_sync(GearContainerDB.metadata.create_all)
        await conn.run_sync(GearItemDB.metadata.create_all)

    print("✓ gear_containers table created successfully")
    print("✓ gear_items table created successfully")


async def downgrade() -> None:
    """Drop gear_containers and gear_items tables."""
    print("Dropping gear tables...")

    async with engine.begin() as conn:
        await conn.run_sync(GearItemDB.metadata.drop_all)
        await conn.run_sync(GearContainerDB.metadata.drop_all)

    print("✓ gear_items table dropped successfully")
    print("✓ gear_containers table dropped successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Gear tables migration")
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
