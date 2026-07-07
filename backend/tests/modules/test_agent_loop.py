"""Tests for agent tool-calling loop."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.agent.services.agent_loop import AgentLoopService
from app.modules.agent.tools.base import AgentTool, AgentToolDefinition, AgentToolRegistry


class _EchoTool(AgentTool):
    @property
    def definition(self) -> AgentToolDefinition:
        return AgentToolDefinition(
            name="echo",
            description="Echo input",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        )

    async def execute(self, arguments: dict) -> dict:
        return {"echo": arguments.get("text")}


def _make_completion(*, content: str | None = None, tool_calls=None, finish_reason="stop"):
    message = MagicMock()
    message.content = content
    message.tool_calls = tool_calls or []
    message.model_dump.return_value = {
        "role": "assistant",
        "content": content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in (tool_calls or [])
        ],
    }

    choice = MagicMock()
    choice.message = message
    choice.finish_reason = finish_reason

    usage = MagicMock()
    usage.prompt_tokens = 10
    usage.completion_tokens = 5
    usage.total_tokens = 15

    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    return response


@pytest.mark.asyncio
async def test_agent_loop_completes_without_tools():
    registry = AgentToolRegistry()
    service = AgentLoopService(
        model="google/gemini-2.0-flash-001",
        system_prompt="You are helpful.",
        tool_registry=registry,
        api_key="test-key",
        max_steps=3,
    )

    completion = _make_completion(content="Hello from agent")

    with patch.object(
        service.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=completion,
    ):
        result = await service.run("Hi")

    assert result.message == "Hello from agent"
    assert result.total_tokens == 15


@pytest.mark.asyncio
async def test_agent_loop_executes_tool_then_responds():
    registry = AgentToolRegistry(tools=[_EchoTool()])

    tool_call = MagicMock()
    tool_call.id = "call-1"
    tool_call.function.name = "echo"
    tool_call.function.arguments = json.dumps({"text": "IT-123"})

    first = _make_completion(tool_calls=[tool_call], finish_reason="tool_calls")
    second = _make_completion(content="Done: IT-123", finish_reason="stop")

    service = AgentLoopService(
        model="google/gemini-2.0-flash-001",
        system_prompt="Test",
        tool_registry=registry,
        api_key="test-key",
        max_steps=5,
    )

    mock_create = AsyncMock(side_effect=[first, second])
    with patch.object(service.client.chat.completions, "create", mock_create):
        result = await service.run("Run echo")

    assert result.message == "Done: IT-123"
    assert mock_create.await_count == 2
    assert any(step.get("stepType") == "tool_result" for step in result.steps_trace)
