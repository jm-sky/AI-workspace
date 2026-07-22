"""Migration: integration connections visibility + GitHub OAuth scopes.

Usage:
    python migrations/058_integration_connections_visibility.py upgrade
    python migrations/058_integration_connections_visibility.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


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
    print("Applying integration connections visibility migration...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "integration_oauth_tokens"):
            print("integration_oauth_tokens table missing — run 056 first")
            return

        if await column_exists(conn, "integration_oauth_tokens", "user_id"):
            print("Renaming user_id -> owner_user_id...")
            await conn.execute(text("""
                    ALTER TABLE integration_oauth_tokens
                    RENAME COLUMN user_id TO owner_user_id;
                """))
        elif not await column_exists(conn, "integration_oauth_tokens", "owner_user_id"):
            print("owner_user_id column missing — unexpected schema")
            return

        if await column_exists(conn, "integration_oauth_tokens", "visibility_scope"):
            print("✓ visibility columns already exist")
        else:
            print("Adding visibility columns...")
            await conn.execute(text("""
                    ALTER TABLE integration_oauth_tokens
                    ADD COLUMN visibility_scope VARCHAR(20) NOT NULL DEFAULT 'user';
                """))
            await conn.execute(text("""
                    ALTER TABLE integration_oauth_tokens
                    ADD COLUMN tenant_id VARCHAR(36) REFERENCES tenants(id) ON DELETE CASCADE;
                """))
            await conn.execute(text("""
                    ALTER TABLE integration_oauth_tokens
                    ADD COLUMN team_id VARCHAR(36) REFERENCES teams(id) ON DELETE CASCADE;
                """))

        print("Updating unique constraints and indexes...")
        await conn.execute(text("""
                ALTER TABLE integration_oauth_tokens
                DROP CONSTRAINT IF EXISTS uq_integration_oauth_tokens_user_provider;
            """))
        for index_name in (
            "uq_integration_oauth_user_provider",
            "uq_integration_oauth_team_provider",
            "uq_integration_oauth_tenant_provider",
        ):
            await conn.execute(text(f"DROP INDEX IF EXISTS {index_name};"))
        await conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_integration_oauth_user_provider
                ON integration_oauth_tokens (owner_user_id, provider)
                WHERE visibility_scope = 'user';
            """))
        await conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_integration_oauth_team_provider
                ON integration_oauth_tokens (team_id, provider)
                WHERE visibility_scope = 'team';
            """))
        await conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_integration_oauth_tenant_provider
                ON integration_oauth_tokens (tenant_id, provider)
                WHERE visibility_scope = 'tenant';
            """))
        await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_integration_oauth_tokens_tenant_id
                ON integration_oauth_tokens(tenant_id);
            """))
        await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_integration_oauth_tokens_team_id
                ON integration_oauth_tokens(team_id);
            """))

    print("Integration connections visibility migration complete.")


async def downgrade() -> None:
    print("Reverting integration connections visibility migration...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "integration_oauth_tokens"):
            return

        await conn.execute(text("DROP INDEX IF EXISTS uq_integration_oauth_tenant_provider;"))
        await conn.execute(text("DROP INDEX IF EXISTS uq_integration_oauth_team_provider;"))
        await conn.execute(text("DROP INDEX IF EXISTS uq_integration_oauth_user_provider;"))

        if await column_exists(conn, "integration_oauth_tokens", "visibility_scope"):
            await conn.execute(text("""
                    ALTER TABLE integration_oauth_tokens
                    DROP COLUMN IF EXISTS visibility_scope,
                    DROP COLUMN IF EXISTS tenant_id,
                    DROP COLUMN IF EXISTS team_id;
                """))

        if await column_exists(conn, "integration_oauth_tokens", "owner_user_id"):
            await conn.execute(text("""
                    ALTER TABLE integration_oauth_tokens
                    RENAME COLUMN owner_user_id TO user_id;
                """))

        await conn.execute(text("""
                ALTER TABLE integration_oauth_tokens
                ADD CONSTRAINT uq_integration_oauth_tokens_user_provider
                UNIQUE (user_id, provider);
            """))

    print("Reverted integration connections visibility migration.")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
