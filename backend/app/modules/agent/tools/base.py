"""Agent tool definitions and execution (MCP-compatible schemas, in-process bridge)."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
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
    """Registry of tools available to the agent loop.

    Supports an optional active subset for tool search: the full catalog stays
    executable, while ``openai_tools()`` only exposes currently loaded schemas.
    """

    def __init__(self, tools: list[AgentTool] | None = None):
        self._tools: dict[str, AgentTool] = {}
        # None means every registered tool is active (pass-all / no search mode).
        self._active: set[str] | None = None
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: AgentTool) -> None:
        self._tools[tool.definition.name] = tool

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def get(self, name: str) -> AgentTool | None:
        return self._tools.get(name)

    def set_active(self, names: Iterable[str]) -> None:
        """Restrict OpenAI schemas to the given names (must already be registered)."""
        self._active = {name for name in names if name in self._tools}

    def activate(self, names: Iterable[str]) -> list[str]:
        """Add tools to the active set. Returns names that are now active."""
        if self._active is None:
            self._active = set(self._tools.keys())
        activated: list[str] = []
        for name in names:
            if name not in self._tools:
                continue
            self._active.add(name)
            activated.append(name)
        return activated

    def openai_tools(self) -> list[dict[str, Any]]:
        """Schemas for the LLM (active subset only)."""
        if self._active is None:
            return [tool.definition.to_openai_tool() for tool in self._tools.values()]
        return [
            tool.definition.to_openai_tool()
            for name, tool in self._tools.items()
            if name in self._active
        ]

    def all_openai_tools(self) -> list[dict[str, Any]]:
        """Full catalog schemas (including deferred)."""
        return [tool.definition.to_openai_tool() for tool in self._tools.values()]

    def deferred_openai_tools(self) -> list[dict[str, Any]]:
        """Schemas not yet loaded into the LLM tools array."""
        if self._active is None:
            return []
        return [
            tool.definition.to_openai_tool()
            for name, tool in self._tools.items()
            if name not in self._active
        ]

    def has_deferred(self) -> bool:
        if self._active is None:
            return False
        return any(name not in self._active for name in self._tools)

    async def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(name)
        if tool is None:
            return {"error": f"Unknown tool: {name}"}
        return await tool.execute(arguments)
