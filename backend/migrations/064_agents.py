"""Migration: tenant-scoped agent definitions.

Usage:
    python migrations/064_agents.py upgrade
    python migrations/064_agents.py downgrade
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine
from app.common.id_utils import generate_id
from app.modules.agent.registry import BUILTIN_AGENTS


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
    print("Applying agents table migration...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "agents"):
            await conn.execute(text("""
                CREATE TABLE agents (
                    id VARCHAR(36) PRIMARY KEY,
                    tenant_id VARCHAR(36) NOT NULL
                        REFERENCES tenants(id) ON DELETE CASCADE,
                    key VARCHAR(100) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    system_prompt TEXT NOT NULL,
                    model VARCHAR(200),
                    effort VARCHAR(50),
                    tool_profile JSONB NOT NULL DEFAULT '[]'::jsonb,
                    memory_scopes JSONB NOT NULL DEFAULT '["session","user","agent"]'::jsonb,
                    rag_enabled BOOLEAN NOT NULL DEFAULT false,
                    routing_hints JSONB NOT NULL DEFAULT '{}'::jsonb,
                    visibility VARCHAR(20) NOT NULL DEFAULT 'tenant',
                    team_id VARCHAR(36),
                    is_enabled BOOLEAN NOT NULL DEFAULT true,
                    is_default BOOLEAN NOT NULL DEFAULT false,
                    limits JSONB,
                    guardrails JSONB,
                    created_by VARCHAR(36),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                    CONSTRAINT uq_agents_tenant_key UNIQUE (tenant_id, key),
                    CONSTRAINT chk_agents_visibility CHECK (visibility IN ('tenant', 'team'))
                )
            """))
            await conn.execute(text("""
                CREATE INDEX idx_agents_tenant_enabled
                ON agents(tenant_id, is_enabled)
            """))
            await conn.execute(text("""
                CREATE UNIQUE INDEX uq_agents_tenant_default
                ON agents(tenant_id)
                WHERE is_default = true
            """))
            print("✓ Created agents table")
        else:
            print("✓ agents table already exists")

        tenants = (await conn.execute(text("SELECT id FROM tenants"))).fetchall()
        seeded = 0
        for (tenant_id,) in tenants:
            for agent in BUILTIN_AGENTS.values():
                exists = await conn.execute(
                    text("""
                        SELECT 1 FROM agents
                        WHERE tenant_id = :tenant_id AND key = :key
                    """),
                    {"tenant_id": tenant_id, "key": agent.key},
                )
                if exists.scalar() is not None:
                    continue
                await conn.execute(
                    text("""
                        INSERT INTO agents (
                            id, tenant_id, key, name, description, system_prompt,
                            model, effort, tool_profile, memory_scopes, rag_enabled,
                            routing_hints, visibility, is_enabled, is_default,
                            created_at, updated_at
                        ) VALUES (
                            :id, :tenant_id, :key, :name, :description, :system_prompt,
                            :model, :effort, CAST(:tool_profile AS jsonb),
                            CAST(:memory_scopes AS jsonb), :rag_enabled,
                            CAST(:routing_hints AS jsonb), 'tenant', :is_enabled, :is_default,
                            (NOW() AT TIME ZONE 'UTC'), (NOW() AT TIME ZONE 'UTC')
                        )
                    """),
                    {
                        "id": generate_id(),
                        "tenant_id": tenant_id,
                        "key": agent.key,
                        "name": agent.name,
                        "description": agent.description,
                        "system_prompt": agent.system_prompt,
                        "model": agent.model,
                        "effort": agent.effort,
                        "tool_profile": json.dumps(list(agent.tool_profile)),
                        "memory_scopes": json.dumps(list(agent.memory_scopes)),
                        "rag_enabled": agent.rag_enabled,
                        "routing_hints": json.dumps(agent.routing_hints or {}),
                        "is_enabled": agent.is_enabled,
                        "is_default": agent.is_default,
                    },
                )
                seeded += 1
        print(f"✓ Seeded {seeded} agent rows for {len(tenants)} tenants")

    print("✓ Agents migration complete")


async def downgrade() -> None:
    print("Reverting agents table migration...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS agents CASCADE"))
        print("✓ Dropped agents table")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("upgrade", "downgrade"):
        print("Usage: python migrations/064_agents.py [upgrade|downgrade]")
        sys.exit(1)
    asyncio.run(upgrade() if sys.argv[1] == "upgrade" else downgrade())
