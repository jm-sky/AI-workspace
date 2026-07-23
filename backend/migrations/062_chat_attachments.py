"""Migration: chat attachments for workspace agent.

Usage:
    python migrations/062_chat_attachments.py upgrade
    python migrations/062_chat_attachments.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


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
    print("Applying chat attachments migration...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "chat_attachments"):
            await conn.execute(text("""
                    CREATE TABLE chat_attachments (
                        id VARCHAR(36) PRIMARY KEY,
                        owner_user_id VARCHAR(36) NOT NULL
                            REFERENCES users(id) ON DELETE CASCADE,
                        tenant_id VARCHAR(36) NOT NULL
                            REFERENCES tenants(id) ON DELETE CASCADE,
                        session_id VARCHAR(36)
                            REFERENCES chat_sessions(id) ON DELETE CASCADE,
                        run_id VARCHAR(36)
                            REFERENCES agent_runs(id) ON DELETE SET NULL,
                        kind VARCHAR(20) NOT NULL,
                        original_filename TEXT NOT NULL,
                        mime_type VARCHAR(100) NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        storage_path TEXT NOT NULL,
                        thumbnail_path TEXT,
                        width INTEGER,
                        height INTEGER,
                        extracted_text TEXT,
                        extracted_chars INTEGER,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT chk_chat_attachment_kind CHECK (
                            kind IN ('image', 'text', 'pdf')
                        )
                    )
                """))
            await conn.execute(text("""
                    CREATE INDEX idx_chat_attachments_owner_created
                    ON chat_attachments(owner_user_id, created_at DESC)
                    """))
            await conn.execute(text("""
                    CREATE INDEX idx_chat_attachments_run
                    ON chat_attachments(run_id)
                    """))
            await conn.execute(text("""
                    CREATE INDEX idx_chat_attachments_tenant_session
                    ON chat_attachments(tenant_id, session_id)
                    """))
            print("✓ Created chat_attachments table")
        else:
            print("✓ chat_attachments table already exists")

    print("Chat attachments migration complete.")


async def downgrade() -> None:
    print("Reverting chat attachments migration...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS chat_attachments CASCADE;"))
    print("✓ Dropped chat_attachments")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
