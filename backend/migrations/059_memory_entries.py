"""Migration: memory entries with pgvector for semantic retrieval.

Usage:
    python migrations/059_memory_entries.py upgrade
    python migrations/059_memory_entries.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine

EMBEDDING_DIMENSIONS = 1536


async def table_exists(conn, table_name: str) -> bool:
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    print("Applying memory entries migration...")

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("✓ pgvector extension enabled")

        if not await table_exists(conn, "memory_entries"):
            await conn.execute(text(f"""
                    CREATE TABLE memory_entries (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL
                            REFERENCES tenants(id) ON DELETE CASCADE,
                        user_id VARCHAR(36) NOT NULL
                            REFERENCES users(id) ON DELETE CASCADE,
                        scope VARCHAR(20) NOT NULL,
                        agent_key VARCHAR(100),
                        session_id VARCHAR(36),
                        content TEXT NOT NULL,
                        source VARCHAR(50) NOT NULL DEFAULT 'user',
                        entry_metadata JSONB,
                        embedding vector({EMBEDDING_DIMENSIONS}),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT chk_memory_scope CHECK (
                            scope IN ('session', 'user', 'agent')
                        )
                    )
                """))
            await conn.execute(text("""
                    CREATE INDEX idx_memory_entries_tenant_user
                    ON memory_entries(tenant_id, user_id, created_at DESC)
                    """))
            await conn.execute(text("""
                    CREATE INDEX idx_memory_entries_scope
                    ON memory_entries(scope, agent_key, session_id)
                    """))
            await conn.execute(text("""
                    CREATE INDEX idx_memory_entries_embedding
                    ON memory_entries
                    USING hnsw (embedding vector_cosine_ops)
                    """))
            print("✓ Created memory_entries table")
        else:
            print("✓ memory_entries table already exists")

    print("Memory entries migration complete.")


async def downgrade() -> None:
    print("Reverting memory entries migration...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS memory_entries CASCADE;"))
    print("✓ Dropped memory_entries table")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
