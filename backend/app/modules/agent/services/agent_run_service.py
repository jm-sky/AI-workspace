"""High-level agent run orchestration with persistence."""

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.agent.audit import redact_payload
from app.modules.agent.db_models import AgentRunDB, AgentRunStepDB, AgentSessionDB
from app.modules.agent.exceptions import (
    AgentNotConfiguredError,
    AgentToolsDisabledError,
)
from app.modules.agent.guards import (
    SourceRoutingWarning,
    check_source_mismatch,
    provider_of_tool,
)
from app.modules.agent.guards.source_routing import format_warnings
from app.modules.agent.prompts.github_workspace import GITHUB_WORKSPACE_SYSTEM_PROMPT
from app.modules.agent.prompts.jira_360 import JIRA_360_SYSTEM_PROMPT
from app.modules.agent.repositories import AgentRunRepository, AgentSessionRepository
from app.modules.agent.schemas import (
    AgentRunResponse,
    AgentRunStepResponse,
    AgentSessionDetail,
    AgentSessionSummary,
)
from app.modules.agent.services.agent_loop import AgentLoopEvent, AgentLoopService
from app.modules.agent.tools import build_tool_registry
from app.modules.agent.tools.base import AgentToolRegistry
from app.modules.ai.utils.models_config import get_model_by_id, has_live_catalog
from app.modules.integrations.service import IntegrationTokenService
from app.modules.memory.services.memory_service import MemoryService
from app.modules.tenants.service import TenantContext
from app.modules.workspace_config.repositories import WorkspaceConfigRepository
from app.modules.workspace_config.resolver import WorkspaceConfigResolver

AGENT_PROMPTS: dict[str, str] = {
    "github-workspace": GITHUB_WORKSPACE_SYSTEM_PROMPT,
    "jira-360": JIRA_360_SYSTEM_PROMPT,
}


