"""Migration: two-tier agent trace audit (PII-safe summary + raw tier).

`agent_run_steps.input_data`/`output_data` become the redacted (summary) tier
shown in the normal audit view. Full payloads move to `raw_input_data`/
`raw_output_data` with an expiry (`raw_expires_at`) for retention.

Usage:
    python migrations/061_agent_step_raw_audit.py upgrade
    python migrations/061_agent_step_raw_audit.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


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
    print("Applying two-tier agent audit migration...")

    async with engine.begin() as conn:
        added = []
        for column, ddl in (
            ("raw_input_data", "ADD COLUMN raw_input_data JSONB"),
            ("raw_output_data", "ADD COLUMN raw_output_data JSONB"),
            ("raw_expires_at", "ADD COLUMN raw_expires_at TIMESTAMPTZ"),
        ):
            if not await column_exists(conn, "agent_run_steps", column):
                await conn.execute(text(f"ALTER TABLE agent_run_steps {ddl}"))
                added.append(column)

        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_agent_run_steps_raw_expires_at "
                "ON agent_run_steps(raw_expires_at)"
            )
        )

        if added:
            print(f"✓ Added columns: {', '.join(added)}")
        else:
            print("✓ Raw audit columns already exist")

    print("Two-tier agent audit migration complete.")


async def downgrade() -> None:
    print("Reverting two-tier agent audit migration...")
    async with engine.begin() as conn:
        await conn.execute(
            text("DROP INDEX IF EXISTS idx_agent_run_steps_raw_expires_at;")
        )
        for column in ("raw_input_data", "raw_output_data", "raw_expires_at"):
            await conn.execute(
                text(f"ALTER TABLE agent_run_steps DROP COLUMN IF EXISTS {column};")
            )
    print("✓ Dropped raw audit columns")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
