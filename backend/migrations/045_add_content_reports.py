"""Migration: Add content_reports table and is_hidden_by_reports field.

This migration adds:
- content_reports table for reporting inappropriate content in public containers
- is_hidden_by_reports field to gear_containers table

Usage:
    python migrations/045_add_content_reports.py upgrade
    python migrations/045_add_content_reports.py downgrade
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


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table (PostgreSQL compatible).

    Args:
        conn: Database connection
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        True if column exists, False otherwise
    """
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
    """Add content_reports table and is_hidden_by_reports field."""
    print("Adding content reports support...")

    async with engine.begin() as conn:
        # Add is_hidden_by_reports column to gear_containers
        containers_exist = await table_exists(conn, "gear_containers")
        if containers_exist:
            if not await column_exists(conn, "gear_containers", "is_hidden_by_reports"):
                print("Adding is_hidden_by_reports column to gear_containers...")
                await conn.execute(
                    text(
                        """
                        ALTER TABLE gear_containers
                        ADD COLUMN is_hidden_by_reports BOOLEAN NOT NULL DEFAULT FALSE;
                    """
                    )
                )
                # Create index for better query performance
                await conn.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS ix_gear_containers_is_hidden_by_reports
                        ON gear_containers(is_hidden_by_reports);
                    """
                    )
                )
                print("✓ Added is_hidden_by_reports column to gear_containers")
            else:
                print("✓ is_hidden_by_reports column already exists in gear_containers")
        else:
            print("gear_containers table does not exist, skipping...")

        # Create content_reports table if it doesn't exist
        reports_exist = await table_exists(conn, "content_reports")

        if reports_exist:
            print("content_reports table already exists, skipping migration...")
            return

        print("Creating content_reports table...")
        await conn.execute(
            text(
                """
                CREATE TABLE content_reports (
                    id VARCHAR(36) PRIMARY KEY,
                    container_id VARCHAR(36) NOT NULL,
                    reporter_user_id VARCHAR(36) NOT NULL,
                    reason VARCHAR(50) NOT NULL,
                    additional_info TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP WITH TIME ZONE,
                    reviewed_by VARCHAR(36),
                    CONSTRAINT fk_content_reports_container
                        FOREIGN KEY (container_id)
                        REFERENCES gear_containers(id)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_content_reports_reporter
                        FOREIGN KEY (reporter_user_id)
                        REFERENCES users(id)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_content_reports_reviewer
                        FOREIGN KEY (reviewed_by)
                        REFERENCES users(id)
                        ON DELETE SET NULL,
                    CONSTRAINT unique_container_reporter
                        UNIQUE (container_id, reporter_user_id),
                    CONSTRAINT check_report_reason
                        CHECK (reason IN ('spam_fraud', 'violence', 'sexual_content', 'profanity', 'other')),
                    CONSTRAINT check_report_status
                        CHECK (status IN ('pending', 'reviewed', 'dismissed', 'action_taken'))
                );
            """
            ),
        )

        # Create indexes
        print("Creating indexes...")
        await conn.execute(
            text(
                """
                CREATE INDEX ix_content_reports_container_id
                ON content_reports(container_id);
            """
            )
        )
        await conn.execute(
            text(
                """
                CREATE INDEX ix_content_reports_reporter_user_id
                ON content_reports(reporter_user_id);
            """
            )
        )
        await conn.execute(
            text(
                """
                CREATE INDEX ix_content_reports_status
                ON content_reports(status);
            """
            )
        )
        await conn.execute(
            text(
                """
                CREATE INDEX ix_content_reports_container_status
                ON content_reports(container_id, status);
            """
            )
        )

        print("✓ Created content_reports table with indexes")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove content_reports table and is_hidden_by_reports field."""
    print("Removing content reports support...")

    async with engine.begin() as conn:
        # Drop content_reports table
        reports_exist = await table_exists(conn, "content_reports")
        if reports_exist:
            print("Dropping content_reports table...")
            await conn.execute(text("DROP TABLE IF EXISTS content_reports CASCADE;"))
            print("✓ Dropped content_reports table")
        else:
            print("content_reports table does not exist, skipping...")

        # Remove is_hidden_by_reports column from gear_containers
        containers_exist = await table_exists(conn, "gear_containers")
        if containers_exist:
            if await column_exists(conn, "gear_containers", "is_hidden_by_reports"):
                # Drop index first
                await conn.execute(
                    text(
                        """
                        DROP INDEX IF EXISTS ix_gear_containers_is_hidden_by_reports;
                    """
                    )
                )
                # Drop column
                await conn.execute(
                    text(
                        """
                        ALTER TABLE gear_containers
                        DROP COLUMN IF EXISTS is_hidden_by_reports;
                    """
                    )
                )
                print("✓ Removed is_hidden_by_reports column from gear_containers")
            else:
                print("✓ is_hidden_by_reports column does not exist in gear_containers")
        else:
            print("gear_containers table does not exist, skipping...")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add content reports migration")
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
