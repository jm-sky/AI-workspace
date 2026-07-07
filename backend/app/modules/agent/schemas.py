"""Pydantic schemas for agent API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    """User message to the workspace agent."""

    message: str = Field(..., min_length=1, max_length=8000)
    agentKey: str = Field(default="github-workspace", alias="agent_key")
    model: str | None = None

    model_config = {"populate_by_name": True}


class RichBlock(BaseModel):
    """Rich UI block rendered alongside Markdown."""

    type: Literal["card", "table", "markdown"]
    title: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class AgentRunStepResponse(BaseModel):
    """Single trace step."""

    id: str
    stepIndex: int
    stepType: str
    name: str | None = None
    inputData: dict[str, Any] | None = None
    outputData: dict[str, Any] | None = None
    createdAt: datetime


class AgentRunResponse(BaseModel):
    """Completed or in-progress agent run."""

    id: str
    agentKey: str
    status: str
    inputMessage: str
    outputMessage: str | None = None
    systemPrompt: str
    model: str
    promptTokens: int
    completionTokens: int
    totalTokens: int
    costUsd: float | None = None
    blocks: list[RichBlock] = Field(default_factory=list)
    steps: list[AgentRunStepResponse] = Field(default_factory=list)
    createdAt: datetime
    completedAt: datetime | None = None


class AgentRunsListResponse(BaseModel):
    """Paginated list of runs."""

    runs: list[AgentRunResponse]
    total: int
