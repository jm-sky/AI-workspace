"""Migration: Add AI tables for OpenRouter integration.

This migration creates three tables for AI functionality:
1. ai_user_settings - User AI configuration and API tokens
2. ai_history - Full interaction history with tokens and costs
3. ai_cache - Cache for AI responses with TTL

Usage:
    python migrations/021_add_ai_tables.py upgrade
    python migrations/021_add_ai_tables.py downgrade
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
    """Create AI tables."""
    print("Creating AI tables...")

    async with engine.begin() as conn:
        # Check if tables already exist
        settings_exist = await table_exists(conn, "ai_user_settings")
        history_exist = await table_exists(conn, "ai_history")
        cache_exist = await table_exists(conn, "ai_cache")

        if settings_exist and history_exist and cache_exist:
            print("AI tables already exist, skipping migration...")
            return

        # Create ai_user_settings table
        if not settings_exist:
            print("Creating ai_user_settings table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE ai_user_settings (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                        use_own_token BOOLEAN NOT NULL DEFAULT FALSE,
                        encrypted_api_token TEXT,
                        selected_model VARCHAR(255) NOT NULL DEFAULT 'openai/gpt-4o-mini',
                        context_fields JSONB NOT NULL DEFAULT '{}',
                        max_tokens INTEGER,
                        temperature REAL NOT NULL DEFAULT 1.0,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """
                )
            )
            print("✓ Created ai_user_settings table")

            # Create index on user_id
            await conn.execute(
                text(
                    "CREATE INDEX idx_ai_user_settings_user_id ON ai_user_settings(user_id);"
                )
            )
            print("✓ Created index on ai_user_settings.user_id")

        # Create ai_history table
        if not history_exist:
            print("Creating ai_history table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE ai_history (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        operation_type VARCHAR(50) NOT NULL,
                        model VARCHAR(255) NOT NULL,
                        prompt_tokens INTEGER NOT NULL DEFAULT 0,
                        completion_tokens INTEGER NOT NULL DEFAULT 0,
                        total_tokens INTEGER NOT NULL DEFAULT 0,
                        cost_usd REAL,
                        input_data JSONB NOT NULL,
                        output_data JSONB NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    );
                """
                )
            )
            print("✓ Created ai_history table")

            # Create indexes
            await conn.execute(
                text("CREATE INDEX idx_ai_history_user_id ON ai_history(user_id);")
            )
            print("✓ Created index on ai_history.user_id")

            await conn.execute(
                text(
                    "CREATE INDEX idx_ai_history_created_at ON ai_history(created_at);"
                )
            )
            print("✓ Created index on ai_history.created_at")

            await conn.execute(
                text(
                    "CREATE INDEX idx_ai_history_operation_type ON ai_history(operation_type);"
                )
            )
            print("✓ Created index on ai_history.operation_type")

        # Create ai_cache table
        if not cache_exist:
            print("Creating ai_cache table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE ai_cache (
                        cache_key VARCHAR(64) PRIMARY KEY,
                        operation_type VARCHAR(50) NOT NULL,
                        model VARCHAR(255) NOT NULL,
                        cached_data JSONB NOT NULL,
                        hit_count INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL
                    );
                """
                )
            )
            print("✓ Created ai_cache table")

            # Create indexes
            await conn.execute(
                text("CREATE INDEX idx_ai_cache_expires_at ON ai_cache(expires_at);")
            )
            print("✓ Created index on ai_cache.expires_at")

            await conn.execute(
                text(
                    "CREATE INDEX idx_ai_cache_operation_type ON ai_cache(operation_type);"
                )
            )
            print("✓ Created index on ai_cache.operation_type")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Drop AI tables."""
    print("Dropping AI tables...")

    async with engine.begin() as conn:
        # Drop tables in reverse order (respecting foreign keys)
        await conn.execute(text("DROP TABLE IF EXISTS ai_cache CASCADE;"))
        print("✓ Dropped ai_cache table")

        await conn.execute(text("DROP TABLE IF EXISTS ai_history CASCADE;"))
        print("✓ Dropped ai_history table")

        await conn.execute(text("DROP TABLE IF EXISTS ai_user_settings CASCADE;"))
        print("✓ Dropped ai_user_settings table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add AI tables migration")
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
