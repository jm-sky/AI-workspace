"""AI models configuration for OpenRouter.

This module defines the 10 AI models available in the application.
Costs are per 1 million tokens.
"""

from typing import Any

# 10 AI Models Configuration
MODELS: list[dict[str, Any]] = [
    # OpenAI Models
    {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "description": "Fast and affordable model, great for most tasks",
        "context_length": 128000,
        "cost_per_1m_input": 0.15,
        "cost_per_1m_output": 0.60,
        "recommended": True,
    },
    {
        "id": "openai/gpt-4o",
        "name": "GPT-4o",
        "provider": "OpenAI",
        "description": "Most capable OpenAI model with vision support",
        "context_length": 128000,
        "cost_per_1m_input": 2.50,
        "cost_per_1m_output": 10.00,
        "recommended": False,
    },
    {
        "id": "openai/gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "OpenAI",
        "description": "Fast and cost-effective for simple tasks",
        "context_length": 16385,
        "cost_per_1m_input": 0.50,
        "cost_per_1m_output": 1.50,
        "recommended": False,
    },
    # Anthropic Models
    {
        "id": "anthropic/claude-3.5-sonnet",
        "name": "Claude 3.5 Sonnet",
        "provider": "Anthropic",
        "description": "Excellent for structured output and analysis",
        "context_length": 200000,
        "cost_per_1m_input": 3.00,
        "cost_per_1m_output": 15.00,
        "recommended": True,
    },
    {
        "id": "anthropic/claude-3-haiku",
        "name": "Claude 3 Haiku",
        "provider": "Anthropic",
        "description": "Fast and affordable Anthropic model",
        "context_length": 200000,
        "cost_per_1m_input": 0.25,
        "cost_per_1m_output": 1.25,
        "recommended": False,
    },
    # Google Models
    {
        "id": "google/gemini-pro-1.5-exp",
        "name": "Gemini Pro 1.5",
        "provider": "Google",
        "description": "Google's most capable model with large context",
        "context_length": 2000000,
        "cost_per_1m_input": 1.25,
        "cost_per_1m_output": 5.00,
        "recommended": False,
    },
    {
        "id": "google/gemini-flash-1.5-8b",
        "name": "Gemini Flash 1.5 8B",
        "provider": "Google",
        "description": "Fast and affordable Google model",
        "context_length": 1000000,
        "cost_per_1m_input": 0.075,
        "cost_per_1m_output": 0.30,
        "recommended": True,
    },
    # Meta Models
    {
        "id": "meta-llama/llama-3.1-70b-instruct",
        "name": "Llama 3.1 70B",
        "provider": "Meta",
        "description": "Open-source model with strong performance",
        "context_length": 131072,
        "cost_per_1m_input": 0.52,
        "cost_per_1m_output": 0.75,
        "recommended": False,
    },
    {
        "id": "meta-llama/llama-3.1-8b-instruct",
        "name": "Llama 3.1 8B",
        "provider": "Meta",
        "description": "Very affordable open-source model",
        "context_length": 131072,
        "cost_per_1m_input": 0.06,
        "cost_per_1m_output": 0.06,
        "recommended": False,
    },
    # Mistral Models
    {
        "id": "mistralai/mistral-7b-instruct",
        "name": "Mistral 7B",
        "provider": "Mistral AI",
        "description": "Efficient open-source model",
        "context_length": 32768,
        "cost_per_1m_input": 0.06,
        "cost_per_1m_output": 0.06,
        "recommended": False,
    },
]


def get_model_by_id(model_id: str) -> dict[str, Any] | None:
    """Get model configuration by ID.

    Args:
        model_id: Model identifier (e.g., "openai/gpt-4o-mini")

    Returns:
        Model configuration dict or None if not found
    """
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
