"""Migration: Phase 1 multi-turn chat sessions.

Adds a `chat_sessions` table that groups several agent runs into one
conversation, and links `agent_runs` to a session via `session_id`.

Usage:
    python migrations/060_chat_sessions.py upgrade
    python migrations/060_chat_sessions.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
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
    print("Applying chat sessions migration...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "chat_sessions"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE chat_sessions (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL
                            REFERENCES tenants(id) ON DELETE CASCADE,
                        user_id VARCHAR(36) NOT NULL
                            REFERENCES users(id) ON DELETE CASCADE,
                        agent_key VARCHAR(100) NOT NULL,
                        title VARCHAR(255),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        last_message_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
                    )
                """
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_chat_sessions_tenant_user "
                    "ON chat_sessions(tenant_id, user_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_chat_sessions_last_message_at "
                    "ON chat_sessions(last_message_at DESC)"
                )
            )
            print("✓ Created chat_sessions table")
        else:
            print("✓ chat_sessions table already exists")

        if not await column_exists(conn, "agent_runs", "session_id"):
            await conn.execute(
                text(
                    "ALTER TABLE agent_runs ADD COLUMN session_id VARCHAR(36) "
                    "REFERENCES chat_sessions(id) ON DELETE CASCADE"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_agent_runs_session_id "
                    "ON agent_runs(session_id, created_at)"
                )
            )
            print("✓ Added agent_runs.session_id column")
        else:
            print("✓ agent_runs.session_id column already exists")

    print("Chat sessions migration complete.")


async def downgrade() -> None:
    print("Reverting chat sessions migration...")
    async with engine.begin() as conn:
        await conn.execute(
            text("ALTER TABLE agent_runs DROP COLUMN IF EXISTS session_id;")
        )
        await conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE;"))
    print("✓ Dropped chat sessions")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
