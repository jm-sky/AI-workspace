"""Migration: Add container share tokens table.

This migration adds the following:
- container_share_tokens table for sharing containers via tokens

Usage:
    python migrations/032_add_container_share_tokens.py upgrade
    python migrations/032_add_container_share_tokens.py downgrade
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
    """Add container share tokens table."""
    print("Adding container_share_tokens table...")

    async with engine.begin() as conn:
        tokens_exist = await table_exists(conn, "container_share_tokens")
        if not tokens_exist:
            print("Creating container_share_tokens table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE container_share_tokens (
                        token VARCHAR(255) PRIMARY KEY,
                        container_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT fk_container_share_tokens_container 
                            FOREIGN KEY (container_id) 
                            REFERENCES gear_containers(id) 
                            ON DELETE CASCADE,
                        CONSTRAINT fk_container_share_tokens_user 
                            FOREIGN KEY (user_id) 
                            REFERENCES users(id)
                    );
                """
                )
            )
            # Create indexes for better query performance
            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_token 
                    ON container_share_tokens(token);
                """
                )
            )
            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_container_id 
                    ON container_share_tokens(container_id);
                """
                )
            )
            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_user_id 
                    ON container_share_tokens(user_id);
                """
                )
            )
            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_expires_at 
                    ON container_share_tokens(expires_at);
                """
                )
            )
            print("✓ Created container_share_tokens table")
        else:
            print("✓ container_share_tokens table already exists")


async def downgrade() -> None:
    """Remove container share tokens table."""
    print("Removing container_share_tokens table...")

    async with engine.begin() as conn:
        tokens_exist = await table_exists(conn, "container_share_tokens")
        if tokens_exist:
            print("Dropping container_share_tokens table...")
            await conn.execute(
                text(
                    """
                    DROP TABLE IF EXISTS container_share_tokens CASCADE;
                """
                )
            )
            print("✓ Dropped container_share_tokens table")
        else:
            print("✓ container_share_tokens table does not exist")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print(
            "Usage: python migrations/032_add_container_share_tokens.py [upgrade|downgrade]"
        )
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        await upgrade()
    elif command == "downgrade":
        await downgrade()
    else:
        print(f"Unknown command: {command}")
        print(
            "Usage: python migrations/032_add_container_share_tokens.py [upgrade|downgrade]"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
