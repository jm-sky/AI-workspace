"""Migration: Add item_images table for image uploads.

This migration creates the item_images table for storing uploaded gear item images.

Usage:
    python migrations/017_add_item_images_table.py upgrade
    python migrations/017_add_item_images_table.py downgrade
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


async def upgrade() -> None:
    """Create item_images table."""
    print("Creating item_images table...")

    async with engine.begin() as conn:
        # Check if table already exists
        if await table_exists(conn, "item_images"):
            print("item_images table already exists, skipping migration...")
            return

        # Create item_images table
        await conn.execute(
            text(
                """
                CREATE TABLE item_images (
                    id VARCHAR(36) PRIMARY KEY,
                    item_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36) NOT NULL,

                    -- Storage info
                    storage_type VARCHAR(10) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type VARCHAR(50) NOT NULL,

                    -- Image metadata
                    width INTEGER,
                    height INTEGER,
                    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
                    "order" INTEGER NOT NULL DEFAULT 0,

                    -- Processing flags
                    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
                    original_file_size INTEGER,

                    -- Timestamps
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    -- Foreign keys
                    CONSTRAINT fk_item_images_item_id FOREIGN KEY (item_id)
                        REFERENCES gear_items(id) ON DELETE CASCADE,
                    CONSTRAINT fk_item_images_user_id FOREIGN KEY (user_id)
                        REFERENCES users(id)
                );
            """
            )
        )
        print("✓ Created item_images table")

        # Create indexes for better query performance
        await conn.execute(
            text(
                """
                CREATE INDEX ix_item_images_item_id ON item_images(item_id);
            """
            )
        )
        print("✓ Created index on item_id")

        await conn.execute(
            text(
                """
                CREATE INDEX ix_item_images_user_id ON item_images(user_id);
            """
            )
        )
        print("✓ Created index on user_id")

        await conn.execute(
            text(
                """
                CREATE INDEX ix_item_images_order ON item_images(item_id, "order");
            """
            )
        )
        print("✓ Created index on item_id and order")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Drop item_images table."""
    print("Dropping item_images table...")

    async with engine.begin() as conn:
        # Drop indexes first
        await conn.execute(
            text(
                """
                DROP INDEX IF EXISTS ix_item_images_item_id;
            """
            )
        )
        print("✓ Dropped index on item_id")

        await conn.execute(
            text(
                """
                DROP INDEX IF EXISTS ix_item_images_user_id;
            """
            )
        )
        print("✓ Dropped index on user_id")

        await conn.execute(
            text(
                """
                DROP INDEX IF EXISTS ix_item_images_order;
            """
            )
        )
        print("✓ Dropped index on item_id and order")

        # Drop table
        await conn.execute(
            text(
                """
                DROP TABLE IF EXISTS item_images CASCADE;
            """
            )
        )
        print("✓ Dropped item_images table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add item_images table migration")
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
