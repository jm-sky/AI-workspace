"""Migration: Phase 1 agent runs and trace steps.

Usage:
    python migrations/057_agent_runs.py upgrade
    python migrations/057_agent_runs.py downgrade
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


async def upgrade() -> None:
    print("Applying Phase 1 agent runs migration...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "agent_runs"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE agent_runs (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL
                            REFERENCES tenants(id) ON DELETE CASCADE,
                        user_id VARCHAR(36) NOT NULL
                            REFERENCES users(id) ON DELETE CASCADE,
                        agent_key VARCHAR(100) NOT NULL,
                        status VARCHAR(30) NOT NULL DEFAULT 'running',
                        input_message TEXT NOT NULL,
                        output_message TEXT,
                        system_prompt TEXT NOT NULL,
                        model VARCHAR(255) NOT NULL,
                        prompt_tokens INTEGER NOT NULL DEFAULT 0,
                        completion_tokens INTEGER NOT NULL DEFAULT 0,
                        total_tokens INTEGER NOT NULL DEFAULT 0,
                        cost_usd REAL,
                        blocks JSONB,
                        run_metadata JSONB,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        completed_at TIMESTAMPTZ
                    )
                """
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_agent_runs_tenant_user ON agent_runs(tenant_id, user_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_agent_runs_created_at ON agent_runs(created_at DESC)"
                )
            )
            print("✓ Created agent_runs table")
        else:
            print("✓ agent_runs table already exists")

        if not await table_exists(conn, "agent_run_steps"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE agent_run_steps (
                        id VARCHAR(36) PRIMARY KEY,
                        run_id VARCHAR(36) NOT NULL
                            REFERENCES agent_runs(id) ON DELETE CASCADE,
                        step_index INTEGER NOT NULL,
                        step_type VARCHAR(30) NOT NULL,
                        name VARCHAR(255),
                        input_data JSONB,
                        output_data JSONB,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
                    )
                """
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_agent_run_steps_run_id ON agent_run_steps(run_id, step_index)"
                )
            )
            print("✓ Created agent_run_steps table")
        else:
            print("✓ agent_run_steps table already exists")

    print("Phase 1 agent runs migration complete.")


async def downgrade() -> None:
    print("Reverting Phase 1 agent runs migration...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS agent_run_steps CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS agent_runs CASCADE;"))
    print("✓ Dropped agent tables")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