class AgentRunService:
    """Coordinates config resolution, tool registry, loop, and trace persistence."""

    def __init__(
        self,
        db: AsyncSession,
        token_service: IntegrationTokenService,
    ):
        self.db = db
        self.token_service = token_service
        self.run_repo = AgentRunRepository(db)
        self.session_repo = AgentSessionRepository(db)
        self.config_resolver = WorkspaceConfigResolver(WorkspaceConfigRepository(db))

    async def _resolve_model(
        self,
        *,
        user_id: str,
        tenant_ctx: TenantContext,
        requested_model: str | None,
    ) -> str:
        effective = await self.config_resolver.resolve(
            user_id=user_id,
            tenant_id=tenant_ctx.tenant_id,
            team_id=tenant_ctx.team_id,
        )
        if not effective.toolsEnabled:
            raise AgentToolsDisabledError("Agent tools are disabled for this workspace")

        model = requested_model or effective.defaultModel

        # An empty allow-list means the workspace sets no ceiling: any model the
        # catalog knows about is fair game. Without a live catalog we cannot tell
        # a typo from a legitimate model, so we pass it through to OpenRouter
        # rather than fail every non-curated model.
        if not effective.allowedModels:
            if not model:
                raise AgentNotConfiguredError("No model configured for workspace")
            if has_live_catalog() and not get_model_by_id(model):
                raise AgentNotConfiguredError(f"Unknown model for workspace: {model}")
            return model

        if model and model in effective.allowedModels:
            return model
        return effective.allowedModels[0]

    def _system_prompt(self, agent_key: str) -> str:
        prompt = AGENT_PROMPTS.get(agent_key)
        if prompt is None:
            raise AgentNotConfiguredError(f"Unknown agent: {agent_key}")
        return prompt

    async def run_stream(
        self,
        *,
        tenant_ctx: TenantContext,
        message: str,
        agent_key: str = "github-workspace",
        model: str | None = None,
        session_id: str | None = None,
    ) -> AsyncIterator[AgentLoopEvent]:
        resolved_model = await self._resolve_model(
            user_id=tenant_ctx.user_id,
            tenant_ctx=tenant_ctx,
            requested_model=model,
        )
        base_prompt = self._system_prompt(agent_key)

        # Resolve the conversation this turn belongs to (create on first turn).
        session = None
        if session_id:
            session = await self.session_repo.get_session(session_id, user_id=tenant_ctx.user_id)
        if session is None:
            session = await self.session_repo.create_session(
                tenant_id=tenant_ctx.tenant_id,
                user_id=tenant_ctx.user_id,
                agent_key=agent_key,
                title=_derive_title(message),
            )
        session_id = session.id

        # Prior turns become plain user/assistant history for the loop.
        history = await self._load_history(session_id)

        run = await self.run_repo.create_run(
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
            agent_key=agent_key,
            input_message=message,
            system_prompt=base_prompt,
            model=resolved_model,
            session_id=session_id,
        )
        await self.db.commit()

        tool_registry = build_tool_registry(
            tenant_ctx=tenant_ctx,
            token_service=self.token_service,
            db=self.db,
            agent_key=agent_key,
            session_id=session_id,
        )

        system_prompt = await self._build_system_prompt(
            base_prompt=base_prompt,
            tenant_ctx=tenant_ctx,
            tool_registry=tool_registry,
            message=message,
            agent_key=agent_key,
            session_id=session_id,
        )
        if system_prompt != run.system_prompt:
            run.system_prompt = system_prompt
            await self.db.commit()

        loop = AgentLoopService(
            model=resolved_model,
            system_prompt=system_prompt,
            tool_registry=tool_registry,
            agent_key=agent_key,
        )

        step_index = 0

        try:
            async for event in loop.run_stream(message, history=history):
                if event.event == "step":
                    yield AgentLoopEvent(
                        event=event.event,
                        data={**event.data, "runId": run.id, "sessionId": session_id},
                    )
                elif event.event == "run_complete":
                    self._apply_source_guard(
                        event=event,
                        user_message=message,
                        tool_registry=tool_registry,
                    )
                    raw_enabled = settings.ai.audit_raw_enabled
                    raw_expiry = _raw_expiry()
                    for trace_step in event.data.get("stepsTrace", []):
                        raw_input = trace_step.get("inputData")
                        raw_output = trace_step.get("outputData")
                        await self.run_repo.add_step(
                            run_id=run.id,
                            step_index=trace_step.get("stepIndex", step_index),
                            step_type=trace_step.get("stepType", "step"),
                            name=trace_step.get("name"),
                            input_data=(redact_payload(raw_input) if raw_input is not None else None),
                            output_data=(redact_payload(raw_output) if raw_output is not None else None),
                            raw_input_data=raw_input if raw_enabled else None,
                            raw_output_data=raw_output if raw_enabled else None,
                            raw_expires_at=raw_expiry if raw_enabled else None,
                        )
                        step_index += 1

                    await self.run_repo.complete_run(
                        run,
                        status="completed",
                        output_message=event.data.get("message"),
                        prompt_tokens=event.data.get("promptTokens", 0),
                        completion_tokens=event.data.get("completionTokens", 0),
                        total_tokens=event.data.get("totalTokens", 0),
                        cost_usd=event.data.get("costUsd"),
                        blocks=event.data.get("blocks"),
                    )
                    await self.session_repo.touch_session(session, title=_derive_title(message))
                    await self.db.commit()
                    yield AgentLoopEvent(
                        event="run_complete",
                        data={**event.data, "runId": run.id, "sessionId": session_id},
                    )
        except Exception as exc:
            await self.run_repo.complete_run(
                run,
                status="failed",
                output_message=str(exc),
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=None,
                run_metadata={"error": str(exc)},
            )
            await self.db.commit()
            yield AgentLoopEvent(
                event="error",
                data={"runId": run.id, "sessionId": session_id, "message": str(exc)},
            )

    async def _load_history(self, session_id: str, *, max_turns: int = 10) -> list[dict[str, str]]:
        """Prior completed turns of a session as plain user/assistant messages."""
        prior = await self.run_repo.list_runs_for_session(session_id)
        turns: list[dict[str, str]] = []
        for run in prior:
            if run.status != "completed" or not run.output_message:
                continue
            turns.append({"role": "user", "content": run.input_message})
            turns.append({"role": "assistant", "content": run.output_message})
        if len(turns) > max_turns * 2:
            turns = turns[-max_turns * 2 :]
        return turns

    async def _build_system_prompt(
        self,
        *,
        base_prompt: str,
        tenant_ctx: TenantContext,
        tool_registry: AgentToolRegistry,
        message: str,
        agent_key: str,
        session_id: str,
    ) -> str:
        """Assemble the system prompt: base + user context + tools + memory."""
        sections: list[str] = []

        user_context = await self._build_user_context(tenant_ctx)
        if user_context:
            sections.append(user_context)

        tool_catalog = _build_tool_catalog(tool_registry)
        if tool_catalog:
            sections.append(tool_catalog)

        memory_service = MemoryService(self.db)
        try:
            memory_context = await memory_service.build_injection_context(
                tenant_ctx=tenant_ctx,
                user_message=message,
                agent_key=agent_key,
                session_id=session_id,
            )
        except Exception:
            memory_context = ""
        if memory_context:
            sections.append(memory_context)

        if not sections:
            return base_prompt
        return base_prompt + "\n\n" + "\n\n".join(sections)

    async def _build_user_context(self, tenant_ctx: TenantContext) -> str:
        """Tell the agent whose behalf it acts on and which integrations exist."""
        providers: list[str] = []
        try:
            team_ids = [tenant_ctx.team_id] if tenant_ctx.team_id else []
            connections = await self.token_service.list_connections(
                user_id=tenant_ctx.user_id,
                tenant_id=tenant_ctx.tenant_id,
                team_ids=team_ids,
                tenant_role=tenant_ctx.tenant_role,
            )
            providers = sorted({c["provider"] for c in connections})
        except Exception:
            providers = []

        integrations = ", ".join(providers) if providers else "none connected yet"
        return (
            "## USER CONTEXT\n"
            "You are acting on behalf of the current user via their own OAuth tokens.\n"
            f"- Connected integrations: {integrations}\n"
            "If a required integration is not connected, say so and ask the user to "
            "connect it in Settings instead of guessing."
        )

    def _apply_source_guard(
        self,
        *,
        event: AgentLoopEvent,
        user_message: str,
        tool_registry: AgentToolRegistry,
    ) -> None:
        """Append a warning if the user named a source the agent never queried."""
        steps = event.data.get("stepsTrace", [])
        tools_used = [step.get("name") for step in steps if step.get("stepType") == "tool_result" and step.get("name")]
        warnings = check_source_mismatch(
            user_message=user_message,
            tools_used=tools_used,
            available_providers=_available_providers(tool_registry),
        )
        if not warnings:
            return

        note = format_warnings(warnings)
        base_msg = event.data.get("message") or ""
        event.data["message"] = f"{base_msg}\n\n{note}" if base_msg else note
        steps.append(
            {
                "stepIndex": len(steps),
                "stepType": "guard",
                "name": "source_routing_guard",
                "inputData": {"tools_used": tools_used},
                "outputData": {
                    "warnings": [_warning_dict(w) for w in warnings],
                },
            }
        )
        event.data["stepsTrace"] = steps

    async def get_run(self, run_id: str, *, user_id: str) -> AgentRunResponse | None:
        run = await self.run_repo.get_run(run_id, user_id=user_id)
        if run is None:
            return None
        steps = await self.run_repo.get_steps(run_id)
        return _to_run_response(run, steps)

    async def get_run_raw(self, run_id: str) -> dict[str, Any] | None:
        """Full (raw) trace for admins; expired raw payloads are withheld."""
        run = await self.run_repo.get_run_any(run_id)
        if run is None:
            return None
        steps = await self.run_repo.get_steps(run_id)
        now = datetime.now(UTC)
        step_dicts: list[dict[str, Any]] = []
        for step in steps:
            expired = step.raw_expires_at is not None and step.raw_expires_at < now
            step_dicts.append(
                {
                    "id": step.id,
                    "stepIndex": step.step_index,
                    "stepType": step.step_type,
                    "name": step.name,
                    "inputData": step.input_data,
                    "outputData": step.output_data,
                    "rawInputData": None if expired else step.raw_input_data,
                    "rawOutputData": None if expired else step.raw_output_data,
                    "rawExpiresAt": (step.raw_expires_at.isoformat() if step.raw_expires_at else None),
                    "rawExpired": expired,
                    "createdAt": step.created_at.isoformat(),
                }
            )
        return {
            "id": run.id,
            "sessionId": run.session_id,
            "agentKey": run.agent_key,
            "status": run.status,
            "inputMessage": run.input_message,
            "outputMessage": run.output_message,
            "systemPrompt": run.system_prompt,
            "model": run.model,
            "tenantId": run.tenant_id,
            "userId": run.user_id,
            "steps": step_dicts,
        }

    async def purge_expired_raw(self) -> int:
        """Housekeeping: drop raw payloads past their retention window."""
        purged = await self.run_repo.purge_expired_raw()
        if purged:
            await self.db.commit()
        return purged

    async def list_runs(
        self,
        *,
        tenant_ctx: TenantContext,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[AgentRunResponse], int]:
        runs, total = await self.run_repo.list_runs(
            user_id=tenant_ctx.user_id,
            tenant_id=tenant_ctx.tenant_id,
            limit=limit,
            offset=offset,
        )
        responses: list[AgentRunResponse] = []
        for run in runs:
            steps = await self.run_repo.get_steps(run.id)
            responses.append(_to_run_response(run, steps))
        return responses, total

    async def list_sessions(
        self,
        *,
        tenant_ctx: TenantContext,
        limit: int = 30,
        offset: int = 0,
    ) -> tuple[list[AgentSessionSummary], int]:
        sessions, total = await self.session_repo.list_sessions(
            user_id=tenant_ctx.user_id,
            tenant_id=tenant_ctx.tenant_id,
            limit=limit,
            offset=offset,
        )
        return [_to_session_summary(s) for s in sessions], total

    async def get_session_detail(self, session_id: str, *, user_id: str) -> AgentSessionDetail | None:
        session = await self.session_repo.get_session(session_id, user_id=user_id)
        if session is None:
            return None
        runs = await self.run_repo.list_runs_for_session(session_id)
        run_responses: list[AgentRunResponse] = []
        for run in runs:
            steps = await self.run_repo.get_steps(run.id)
            run_responses.append(_to_run_response(run, steps))
        summary = _to_session_summary(session)
        return AgentSessionDetail(**summary.model_dump(), runs=run_responses)


