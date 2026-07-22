"""Migration: Phase 0 foundation — tenants, teams, workspace config, integration tokens.

Creates multi-tenancy tables (if missing), teams, cascade config entries,
per-user integration OAuth token vault, and active workspace columns on users.

Usage:
    python migrations/056_phase0_foundation.py upgrade
    python migrations/056_phase0_foundation.py downgrade
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


async def upgrade() -> None:
    print("Applying Phase 0 foundation migration...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "tenants"):
            print("Creating tenants table...")
            await conn.execute(text("""
                    CREATE TABLE tenants (
                        id VARCHAR(36) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description VARCHAR(512),
                        owner_id VARCHAR(36) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT fk_tenants_owner
                            FOREIGN KEY (owner_id) REFERENCES users(id)
                    );
                """))
            print("✓ Created tenants table")
        else:
            print("✓ tenants table already exists")

        if not await table_exists(conn, "tenant_memberships"):
            print("Creating tenant_memberships table...")
            await conn.execute(text("""
                    CREATE TABLE tenant_memberships (
                        tenant_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        role VARCHAR(32) NOT NULL DEFAULT 'member',
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        PRIMARY KEY (tenant_id, user_id),
                        CONSTRAINT fk_tenant_memberships_tenant
                            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_tenant_memberships_user
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            ON DELETE CASCADE
                    );
                """))
            print("✓ Created tenant_memberships table")
        else:
            print("✓ tenant_memberships table already exists")

        if not await table_exists(conn, "teams"):
            print("Creating teams table...")
            await conn.execute(text("""
                    CREATE TABLE teams (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        description VARCHAR(512),
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT fk_teams_tenant
                            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                            ON DELETE CASCADE
                    );
                """))
            await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_teams_tenant_id
                    ON teams(tenant_id);
                """))
            print("✓ Created teams table")
        else:
            print("✓ teams table already exists")

        if not await table_exists(conn, "team_memberships"):
            print("Creating team_memberships table...")
            await conn.execute(text("""
                    CREATE TABLE team_memberships (
                        team_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        role VARCHAR(32) NOT NULL DEFAULT 'member',
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        PRIMARY KEY (team_id, user_id),
                        CONSTRAINT fk_team_memberships_team
                            FOREIGN KEY (team_id) REFERENCES teams(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_team_memberships_user
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            ON DELETE CASCADE
                    );
                """))
            print("✓ Created team_memberships table")
        else:
            print("✓ team_memberships table already exists")

        if not await column_exists(conn, "users", "active_tenant_id"):
            print("Adding active workspace columns to users...")
            await conn.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN active_tenant_id VARCHAR(36),
                    ADD COLUMN active_team_id VARCHAR(36);
                """))
            await conn.execute(text("""
                    ALTER TABLE users
                    ADD CONSTRAINT fk_users_active_tenant
                        FOREIGN KEY (active_tenant_id) REFERENCES tenants(id)
                        ON DELETE SET NULL;
                """))
            await conn.execute(text("""
                    ALTER TABLE users
                    ADD CONSTRAINT fk_users_active_team
                        FOREIGN KEY (active_team_id) REFERENCES teams(id)
                        ON DELETE SET NULL;
                """))
            print("✓ Added active_tenant_id and active_team_id to users")
        else:
            print("✓ users.active_tenant_id already exists")

        if not await table_exists(conn, "workspace_config_entries"):
            print("Creating workspace_config_entries table...")
            await conn.execute(text("""
                    CREATE TABLE workspace_config_entries (
                        id VARCHAR(36) PRIMARY KEY,
                        scope VARCHAR(20) NOT NULL,
                        scope_id VARCHAR(36),
                        tenant_id VARCHAR(36),
                        config_key VARCHAR(100) NOT NULL,
                        config_value JSONB NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT uq_workspace_config_scope_key
                            UNIQUE (scope, scope_id, tenant_id, config_key)
                    );
                """))
            await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_workspace_config_scope
                    ON workspace_config_entries(scope, scope_id);
                """))
            print("✓ Created workspace_config_entries table")
        else:
            print("✓ workspace_config_entries table already exists")

        if not await table_exists(conn, "integration_oauth_tokens"):
            print("Creating integration_oauth_tokens table...")
            await conn.execute(text("""
                    CREATE TABLE integration_oauth_tokens (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        provider VARCHAR(50) NOT NULL,
                        encrypted_access_token TEXT NOT NULL,
                        encrypted_refresh_token TEXT,
                        token_type VARCHAR(50) NOT NULL DEFAULT 'Bearer',
                        expires_at TIMESTAMP WITH TIME ZONE,
                        scopes TEXT,
                        provider_metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL
                            DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT fk_integration_oauth_tokens_user
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            ON DELETE CASCADE,
                        CONSTRAINT uq_integration_oauth_tokens_user_provider
                            UNIQUE (user_id, provider)
                    );
                """))
            await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_integration_oauth_tokens_user_id
                    ON integration_oauth_tokens(user_id);
                """))
            print("✓ Created integration_oauth_tokens table")
        else:
            print("✓ integration_oauth_tokens table already exists")

    print("Phase 0 foundation migration complete.")


async def downgrade() -> None:
    print("Reverting Phase 0 foundation migration...")

    async with engine.begin() as conn:
        if await table_exists(conn, "integration_oauth_tokens"):
            await conn.execute(text("DROP TABLE IF EXISTS integration_oauth_tokens CASCADE;"))
            print("✓ Dropped integration_oauth_tokens")

        if await table_exists(conn, "workspace_config_entries"):
            await conn.execute(text("DROP TABLE IF EXISTS workspace_config_entries CASCADE;"))
            print("✓ Dropped workspace_config_entries")

        if await column_exists(conn, "users", "active_tenant_id"):
            await conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_active_team;"))
            await conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_active_tenant;"))
            await conn.execute(text("""
                    ALTER TABLE users
                    DROP COLUMN IF EXISTS active_team_id,
                    DROP COLUMN IF EXISTS active_tenant_id;
                """))
            print("✓ Removed active workspace columns from users")

        if await table_exists(conn, "team_memberships"):
            await conn.execute(text("DROP TABLE IF EXISTS team_memberships CASCADE;"))
            print("✓ Dropped team_memberships")

        if await table_exists(conn, "teams"):
            await conn.execute(text("DROP TABLE IF EXISTS teams CASCADE;"))
            print("✓ Dropped teams")

        # Keep tenants — may have been created before this migration

    print("Phase 0 foundation downgrade complete.")


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python migrations/056_phase0_foundation.py [upgrade|downgrade]")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        await upgrade()
    elif command == "downgrade":
        await downgrade()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
