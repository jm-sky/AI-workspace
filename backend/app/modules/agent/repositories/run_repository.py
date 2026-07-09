"""Repository for agent runs and trace steps."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.modules.agent.db_models import AgentRunDB, AgentRunStepDB, AgentSessionDB


class AgentRunRepository:
    """Persistence for agent runs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_run(
        self,
        *,
        tenant_id: str,
        user_id: str,
        agent_key: str,
        input_message: str,
        system_prompt: str,
        model: str,
        session_id: str | None = None,
    ) -> AgentRunDB:
        run = AgentRunDB(
            id=generate_id(),
            session_id=session_id,
            tenant_id=tenant_id,
            user_id=user_id,
            agent_key=agent_key,
            status="running",
            input_message=input_message,
            system_prompt=system_prompt,
            model=model,
        )
        self.db.add(run)
        await self.db.flush()
        return run

    async def add_step(
        self,
        *,
        run_id: str,
        step_index: int,
        step_type: str,
        name: str | None = None,
        input_data: dict[str, Any] | None = None,
        output_data: dict[str, Any] | None = None,
        raw_input_data: dict[str, Any] | None = None,
        raw_output_data: dict[str, Any] | None = None,
        raw_expires_at: datetime | None = None,
    ) -> AgentRunStepDB:
        step = AgentRunStepDB(
            id=generate_id(),
            run_id=run_id,
            step_index=step_index,
            step_type=step_type,
            name=name,
            input_data=input_data,
            output_data=output_data,
            raw_input_data=raw_input_data,
            raw_output_data=raw_output_data,
            raw_expires_at=raw_expires_at,
        )
        self.db.add(step)
        await self.db.flush()
        return step

    async def complete_run(
        self,
        run: AgentRunDB,
        *,
        status: str,
        output_message: str | None,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost_usd: float | None,
        blocks: list[dict[str, Any]] | None = None,
        run_metadata: dict[str, Any] | None = None,
    ) -> AgentRunDB:
        run.status = status
        run.output_message = output_message
        run.prompt_tokens = prompt_tokens
        run.completion_tokens = completion_tokens
        run.total_tokens = total_tokens
        run.cost_usd = cost_usd
        run.blocks = blocks
        run.run_metadata = run_metadata
        run.completed_at = datetime.now(UTC)
        await self.db.flush()
        return run

    async def get_run(self, run_id: str, *, user_id: str) -> AgentRunDB | None:
        stmt = select(AgentRunDB).where(
            AgentRunDB.id == run_id,
            AgentRunDB.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_runs(
        self,
        *,
        user_id: str,
        tenant_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[AgentRunDB], int]:
        count_stmt = (
            select(func.count())
            .select_from(AgentRunDB)
            .where(
                AgentRunDB.user_id == user_id,
                AgentRunDB.tenant_id == tenant_id,
            )
        )
        total = int((await self.db.execute(count_stmt)).scalar_one())

        stmt = (
            select(AgentRunDB)
            .where(
                AgentRunDB.user_id == user_id,
                AgentRunDB.tenant_id == tenant_id,
            )
            .order_by(AgentRunDB.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_steps(self, run_id: str) -> list[AgentRunStepDB]:
        stmt = (
            select(AgentRunStepDB)
            .where(AgentRunStepDB.run_id == run_id)
            .order_by(AgentRunStepDB.step_index.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_run_any(self, run_id: str) -> AgentRunDB | None:
        """Fetch a run without user scoping (admin/raw-audit use only)."""
        stmt = select(AgentRunDB).where(AgentRunDB.id == run_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def purge_expired_raw(self, *, now: datetime | None = None) -> int:
        """Null out raw payloads whose retention window has passed."""
        cutoff = now or datetime.now(UTC)
        stmt = (
            update(AgentRunStepDB)
            .where(
                AgentRunStepDB.raw_expires_at.is_not(None),
                AgentRunStepDB.raw_expires_at < cutoff,
                (
                    AgentRunStepDB.raw_input_data.is_not(None)
                    | AgentRunStepDB.raw_output_data.is_not(None)
                ),
            )
            .values(raw_input_data=None, raw_output_data=None, raw_expires_at=None)
        )
        result = await self.db.execute(stmt)
        return result.rowcount or 0

    async def list_runs_for_session(self, session_id: str) -> list[AgentRunDB]:
        """All runs in a session, oldest first (conversation order)."""
        stmt = (
            select(AgentRunDB)
            .where(AgentRunDB.session_id == session_id)
            .order_by(AgentRunDB.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class AgentSessionRepository:
    """Persistence for multi-turn chat sessions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        *,
        tenant_id: str,
        user_id: str,
        agent_key: str,
        title: str | None = None,
    ) -> AgentSessionDB:
        session = AgentSessionDB(
            id=generate_id(),
            tenant_id=tenant_id,
            user_id=user_id,
            agent_key=agent_key,
            title=title,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_session(
        self, session_id: str, *, user_id: str
    ) -> AgentSessionDB | None:
        stmt = select(AgentSessionDB).where(
            AgentSessionDB.id == session_id,
            AgentSessionDB.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def touch_session(
        self, session: AgentSessionDB, *, title: str | None = None
    ) -> AgentSessionDB:
        session.last_message_at = datetime.now(UTC)
        if title and not session.title:
            session.title = title
        await self.db.flush()
        return session

    async def list_sessions(
        self,
        *,
        user_id: str,
        tenant_id: str,
        limit: int = 30,
        offset: int = 0,
    ) -> tuple[list[AgentSessionDB], int]:
        count_stmt = (
            select(func.count())
            .select_from(AgentSessionDB)
            .where(
                AgentSessionDB.user_id == user_id,
                AgentSessionDB.tenant_id == tenant_id,
            )
        )
        total = int((await self.db.execute(count_stmt)).scalar_one())

        stmt = (
            select(AgentSessionDB)
            .where(
                AgentSessionDB.user_id == user_id,
                AgentSessionDB.tenant_id == tenant_id,
            )
            .order_by(AgentSessionDB.last_message_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
