"""AI models configuration for OpenRouter.

This module defines the curated AI models available in the application.
Costs are per 1 million tokens; `tier` describes raw capability, not price.

`MODELS` is the curated fallback catalog. At runtime the live OpenRouter
catalog is fetched by `app.modules.ai.services.model_catalog_service` and
published here via `set_catalog_snapshot`, so that the synchronous readers
below (`get_model_by_id`, `calculate_cost`) can price models that are not in
the curated list without becoming async.
"""

from typing import Any

# Capability tiers, strongest first. Used for sorting and badges in the picker.
TIERS: tuple[str, ...] = ("frontier", "balanced", "fast")

# Live catalog, keyed by model id. Empty until the first successful fetch, in
# which case every lookup falls back to the curated MODELS list below.
_SNAPSHOT: dict[str, dict[str, Any]] = {}

MODELS: list[dict[str, Any]] = [
    # Anthropic Models
    {
        "id": "anthropic/claude-opus-4.8",
        "name": "Claude Opus 4.8",
        "provider": "Anthropic",
        "description": "Most capable Anthropic model for long agentic runs",
        "context_length": 1000000,
        "cost_per_1m_input": 5.00,
        "cost_per_1m_output": 25.00,
        "tier": "frontier",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    {
        "id": "anthropic/claude-sonnet-5",
        "name": "Claude Sonnet 5",
        "provider": "Anthropic",
        "description": "Frontier reasoning at a fraction of Opus pricing",
        "context_length": 1000000,
        "cost_per_1m_input": 2.00,
        "cost_per_1m_output": 10.00,
        "tier": "frontier",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": True,
    },
    {
        "id": "anthropic/claude-sonnet-4.5",
        "name": "Claude Sonnet 4.5",
        "provider": "Anthropic",
        "description": "Strong reasoning and tool-calling for complex agent tasks",
        "context_length": 1000000,
        "cost_per_1m_input": 3.00,
        "cost_per_1m_output": 15.00,
        "tier": "balanced",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    {
        "id": "anthropic/claude-haiku-4.5",
        "name": "Claude Haiku 4.5",
        "provider": "Anthropic",
        "description": "Fast and affordable Anthropic model",
        "context_length": 200000,
        "cost_per_1m_input": 1.00,
        "cost_per_1m_output": 5.00,
        "tier": "fast",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    # OpenAI Models
    {
        "id": "openai/gpt-5.4",
        "name": "GPT-5.4",
        "provider": "OpenAI",
        "description": "OpenAI flagship with reasoning and huge context",
        "context_length": 1050000,
        "cost_per_1m_input": 2.50,
        "cost_per_1m_output": 15.00,
        "tier": "frontier",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    {
        "id": "openai/gpt-4o",
        "name": "GPT-4o",
        "provider": "OpenAI",
        "description": "Capable general-purpose model with vision support",
        "context_length": 128000,
        "cost_per_1m_input": 2.50,
        "cost_per_1m_output": 10.00,
        "tier": "balanced",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": False,
        "recommended": False,
    },
    {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "description": "Fast and affordable model, great for most tasks",
        "context_length": 128000,
        "cost_per_1m_input": 0.15,
        "cost_per_1m_output": 0.60,
        "tier": "fast",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": False,
        "recommended": True,
    },
    {
        "id": "openai/gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "OpenAI",
        "description": "Fast and cost-effective for simple tasks",
        "context_length": 16385,
        "cost_per_1m_input": 0.50,
        "cost_per_1m_output": 1.50,
        "tier": "fast",
        "supports_vision": False,
        "supports_tools": True,
        "supports_reasoning": False,
        "recommended": False,
    },
    # Google Models
    {
        "id": "google/gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "provider": "Google",
        "description": "Advanced reasoning and tool-calling with large context",
        "context_length": 1048576,
        "cost_per_1m_input": 0.30,
        "cost_per_1m_output": 2.50,
        "tier": "balanced",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    {
        "id": "google/gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash Lite",
        "provider": "Google",
        "description": "Ultra-low latency and cost Google model",
        "context_length": 1048576,
        "cost_per_1m_input": 0.10,
        "cost_per_1m_output": 0.40,
        "tier": "fast",
        "supports_vision": True,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    # Open-weight Models
    {
        "id": "moonshotai/kimi-k2-thinking",
        "name": "Kimi K2 Thinking",
        "provider": "Moonshot AI",
        "description": "Open-weight reasoning model tuned for long tool chains",
        "context_length": 262144,
        "cost_per_1m_input": 0.60,
        "cost_per_1m_output": 2.50,
        "tier": "balanced",
        "supports_vision": False,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    {
        "id": "deepseek/deepseek-v4-flash",
        "name": "DeepSeek V4 Flash",
        "provider": "DeepSeek",
        "description": "Cheap reasoning model with million-token context",
        "context_length": 1048576,
        "cost_per_1m_input": 0.09,
        "cost_per_1m_output": 0.18,
        "tier": "fast",
        "supports_vision": False,
        "supports_tools": True,
        "supports_reasoning": True,
        "recommended": False,
    },
    {
        "id": "qwen/qwen3-30b-a3b-instruct-2507",
        "name": "Qwen3 30B A3B Instruct",
        "provider": "Qwen",
        "description": "MoE model optimized for agentic tool use and instruction following",
        "context_length": 131072,
        "cost_per_1m_input": 0.048,
        "cost_per_1m_output": 0.193,
        "tier": "fast",
        "supports_vision": False,
        "supports_tools": True,
        "supports_reasoning": False,
        "recommended": True,
    },
    {
        "id": "meta-llama/llama-3.1-70b-instruct",
        "name": "Llama 3.1 70B",
        "provider": "Meta",
        "description": "Open-source model with strong performance",
        "context_length": 131072,
        "cost_per_1m_input": 0.40,
        "cost_per_1m_output": 0.40,
        "tier": "balanced",
        "supports_vision": False,
        "supports_tools": True,
        "supports_reasoning": False,
        "recommended": False,
    },
    {
        "id": "meta-llama/llama-3.1-8b-instruct",
        "name": "Llama 3.1 8B",
        "provider": "Meta",
        "description": "Very affordable open-source model",
        "context_length": 131072,
        "cost_per_1m_input": 0.02,
        "cost_per_1m_output": 0.03,
        "tier": "fast",
        "supports_vision": False,
        "supports_tools": True,
        "supports_reasoning": False,
        "recommended": False,
    },
]


def set_catalog_snapshot(models: list[dict[str, Any]]) -> None:
    """Publish the live catalog for synchronous readers.

    Args:
        models: Mapped model dicts, each carrying the same keys as `MODELS`
    """
    _SNAPSHOT.clear()
    _SNAPSHOT.update({model["id"]: model for model in models})


def clear_catalog_snapshot() -> None:
    """Drop the live catalog, restoring the curated `MODELS` as the only source."""
    _SNAPSHOT.clear()


def has_live_catalog() -> bool:
    """Whether the live catalog has been loaded in this process.

    When it has not, `get_model_by_id` only knows the curated models, so callers
    must not treat a miss as proof that a model does not exist.
    """
    return bool(_SNAPSHOT)


def get_model_by_id(model_id: str) -> dict[str, Any] | None:
    """Get model configuration by ID.

    Args:
        model_id: Model identifier (e.g., "openai/gpt-4o-mini")

    Returns:
        Model configuration dict or None if not found
    """
    snapshot_model = _SNAPSHOT.get(model_id)
    if snapshot_model is not None:
        return snapshot_model
    return next((model for model in MODELS if model["id"] == model_id), None)


def get_recommended_models() -> list[dict[str, Any]]:
    """Get list of recommended models.

    Returns:
        List of recommended model configurations
    """
    return [model for model in MODELS if model.get("recommended", False)]


def calculate_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate cost in USD for token usage.

    Args:
        model_id: Model identifier
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens

    Returns:
        Cost in USD (rounded to 6 decimal places)
    """
    model = get_model_by_id(model_id)
    if not model:
        return 0.0

    input_cost = (prompt_tokens / 1_000_000) * model["cost_per_1m_input"]
    output_cost = (completion_tokens / 1_000_000) * model["cost_per_1m_output"]

    return float(round(input_cost + output_cost, 6))
