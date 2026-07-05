"""Migration: Add catalogue_item_images table.

This migration adds the catalogue_item_images table for storing images
for global catalogue items.

Usage:
    python migrations/031_add_catalogue_item_images_table.py upgrade
    python migrations/031_add_catalogue_item_images_table.py downgrade
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
    """Create catalogue_item_images table."""
    print("Creating catalogue_item_images table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "catalogue_item_images")

        if table_exist:
            print("catalogue_item_images table already exists, skipping migration...")
            return

        print("Creating catalogue_item_images table...")
        await conn.execute(
            text(
                """
                CREATE TABLE catalogue_item_images (
                    id VARCHAR(36) PRIMARY KEY,
                    catalogue_item_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36) NOT NULL,
                    storage_type VARCHAR(10) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type VARCHAR(50) NOT NULL,
                    external_url VARCHAR(1000),
                    width INTEGER,
                    height INTEGER,
                    is_primary BOOLEAN NOT NULL DEFAULT false,
                    "order" INTEGER NOT NULL DEFAULT 0,
                    is_processed BOOLEAN NOT NULL DEFAULT false,
                    original_file_size INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_catalogue_item_images_catalogue_item_id
                        FOREIGN KEY (catalogue_item_id)
                        REFERENCES global_catalogue_items(id)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_catalogue_item_images_user_id
                        FOREIGN KEY (user_id)
                        REFERENCES users(id)
                );
            """
            ),
        )

        # Create indexes
        print("Creating indexes...")
        await conn.execute(
            text(
                "CREATE INDEX ix_catalogue_item_images_catalogue_item_id ON catalogue_item_images(catalogue_item_id);"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX ix_catalogue_item_images_user_id ON catalogue_item_images(user_id);"
            )
        )

        print("✓ Created catalogue_item_images table with indexes")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Drop catalogue_item_images table."""
    print("Dropping catalogue_item_images table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "catalogue_item_images")

        if not table_exist:
            print("catalogue_item_images table does not exist, skipping downgrade...")
            return

        print("catalogue_item_images table exists, removing it...")
        # Drop indexes
        print("Dropping indexes...")
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_catalogue_item_images_user_id;")
        )
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_catalogue_item_images_catalogue_item_id;")
        )

        # Drop table
        print("Dropping table...")
        await conn.execute(text("DROP TABLE IF EXISTS catalogue_item_images CASCADE;"))

        print("✓ Removed catalogue_item_images table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add catalogue_item_images table migration"
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