def _raw_expiry() -> datetime | None:
    """Retention deadline for raw trace payloads, or None if kept indefinitely."""
    days = settings.ai.audit_raw_retention_days
    if days <= 0:
        return None
    return datetime.now(UTC) + timedelta(days=days)


def _available_providers(tool_registry: AgentToolRegistry) -> set[str]:
    """Providers reachable via the current tool registry (e.g. {jira, gitlab}).

    Uses the full catalog (including deferred tools) so source-routing guards
    stay accurate when tool search has not yet activated provider tools.
    """
    providers: set[str] = set()
    for tool in tool_registry.all_openai_tools():
        name = tool.get("function", {}).get("name", "")
        provider = provider_of_tool(name)
        if provider:
            providers.add(provider)
    return providers


def _warning_dict(warning: SourceRoutingWarning) -> dict[str, str]:
    return {
        "provider": warning.provider,
        "reason": warning.reason,
        "message": warning.message,
    }


def _derive_title(message: str) -> str:
    """First line of the user's message, trimmed, as a session title."""
    text = " ".join(message.strip().split())
    if len(text) <= 60:
        return text
    return text[:59].rstrip() + "…"


def _build_tool_catalog(tool_registry: AgentToolRegistry) -> str:
    """Render active tools into the system prompt so names never drift."""
    tools = tool_registry.openai_tools()
    if not tools and not tool_registry.has_deferred():
        return ""
    lines = ["## AVAILABLE TOOLS"]
    for tool in tools:
        fn = tool.get("function", {})
        name = fn.get("name", "")
        description = (fn.get("description") or "").strip().split("\n")[0]
        lines.append(f"- `{name}` — {description}")
    if tool_registry.has_deferred():
        lines.append(
            "- Call `tool_search` with a query to discover and load more tools."
        )
    return "\n".join(lines)


