"""Agent tool definitions and execution (MCP-compatible schemas, in-process bridge)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentToolDefinition:
    """OpenAI / MCP-compatible tool definition."""

    name: str
    description: str
    parameters: dict[str, Any]

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class AgentTool(ABC):
    """Executable agent tool."""

    @property
    @abstractmethod
    def definition(self) -> AgentToolDefinition:
        """Tool schema for the LLM."""

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Run the tool and return JSON-serializable result."""


class AgentToolRegistry:
    """Registry of tools available to the agent loop."""

    def __init__(self, tools: list[AgentTool] | None = None):
        self._tools: dict[str, AgentTool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: AgentTool) -> None:
        self._tools[tool.definition.name] = tool

    def openai_tools(self) -> list[dict[str, Any]]:
        return [tool.definition.to_openai_tool() for tool in self._tools.values()]

    async def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(name)
        if tool is None:
            return {"error": f"Unknown tool: {name}"}
        return await tool.execute(arguments)
