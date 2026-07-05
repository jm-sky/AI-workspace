"""Type definitions for AI providers."""

from typing import Any, TypedDict


class Message(TypedDict):
    """Chat message structure."""

    role: str  # 'user', 'assistant', 'system'
    content: str


class TokenUsage(TypedDict):
    """Token usage information."""

    input: int
    output: int
    total: int


class CostInfo(TypedDict, total=False):
    """Cost information (optional)."""

    input: float
    output: float
    total: float


class ChatResponse(TypedDict):
    """Response from chat completion."""

    content: str
    model: str
    provider: str
    tokens: TokenUsage
    cost: CostInfo | None
    raw_response: dict[str, Any]