def _to_session_summary(session: AgentSessionDB) -> AgentSessionSummary:
    return AgentSessionSummary(
        id=session.id,
        agentKey=session.agent_key,
        title=session.title,
        createdAt=session.created_at,
        lastMessageAt=session.last_message_at,
    )


def _to_run_response(run: AgentRunDB, steps: list[AgentRunStepDB]) -> AgentRunResponse:
    from app.modules.agent.schemas import RichBlock

    return AgentRunResponse(
        id=run.id,
        sessionId=run.session_id,
        agentKey=run.agent_key,
        status=run.status,
        inputMessage=run.input_message,
        outputMessage=run.output_message,
        systemPrompt=run.system_prompt,
        model=run.model,
        promptTokens=run.prompt_tokens,
        completionTokens=run.completion_tokens,
        totalTokens=run.total_tokens,
        costUsd=run.cost_usd,
        blocks=[RichBlock(**block) for block in (run.blocks or [])],
        steps=[
            AgentRunStepResponse(
                id=step.id,
                stepIndex=step.step_index,
                stepType=step.step_type,
                name=step.name,
                inputData=step.input_data,
                outputData=step.output_data,
                createdAt=step.created_at,
            )
            for step in steps
        ],
        createdAt=run.created_at,
        completedAt=run.completed_at,
    )
