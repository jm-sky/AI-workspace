"""Tool-calling agent loop with OpenRouter."""

import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.modules.agent.exceptions import (
    AgentMaxStepsExceededError,
    AgentNotConfiguredError,
    AgentToolError,
)
from app.modules.agent.tools.base import AgentToolRegistry
from app.modules.ai.utils.models_config import calculate_cost

logger = logging.getLogger(__name__)


@dataclass
class AgentLoopEvent:
    """SSE event emitted during agent execution."""

    event: str
    data: dict[str, Any]


@dataclass
class AgentLoopResult:
    """Final result of an agent run."""

    message: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float | None = None
    blocks: list[dict[str, Any]] = field(default_factory=list)
    steps_trace: list[dict[str, Any]] = field(default_factory=list)


class AgentLoopService:
    """Own tool-calling loop against OpenRouter (OpenAI-compatible API)."""

    def __init__(
        self,
        *,
        model: str,
        system_prompt: str,
        tool_registry: AgentToolRegistry,
        api_key: str | None = None,
        max_steps: int | None = None,
    ):
        key = api_key or settings.ai.openrouter_api_key
        if not key:
            raise AgentNotConfiguredError("OPENROUTER_API_KEY is not configured")

        self.model = model
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry
        self.max_steps = max_steps or settings.ai.agent_max_steps
        self.client = AsyncOpenAI(
            api_key=key,
            base_url=settings.ai.openrouter_base_url,
        )

    async def run(self, user_message: str) -> AgentLoopResult:
        """Execute the loop and return the final result."""
        result: AgentLoopResult | None = None
        async for event in self.run_stream(user_message):
            if event.event == "run_complete":
                payload = event.data
                result = AgentLoopResult(
                    message=payload.get("message", ""),
                    prompt_tokens=payload.get("promptTokens", 0),
                    completion_tokens=payload.get("completionTokens", 0),
                    total_tokens=payload.get("totalTokens", 0),
                    cost_usd=payload.get("costUsd"),
                    blocks=payload.get("blocks", []),
                    steps_trace=payload.get("stepsTrace", []),
                )
        if result is None:
            raise AgentMaxStepsExceededError("Agent loop ended without a result")
        return result

    async def run_stream(self, user_message: str) -> AsyncIterator[AgentLoopEvent]:
        """Execute the loop, yielding SSE-friendly events."""
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        tools = self.tool_registry.openai_tools()

        prompt_tokens = 0
        completion_tokens = 0
        steps_trace: list[dict[str, Any]] = []
        step_index = 0

        for iteration in range(self.max_steps):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
            )

            usage = response.usage
            if usage:
                prompt_tokens += usage.prompt_tokens or 0
                completion_tokens += usage.completion_tokens or 0

            choice = response.choices[0]
            assistant_message = choice.message
            assistant_payload = assistant_message.model_dump(exclude_none=True)
            messages.append(assistant_payload)

            model_step = {
                "stepIndex": step_index,
                "stepType": "model",
                "name": self.model,
                "inputData": {"messages_count": len(messages)},
                "outputData": {
                    "finish_reason": choice.finish_reason,
                    "tool_calls": [
                        tc.model_dump() for tc in (assistant_message.tool_calls or [])
                    ],
                },
            }
            steps_trace.append(model_step)
            yield AgentLoopEvent(
                event="step",
                data={
                    "type": "model",
                    "stepIndex": step_index,
                    "finishReason": choice.finish_reason,
                },
            )
            step_index += 1

            tool_calls = assistant_message.tool_calls or []
            if not tool_calls:
                content = assistant_message.content or ""
                total_tokens = prompt_tokens + completion_tokens
                cost = calculate_cost(self.model, prompt_tokens, completion_tokens)
                blocks = _build_blocks_from_trace(steps_trace, content)
                yield AgentLoopEvent(
                    event="run_complete",
                    data={
                        "message": content,
                        "promptTokens": prompt_tokens,
                        "completionTokens": completion_tokens,
                        "totalTokens": total_tokens,
                        "costUsd": cost,
                        "blocks": blocks,
                        "stepsTrace": steps_trace,
                    },
                )
                return

            for tool_call in tool_calls:
                fn = tool_call.function
                tool_name = fn.name
                try:
                    arguments = json.loads(fn.arguments or "{}")
                except json.JSONDecodeError:
                    arguments = {}

                yield AgentLoopEvent(
                    event="step",
                    data={
                        "type": "tool_call",
                        "stepIndex": step_index,
                        "tool": tool_name,
                        "arguments": arguments,
                    },
                )

                tool_step_input = {"tool": tool_name, "arguments": arguments}
                try:
                    tool_result = await self.tool_registry.execute(tool_name, arguments)
                    if "error" in tool_result:
                        raise AgentToolError(str(tool_result["error"]))
                except AgentToolError as exc:
                    tool_result = {"error": str(exc)}
                except Exception as exc:  # noqa: BLE001 — surface to model
                    logger.exception("Tool %s failed", tool_name)
                    tool_result = {"error": str(exc)}

                tool_step = {
                    "stepIndex": step_index,
                    "stepType": "tool_result",
                    "name": tool_name,
                    "inputData": tool_step_input,
                    "outputData": tool_result,
                }
                steps_trace.append(tool_step)
                step_index += 1

                yield AgentLoopEvent(
                    event="step",
                    data={
                        "type": "tool_result",
                        "stepIndex": step_index - 1,
                        "tool": tool_name,
                        "result": tool_result,
                    },
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result, default=str),
                    }
                )

        raise AgentMaxStepsExceededError(
            f"Agent exceeded maximum steps ({self.max_steps})"
        )


def _build_blocks_from_trace(
    steps_trace: list[dict[str, Any]],
    markdown: str,
) -> list[dict[str, Any]]:
    """Build minimal rich blocks (cards/tables) for the 360° view."""
    _ = markdown
    blocks: list[dict[str, Any]] = []

    jira_data: dict[str, Any] | None = None
    gitlab_rows: list[dict[str, Any]] = []

    for step in steps_trace:
        if step.get("stepType") != "tool_result":
            continue
        name = step.get("name")
        output = step.get("outputData") or {}
        if name == "jira_get_issue" and "error" not in output:
            jira_data = output
        if name == "gitlab_search_by_jira_key" and "error" not in output:
            for mr in output.get("merge_requests", []):
                gitlab_rows.append(
                    {
                        "type": "MR",
                        "title": mr.get("title"),
                        "state": mr.get("state"),
                        "url": mr.get("url"),
                    }
                )
            for issue in output.get("issues", []):
                gitlab_rows.append(
                    {
                        "type": "Issue",
                        "title": issue.get("title"),
                        "state": issue.get("state"),
                        "url": issue.get("url"),
                    }
                )

    if jira_data:
        blocks.append(
            {
                "type": "card",
                "title": f"Jira {jira_data.get('key', '')}",
                "data": {
                    "summary": jira_data.get("summary"),
                    "status": jira_data.get("status"),
                    "client": jira_data.get("client"),
                    "url": jira_data.get("url"),
                },
            }
        )

    if gitlab_rows:
        blocks.append(
            {
                "type": "table",
                "title": "GitLab",
                "data": {"columns": ["type", "title", "state", "url"], "rows": gitlab_rows},
            }
        )

    return blocks
