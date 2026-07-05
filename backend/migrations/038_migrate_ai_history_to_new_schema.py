"""Migration: Migrate ai_history table to new schema.

This migration transforms the ai_history table from the old schema (020) to the new schema (021+):
- Renames: tokens_input → prompt_tokens, tokens_output → completion_tokens, tokens_total → total_tokens
- Consolidates: cost_input, cost_output, cost_total → cost_usd (uses cost_total if available)
- Transforms: final_prompt + context_data → input_data (JSONB)
- Keeps: response_data → output_data (same structure)
- Adds: metadata column (JSONB, nullable)
- Removes: provider, duration_ms, used_own_token (moved to metadata)

Usage:
    python migrations/038_migrate_ai_history_to_new_schema.py upgrade
    python migrations/038_migrate_ai_history_to_new_schema.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


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
    """Migrate ai_history table to new schema."""
    print("Migrating ai_history table to new schema...")

    async with engine.begin() as conn:
        # Check if table exists
        table_exists_result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'ai_history'
                );
            """
            )
        )
        if not table_exists_result.scalar():
            print("ai_history table does not exist, skipping migration...")
            return

        # Check if already migrated (has prompt_tokens column)
        if await column_exists(conn, "ai_history", "prompt_tokens"):
            print("ai_history table already migrated, skipping...")
            return

        # Check if old columns exist
        has_old_schema = await column_exists(conn, "ai_history", "tokens_input")
        if not has_old_schema:
            print("Old schema columns not found, skipping migration...")
            return

        print("Transforming data and columns...")

        # Step 1: Add new columns
        print("  Adding new columns...")
        if not await column_exists(conn, "ai_history", "prompt_tokens"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN prompt_tokens INTEGER")
            )
        if not await column_exists(conn, "ai_history", "completion_tokens"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN completion_tokens INTEGER")
            )
        if not await column_exists(conn, "ai_history", "total_tokens"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN total_tokens INTEGER")
            )
        if not await column_exists(conn, "ai_history", "cost_usd"):
            await conn.execute(text("ALTER TABLE ai_history ADD COLUMN cost_usd REAL"))
        if not await column_exists(conn, "ai_history", "input_data"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN input_data JSONB")
            )
        if not await column_exists(conn, "ai_history", "output_data"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN output_data JSONB")
            )
        if not await column_exists(conn, "ai_history", "metadata"):
            await conn.execute(text("ALTER TABLE ai_history ADD COLUMN metadata JSONB"))

        # Step 2: Copy and transform data
        print("  Copying and transforming data...")
        await conn.execute(
            text(
                """
                UPDATE ai_history
                SET
                    prompt_tokens = COALESCE(tokens_input, 0),
                    completion_tokens = COALESCE(tokens_output, 0),
                    total_tokens = COALESCE(tokens_total, 0),
                    cost_usd = COALESCE(cost_total, cost_input + cost_output, NULL),
                    input_data = jsonb_build_object(
                        'final_prompt', COALESCE(final_prompt, ''),
                        'context_data', COALESCE(context_data, '{}'::jsonb)
                    ),
                    output_data = COALESCE(response_data, '{}'::jsonb),
                    metadata = jsonb_build_object(
                        'provider', COALESCE(provider, ''),
                        'duration_ms', duration_ms,
                        'used_own_token', COALESCE(used_own_token, false)
                    )
                WHERE prompt_tokens IS NULL
            """
            )
        )

        # Step 3: Set NOT NULL constraints on required columns
        print("  Setting NOT NULL constraints...")
        await conn.execute(
            text("UPDATE ai_history SET prompt_tokens = 0 WHERE prompt_tokens IS NULL")
        )
        await conn.execute(
            text(
                "UPDATE ai_history SET completion_tokens = 0 WHERE completion_tokens IS NULL"
            )
        )
        await conn.execute(
            text("UPDATE ai_history SET total_tokens = 0 WHERE total_tokens IS NULL")
        )
        await conn.execute(
            text(
                "UPDATE ai_history SET input_data = '{}'::jsonb WHERE input_data IS NULL"
            )
        )
        await conn.execute(
            text(
                "UPDATE ai_history SET output_data = '{}'::jsonb WHERE output_data IS NULL"
            )
        )

        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN prompt_tokens SET NOT NULL")
        )
        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN prompt_tokens SET DEFAULT 0")
        )
        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN completion_tokens SET NOT NULL")
        )
        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN completion_tokens SET DEFAULT 0")
        )
        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN total_tokens SET NOT NULL")
        )
        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN total_tokens SET DEFAULT 0")
        )
        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN input_data SET NOT NULL")
        )
        await conn.execute(
            text("ALTER TABLE ai_history ALTER COLUMN output_data SET NOT NULL")
        )

        # Step 4: Drop old columns
        print("  Dropping old columns...")
        if await column_exists(conn, "ai_history", "tokens_input"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN tokens_input"))
        if await column_exists(conn, "ai_history", "tokens_output"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN tokens_output"))
        if await column_exists(conn, "ai_history", "tokens_total"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN tokens_total"))
        if await column_exists(conn, "ai_history", "cost_input"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN cost_input"))
        if await column_exists(conn, "ai_history", "cost_output"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN cost_output"))
        if await column_exists(conn, "ai_history", "cost_total"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN cost_total"))
        if await column_exists(conn, "ai_history", "final_prompt"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN final_prompt"))
        if await column_exists(conn, "ai_history", "context_data"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN context_data"))
        if await column_exists(conn, "ai_history", "response_data"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN response_data"))
        if await column_exists(conn, "ai_history", "provider"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN provider"))
        if await column_exists(conn, "ai_history", "duration_ms"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN duration_ms"))
        if await column_exists(conn, "ai_history", "used_own_token"):
            await conn.execute(
                text("ALTER TABLE ai_history DROP COLUMN used_own_token")
            )

        print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Revert ai_history table to old schema."""
    print("Reverting ai_history table to old schema...")
    print(
        "Warning: This will lose data transformation. Old columns will be recreated but data may not match exactly."
    )

    async with engine.begin() as conn:
        # Check if table exists
        table_exists_result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'ai_history'
                );
            """
            )
        )
        if not table_exists_result.scalar():
            print("ai_history table does not exist, skipping downgrade...")
            return

        # Check if already in old schema
        if await column_exists(conn, "ai_history", "tokens_input"):
            print("ai_history table already in old schema, skipping downgrade...")
            return

        # Add old columns back
        print("  Adding old columns...")
        if not await column_exists(conn, "ai_history", "tokens_input"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN tokens_input INTEGER")
            )
        if not await column_exists(conn, "ai_history", "tokens_output"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN tokens_output INTEGER")
            )
        if not await column_exists(conn, "ai_history", "tokens_total"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN tokens_total INTEGER")
            )
        if not await column_exists(conn, "ai_history", "cost_input"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN cost_input NUMERIC(10,6)")
            )
        if not await column_exists(conn, "ai_history", "cost_output"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN cost_output NUMERIC(10,6)")
            )
        if not await column_exists(conn, "ai_history", "cost_total"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN cost_total NUMERIC(10,6)")
            )
        if not await column_exists(conn, "ai_history", "final_prompt"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN final_prompt TEXT")
            )
        if not await column_exists(conn, "ai_history", "context_data"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN context_data JSONB")
            )
        if not await column_exists(conn, "ai_history", "response_data"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN response_data JSONB")
            )
        if not await column_exists(conn, "ai_history", "provider"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN provider VARCHAR(100)")
            )
        if not await column_exists(conn, "ai_history", "duration_ms"):
            await conn.execute(
                text("ALTER TABLE ai_history ADD COLUMN duration_ms INTEGER")
            )
        if not await column_exists(conn, "ai_history", "used_own_token"):
            await conn.execute(
                text(
                    "ALTER TABLE ai_history ADD COLUMN used_own_token BOOLEAN DEFAULT FALSE"
                )
            )

        # Copy data back (simplified - may lose some data)
        print("  Copying data back...")
        await conn.execute(
            text(
                """
                UPDATE ai_history
                SET
                    tokens_input = prompt_tokens,
                    tokens_output = completion_tokens,
                    tokens_total = total_tokens,
                    cost_total = cost_usd,
                    final_prompt = COALESCE(input_data->>'final_prompt', ''),
                    context_data = COALESCE(input_data->'context_data', '{}'::jsonb),
                    response_data = output_data,
                    provider = COALESCE(metadata->>'provider', ''),
                    duration_ms = (metadata->>'duration_ms')::INTEGER,
                    used_own_token = COALESCE((metadata->>'used_own_token')::BOOLEAN, false)
                WHERE tokens_input IS NULL
            """
            )
        )

        # Drop new columns
        print("  Dropping new columns...")
        if await column_exists(conn, "ai_history", "prompt_tokens"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN prompt_tokens"))
        if await column_exists(conn, "ai_history", "completion_tokens"):
            await conn.execute(
                text("ALTER TABLE ai_history DROP COLUMN completion_tokens")
            )
        if await column_exists(conn, "ai_history", "total_tokens"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN total_tokens"))
        if await column_exists(conn, "ai_history", "cost_usd"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN cost_usd"))
        if await column_exists(conn, "ai_history", "input_data"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN input_data"))
        if await column_exists(conn, "ai_history", "output_data"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN output_data"))
        if await column_exists(conn, "ai_history", "metadata"):
            await conn.execute(text("ALTER TABLE ai_history DROP COLUMN metadata"))

        print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate ai_history table to new schema"
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
