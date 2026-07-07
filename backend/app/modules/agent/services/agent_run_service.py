"""High-level agent run orchestration with persistence."""

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agent.exceptions import (
    AgentNotConfiguredError,
    AgentToolsDisabledError,
)
from app.modules.agent.prompts.jira_360 import JIRA_360_SYSTEM_PROMPT
from app.modules.agent.repositories import AgentRunRepository
from app.modules.agent.schemas import AgentRunResponse, AgentRunStepResponse
from app.modules.agent.services.agent_loop import AgentLoopEvent, AgentLoopService
from app.modules.agent.tools import build_tool_registry
from app.modules.integrations.service import IntegrationTokenService
from app.modules.tenants.service import TenantContext
from app.modules.workspace_config.repositories import WorkspaceConfigRepository
from app.modules.workspace_config.resolver import WorkspaceConfigResolver


AGENT_PROMPTS: dict[str, str] = {
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
        if model and model in effective.allowedModels:
            return model
        if effective.allowedModels:
            return effective.allowedModels[0]
        raise AgentNotConfiguredError("No allowed model configured for workspace")

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
        agent_key: str = "jira-360",
        model: str | None = None,
    ) -> AsyncIterator[AgentLoopEvent]:
        resolved_model = await self._resolve_model(
            user_id=tenant_ctx.user_id,
            tenant_ctx=tenant_ctx,
            requested_model=model,
        )
        system_prompt = self._system_prompt(agent_key)

        run = await self.run_repo.create_run(
            tenant_id=tenant_ctx.tenant_id,
            user_id=tenant_ctx.user_id,
            agent_key=agent_key,
            input_message=message,
            system_prompt=system_prompt,
            model=resolved_model,
        )
        await self.db.commit()

        tool_registry = build_tool_registry(
            tenant_ctx=tenant_ctx,
            token_service=self.token_service,
        )
        loop = AgentLoopService(
            model=resolved_model,
            system_prompt=system_prompt,
            tool_registry=tool_registry,
        )

        step_index = 0

        try:
            async for event in loop.run_stream(message):
                if event.event == "step":
                    yield AgentLoopEvent(
                        event=event.event,
                        data={**event.data, "runId": run.id},
                    )
                elif event.event == "run_complete":
                    for trace_step in event.data.get("stepsTrace", []):
                        await self.run_repo.add_step(
                            run_id=run.id,
                            step_index=trace_step.get("stepIndex", step_index),
                            step_type=trace_step.get("stepType", "step"),
                            name=trace_step.get("name"),
                            input_data=trace_step.get("inputData"),
                            output_data=trace_step.get("outputData"),
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
                    await self.db.commit()
                    yield AgentLoopEvent(
                        event="run_complete",
                        data={**event.data, "runId": run.id},
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
                data={"runId": run.id, "message": str(exc)},
            )

    async def get_run(self, run_id: str, *, user_id: str) -> AgentRunResponse | None:
        run = await self.run_repo.get_run(run_id, user_id=user_id)
        if run is None:
            return None
        steps = await self.run_repo.get_steps(run_id)
        return _to_run_response(run, steps)

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


def _to_run_response(run, steps) -> AgentRunResponse:
    from app.modules.agent.schemas import RichBlock

    return AgentRunResponse(
        id=run.id,
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
