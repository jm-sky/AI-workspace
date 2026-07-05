"""Migration: Migrate ai_cache table to new schema.

This migration transforms the ai_cache table from the old schema (020) to the new schema (021+):
- Removes: id column (UUID primary key)
- Renames: response_data → cached_data
- Changes: cache_key from VARCHAR(255) UNIQUE to VARCHAR(64) PRIMARY KEY
- Removes: input_hash, last_accessed_at columns (if they exist)
- Ensures correct indexes

Usage:
    python migrations/040_migrate_ai_cache_to_new_schema.py upgrade
    python migrations/040_migrate_ai_cache_to_new_schema.py downgrade
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


async def get_primary_key_constraint_name(conn, table_name: str) -> str | None:
    """Get the primary key constraint name for a table."""
    result = await conn.execute(
        text(
            """
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
            AND table_name = :table_name
            AND constraint_type = 'PRIMARY KEY'
            LIMIT 1;
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar()


async def upgrade() -> None:
    """Migrate ai_cache table to new schema."""
    print("Migrating ai_cache table to new schema...")

    async with engine.begin() as conn:
        # Check if table exists
        if not await table_exists(conn, "ai_cache"):
            print("ai_cache table does not exist, skipping migration...")
            return

        # Check if already migrated (has cached_data column)
        if await column_exists(conn, "ai_cache", "cached_data"):
            print("ai_cache table already migrated, skipping...")
            return

        # Check if old schema exists (has response_data column)
        has_old_schema = await column_exists(conn, "ai_cache", "response_data")
        if not has_old_schema:
            print("Old schema columns not found, skipping migration...")
            return

        print("Transforming ai_cache table...")

        # Step 1: Check if id column exists (indicates old schema)
        has_id_column = await column_exists(conn, "ai_cache", "id")

        # Step 2: Add cached_data column if it doesn't exist
        if not await column_exists(conn, "ai_cache", "cached_data"):
            print("  Adding cached_data column...")
            await conn.execute(
                text("ALTER TABLE ai_cache ADD COLUMN cached_data JSONB")
            )

        # Step 3: Copy data from response_data to cached_data
        print("  Copying data from response_data to cached_data...")
        await conn.execute(
            text(
                """
                UPDATE ai_cache
                SET cached_data = response_data
                WHERE cached_data IS NULL
            """
            )
        )

        # Step 4: Set NOT NULL constraint on cached_data
        print("  Setting NOT NULL constraint on cached_data...")
        await conn.execute(
            text(
                "UPDATE ai_cache SET cached_data = '{}'::jsonb WHERE cached_data IS NULL"
            )
        )
        await conn.execute(
            text("ALTER TABLE ai_cache ALTER COLUMN cached_data SET NOT NULL")
        )

        # Step 5: Handle primary key change if needed
        if has_id_column:
            print("  Changing primary key from id to cache_key...")

            # Get primary key constraint name
            pk_constraint = await get_primary_key_constraint_name(conn, "ai_cache")
            if pk_constraint:
                # Drop existing primary key constraint (constraint name is safe as it comes from information_schema)
                await conn.execute(
                    text(
                        f'ALTER TABLE ai_cache DROP CONSTRAINT IF EXISTS "{pk_constraint}"'
                    )
                )

            # Drop unique constraint on cache_key if it exists (will be replaced by primary key)
            unique_constraint_result = await conn.execute(
                text(
                    """
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE table_schema = 'public'
                    AND table_name = 'ai_cache'
                    AND constraint_type = 'UNIQUE'
                    AND constraint_name LIKE '%cache_key%'
                    LIMIT 1;
                """
                )
            )
            unique_constraint = unique_constraint_result.scalar()
            if unique_constraint:
                await conn.execute(
                    text(
                        f'ALTER TABLE ai_cache DROP CONSTRAINT IF EXISTS "{unique_constraint}"'
                    )
                )

            # First, ensure cache_key is unique and not null
            await conn.execute(
                text("ALTER TABLE ai_cache ALTER COLUMN cache_key SET NOT NULL")
            )

            # Change cache_key to VARCHAR(64) if it's not already
            await conn.execute(
                text("ALTER TABLE ai_cache ALTER COLUMN cache_key TYPE VARCHAR(64)")
            )

            # Create new primary key on cache_key
            await conn.execute(text("ALTER TABLE ai_cache ADD PRIMARY KEY (cache_key)"))

            # Drop id column
            print("  Dropping id column...")
            await conn.execute(text("ALTER TABLE ai_cache DROP COLUMN id"))
        else:
            # Step 6: Ensure cache_key is VARCHAR(64) if it's VARCHAR(255)
            print("  Ensuring cache_key is VARCHAR(64)...")
            await conn.execute(
                text("ALTER TABLE ai_cache ALTER COLUMN cache_key TYPE VARCHAR(64)")
            )

        # Step 7: Drop old columns
        print("  Dropping old columns...")
        if await column_exists(conn, "ai_cache", "response_data"):
            await conn.execute(text("ALTER TABLE ai_cache DROP COLUMN response_data"))
        if await column_exists(conn, "ai_cache", "input_hash"):
            await conn.execute(text("ALTER TABLE ai_cache DROP COLUMN input_hash"))
        if await column_exists(conn, "ai_cache", "last_accessed_at"):
            await conn.execute(
                text("ALTER TABLE ai_cache DROP COLUMN last_accessed_at")
            )

        # Step 8: Ensure correct indexes exist
        print("  Ensuring indexes...")
        # Check if index on expires_at exists
        index_result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM pg_indexes
                    WHERE tablename = 'ai_cache'
                    AND indexname = 'idx_ai_cache_expires_at'
                );
            """
            )
        )
        if not index_result.scalar():
            await conn.execute(
                text("CREATE INDEX idx_ai_cache_expires_at ON ai_cache(expires_at)")
            )

        # Check if index on operation_type exists
        index_result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM pg_indexes
                    WHERE tablename = 'ai_cache'
                    AND indexname = 'idx_ai_cache_operation_type'
                );
            """
            )
        )
        if not index_result.scalar():
            await conn.execute(
                text(
                    "CREATE INDEX idx_ai_cache_operation_type ON ai_cache(operation_type)"
                )
            )

        print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Revert ai_cache table to old schema."""
    print("Reverting ai_cache table to old schema...")
    print(
        "Warning: This will lose data transformation. Old columns will be recreated but data may not match exactly."
    )

    async with engine.begin() as conn:
        # Check if table exists
        if not await table_exists(conn, "ai_cache"):
            print("ai_cache table does not exist, skipping downgrade...")
            return

        # Check if already in old schema
        if await column_exists(conn, "ai_cache", "response_data"):
            print("ai_cache table already in old schema, skipping downgrade...")
            return

        # Add old columns back
        print("  Adding old columns...")
        if not await column_exists(conn, "ai_cache", "id"):
            await conn.execute(
                text(
                    "ALTER TABLE ai_cache ADD COLUMN id UUID DEFAULT gen_random_uuid()"
                )
            )
        if not await column_exists(conn, "ai_cache", "response_data"):
            await conn.execute(
                text("ALTER TABLE ai_cache ADD COLUMN response_data JSONB")
            )
        if not await column_exists(conn, "ai_cache", "input_hash"):
            await conn.execute(
                text("ALTER TABLE ai_cache ADD COLUMN input_hash VARCHAR(255)")
            )
        if not await column_exists(conn, "ai_cache", "last_accessed_at"):
            await conn.execute(
                text(
                    "ALTER TABLE ai_cache ADD COLUMN last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()"
                )
            )

        # Copy data back
        print("  Copying data back...")
        await conn.execute(
            text(
                """
                UPDATE ai_cache
                SET response_data = cached_data,
                    last_accessed_at = NOW()
                WHERE response_data IS NULL
            """
            )
        )

        # Change primary key back to id
        print("  Changing primary key back to id...")
        await conn.execute(
            text("ALTER TABLE ai_cache DROP CONSTRAINT IF EXISTS ai_cache_pkey")
        )
        await conn.execute(
            text("ALTER TABLE ai_cache ALTER COLUMN cache_key TYPE VARCHAR(255)")
        )
        await conn.execute(
            text("ALTER TABLE ai_cache ALTER COLUMN cache_key DROP NOT NULL")
        )
        await conn.execute(text("ALTER TABLE ai_cache ADD PRIMARY KEY (id)"))
        await conn.execute(
            text(
                "ALTER TABLE ai_cache ADD CONSTRAINT ai_cache_cache_key_unique UNIQUE (cache_key)"
            )
        )

        # Set NOT NULL constraints
        await conn.execute(
            text(
                "UPDATE ai_cache SET response_data = '{}'::jsonb WHERE response_data IS NULL"
            )
        )
        await conn.execute(
            text("ALTER TABLE ai_cache ALTER COLUMN response_data SET NOT NULL")
        )

        # Drop new column
        print("  Dropping new column...")
        if await column_exists(conn, "ai_cache", "cached_data"):
            await conn.execute(text("ALTER TABLE ai_cache DROP COLUMN cached_data"))

        print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate ai_cache table to new schema")
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
