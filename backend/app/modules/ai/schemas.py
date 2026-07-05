"""Pydantic schemas for AI module API."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Chat Schemas
# ============================================================================


class AiChatMessage(BaseModel):
    """Single chat message."""

    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")


class AiChatRequest(BaseModel):
    """Request for AI chat."""

    message: str = Field(
        ..., min_length=1, max_length=10000, description="User message"
    )
    history: list[AiChatMessage] = Field(
        default_factory=list, description="Previous messages in conversation"
    )
    context: dict[str, Any] = Field(
        default_factory=dict, description="Optional context data"
    )
    model: str | None = Field(None, description="Override default model")
    max_tokens: int | None = Field(
        None, ge=1, le=4000, description="Max tokens for response"
    )
    temperature: float = Field(
        default=1.0, ge=0.0, le=2.0, description="Temperature for sampling"
    )


class StructuredOutput(BaseModel):
    """Structured output from AI."""

    action: str | None = Field(None, description="Action to perform")
    data: dict[str, Any] = Field(default_factory=dict, description="Action data")


class AiChatResponse(BaseModel):
    """Response from AI chat."""

    message: str = Field(..., description="AI response message")
    structured_output: StructuredOutput | None = Field(
        None, description="Parsed structured output"
    )
    tokens: dict[str, int] = Field(
        ..., description="Token usage (prompt, completion, total)"
    )
    cost: float | None = Field(None, description="Estimated cost in USD")
    model: str = Field(..., description="Model used")
    prompt: str | None = Field(
        None, description="Full prompt sent to AI (for debugging, admin only)"
    )


# ============================================================================
# Models Schemas
# ============================================================================


class AiModel(BaseModel):
    """AI model information."""

    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Model display name")
    provider: str = Field(..., description="Provider name")
    description: str | None = Field(None, description="Model description")
    context_length: int = Field(..., description="Maximum context length in tokens")
    cost_per_1m_input: float = Field(..., description="Cost per 1M input tokens in USD")
    cost_per_1m_output: float = Field(
        ..., description="Cost per 1M output tokens in USD"
    )
    recommended: bool = Field(default=False, description="Whether model is recommended")


class AiModelsResponse(BaseModel):
    """Response with available models."""

    models: list[AiModel] = Field(..., description="List of available models")


# ============================================================================
# Settings Schemas
# ============================================================================


class AiSettings(BaseModel):
    """AI user settings."""

    id: UUID = Field(..., description="Settings ID")
    user_id: str = Field(..., alias="userId", serialization_alias="userId")
    use_own_token: bool = Field(
        ..., alias="useOwnToken", serialization_alias="useOwnToken"
    )
    has_token: bool = Field(..., alias="hasToken", serialization_alias="hasToken")
    selected_model: str = Field(
        ..., alias="selectedModel", serialization_alias="selectedModel"
    )
    context_fields: dict[str, Any] = Field(
        ..., alias="contextFields", serialization_alias="contextFields"
    )
    max_tokens: int | None = Field(
        None, alias="maxTokens", serialization_alias="maxTokens"
    )
    temperature: float = Field(..., description="Temperature setting")
    monthly_token_limit: int | None = Field(
        None, alias="monthlyTokenLimit", serialization_alias="monthlyTokenLimit"
    )
    monthly_tokens_used: int = Field(
        default=0, alias="monthlyTokensUsed", serialization_alias="monthlyTokensUsed"
    )
    monthly_cost_limit: float | None = Field(
        None, alias="monthlyCostLimit", serialization_alias="monthlyCostLimit"
    )
    monthly_cost_used: float = Field(
        default=0.0, alias="monthlyCostUsed", serialization_alias="monthlyCostUsed"
    )
    created_at: datetime = Field(
        ..., alias="createdAt", serialization_alias="createdAt"
    )
    updated_at: datetime = Field(
        ..., alias="updatedAt", serialization_alias="updatedAt"
    )

    model_config = {"populate_by_name": True}


class AiUpdateSettings(BaseModel):
    """Update AI settings request."""

    selected_model: str | None = Field(
        None,
        alias="selectedModel",
        serialization_alias="selectedModel",
        description="Model to select",
    )
    context_fields: dict[str, Any] | None = Field(
        None,
        alias="contextFields",
        serialization_alias="contextFields",
        description="Context fields configuration",
    )
    max_tokens: int | None = Field(
        None,
        alias="maxTokens",
        serialization_alias="maxTokens",
        ge=1,
        le=4000,
        description="Max tokens override",
    )
    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Temperature setting"
    )

    model_config = {"populate_by_name": True}


class AiSetTokenRequest(BaseModel):
    """Set API token request."""

    api_token: str = Field(
        ...,
        alias="apiToken",
        serialization_alias="apiToken",
        min_length=10,
        max_length=500,
        description="OpenRouter API token",
    )

    model_config = {"populate_by_name": True}


class AiSetTokenResponse(BaseModel):
    """Set API token response."""

    success: bool = Field(..., description="Whether token was set successfully")
    message: str = Field(..., description="Result message")


# ============================================================================
# History Schemas
# ============================================================================


class AiHistoryItem(BaseModel):
    """AI history item (list view)."""

    id: UUID = Field(..., description="History ID")
    operation_type: str = Field(
        ...,
        description="Operation type (chat, classify, etc.)",
        serialization_alias="operationType",
    )
    final_prompt: str = Field(
        ..., description="Final prompt sent to AI", serialization_alias="finalPrompt"
    )
    context_data: dict[str, Any] | None = Field(
        None, description="Context data", serialization_alias="contextData"
    )
    response_data: dict[str, Any] = Field(
        ..., description="Response data", serialization_alias="responseData"
    )
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Provider name")
    tokens: dict[str, int] = Field(
        ..., description="Token usage (input, output, total)"
    )
    cost: dict[str, float] = Field(
        ...,
        description="Cost breakdown (input, output, total)",
        serialization_alias="cost",
    )
    duration_ms: int | None = Field(
        None, description="Duration in milliseconds", serialization_alias="durationMs"
    )
    used_own_token: bool = Field(
        ...,
        description="Whether user's own token was used",
        serialization_alias="usedOwnToken",
    )
    container_ids: list[str] | None = Field(
        None,
        description="Container IDs associated with this history entry",
        serialization_alias="containerIds",
    )
    created_at: datetime = Field(
        ..., description="Creation timestamp", serialization_alias="createdAt"
    )

    model_config = {"populate_by_name": True}


class AiHistoryDetail(BaseModel):
    """AI history detail (single view)."""

    id: UUID = Field(..., description="History ID")
    user_id: str = Field(..., description="User ID", serialization_alias="userId")
    operation_type: str = Field(
        ..., description="Operation type", serialization_alias="operationType"
    )
    model: str = Field(..., description="Model used")
    prompt_tokens: int = Field(
        ..., description="Prompt tokens", serialization_alias="promptTokens"
    )
    completion_tokens: int = Field(
        ..., description="Completion tokens", serialization_alias="completionTokens"
    )
    total_tokens: int = Field(
        ..., description="Total tokens", serialization_alias="totalTokens"
    )
    cost_usd: float | None = Field(
        None, description="Cost in USD", serialization_alias="costUsd"
    )
    input_data: dict[str, Any] = Field(
        ..., description="Input data", serialization_alias="inputData"
    )
    output_data: dict[str, Any] = Field(
        ..., description="Output data", serialization_alias="outputData"
    )
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    container_ids: list[str] | None = Field(
        None,
        description="Container IDs associated with this history entry",
        serialization_alias="containerIds",
    )
    created_at: datetime = Field(
        ..., description="Creation timestamp", serialization_alias="createdAt"
    )

    model_config = {"populate_by_name": True}


class AiHistoryListResponse(BaseModel):
    """Response with history list."""

    items: list[AiHistoryItem] = Field(..., description="List of history items")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Limit used")
    offset: int = Field(..., description="Offset used")


class AiHistoryQuery(BaseModel):
    """Query parameters for history list."""

    limit: int = Field(
        default=50, ge=1, le=100, description="Number of items to return"
    )
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    operation_type: str | None = Field(None, description="Filter by operation type")
