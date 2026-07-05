"""Migration: Add container_ratings table.

This migration adds the container_ratings table for storing container ratings.
Supports two types of ratings:
- 'owner': Rating given by container owner
- 'user': Rating given by other users (for public containers)

Usage:
    python migrations/027_add_container_ratings.py upgrade
    python migrations/027_add_container_ratings.py downgrade
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
    """Create container_ratings table."""
    print("Creating container_ratings table...")

    async with engine.begin() as conn:
        ratings_exist = await table_exists(conn, "container_ratings")

        if ratings_exist:
            print("container_ratings table already exists, skipping migration...")
            return

        print("Creating container_ratings table...")
        # Create container_ratings table
        await conn.execute(
            text(
                """
                CREATE TABLE container_ratings (
                    id VARCHAR(36) PRIMARY KEY,
                    container_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36) NOT NULL,
                    rating INTEGER NOT NULL,
                    rating_type VARCHAR(10) NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    CONSTRAINT fk_container_ratings_container 
                        FOREIGN KEY (container_id) 
                        REFERENCES gear_containers(id) 
                        ON DELETE CASCADE,
                    CONSTRAINT fk_container_ratings_user 
                        FOREIGN KEY (user_id) 
                        REFERENCES users(id) 
                        ON DELETE CASCADE,
                    CONSTRAINT uq_container_rating_user_type 
                        UNIQUE (container_id, user_id, rating_type),
                    CONSTRAINT check_rating_range 
                        CHECK (rating >= 1 AND rating <= 5),
                    CONSTRAINT check_rating_type 
                        CHECK (rating_type IN ('owner', 'user'))
                );
            """
            )
        )

        # Create indexes
        await conn.execute(
            text(
                """
                CREATE INDEX ix_container_ratings_container_id 
                    ON container_ratings(container_id);
            """
            )
        )

        await conn.execute(
            text(
                """
                CREATE INDEX ix_container_ratings_user_id 
                    ON container_ratings(user_id);
            """
            )
        )

        await conn.execute(
            text(
                """
                CREATE INDEX ix_container_ratings_rating_type 
                    ON container_ratings(rating_type);
            """
            )
        )

        await conn.execute(
            text(
                """
                CREATE INDEX ix_container_ratings_container_type 
                    ON container_ratings(container_id, rating_type);
            """
            )
        )

        print("✓ Created container_ratings table with indexes")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove container_ratings table."""
    print("Removing container_ratings table...")

    async with engine.begin() as conn:
        ratings_exist = await table_exists(conn, "container_ratings")

        if not ratings_exist:
            print("container_ratings table does not exist, skipping downgrade...")
            return

        print("container_ratings table exists, removing it...")
        # Drop table (cascade will handle foreign keys)
        await conn.execute(
            text(
                """
                DROP TABLE IF EXISTS container_ratings CASCADE;
            """
            )
        )
        print("✓ Removed container_ratings table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add container_ratings table migration"
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
