"""Migration: Add global_catalogue_items table.

This migration adds the global_catalogue_items table for storing template items
that users can add to their containers.

Usage:
    python migrations/029_add_global_catalogue_items.py upgrade
    python migrations/029_add_global_catalogue_items.py downgrade
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


async def upgrade() -> None:
    """Create global_catalogue_items table."""
    print("Creating global_catalogue_items table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "global_catalogue_items")

        if table_exist:
            print("global_catalogue_items table already exists, skipping migration...")
            return

        print("Creating global_catalogue_items table...")
        await conn.execute(
            text(
                """
                CREATE TABLE global_catalogue_items (
                    id VARCHAR(36) PRIMARY KEY,
                    version INTEGER NOT NULL DEFAULT 1,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    weight FLOAT NOT NULL,
                    weight_unit VARCHAR(5) NOT NULL DEFAULT 'g',
                    description TEXT,
                    brand VARCHAR(255),
                    model VARCHAR(255),
                    price_tier VARCHAR(20),
                    quality VARCHAR(20),
                    url TEXT,
                    color VARCHAR(50),
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    created_by VARCHAR(36),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_global_catalogue_items_created_by
                        FOREIGN KEY (created_by)
                        REFERENCES users(id)
                        ON DELETE SET NULL
                );
            """
            ),
        )

        # Create indexes
        print("Creating indexes...")
        await conn.execute(
            text(
                "CREATE INDEX ix_global_catalogue_items_name ON global_catalogue_items(name);"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX ix_global_catalogue_items_category ON global_catalogue_items(category);"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX ix_global_catalogue_items_brand ON global_catalogue_items(brand);"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX ix_global_catalogue_items_is_active ON global_catalogue_items(is_active);"
            )
        )

        print("✓ Created global_catalogue_items table with indexes")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Drop global_catalogue_items table."""
    print("Dropping global_catalogue_items table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "global_catalogue_items")

        if not table_exist:
            print("global_catalogue_items table does not exist, skipping downgrade...")
            return

        print("global_catalogue_items table exists, removing it...")
        # Drop indexes
        print("Dropping indexes...")
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_global_catalogue_items_is_active;")
        )
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_global_catalogue_items_brand;")
        )
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_global_catalogue_items_category;")
        )
        await conn.execute(text("DROP INDEX IF EXISTS ix_global_catalogue_items_name;"))

        # Drop table
        print("Dropping table...")
        await conn.execute(text("DROP TABLE IF EXISTS global_catalogue_items CASCADE;"))

        print("✓ Removed global_catalogue_items table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add global_catalogue_items table migration"
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
