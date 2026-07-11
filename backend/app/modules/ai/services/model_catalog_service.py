"""Live OpenRouter model catalog with Redis caching and curated overlay.

The catalog is fetched from OpenRouter's public `/models` endpoint, mapped into
the internal model dict shape (the same keys `MODELS` carries), cached in Redis,
and published to `models_config._SNAPSHOT` so that the synchronous cost helpers
can price models outside the curated list.

Any failure — missing network, timeout, malformed payload — degrades to the
curated `MODELS` list, so the picker always has something to show.
"""

import json
import logging
from typing import Any

import httpx
from redis.asyncio import Redis

from app.core.config import settings
from app.modules.ai.utils.models_config import MODELS, set_catalog_snapshot

logger = logging.getLogger(__name__)

CATALOG_CACHE_KEY = "ai:model_catalog:v1"

# Slugs whose title-cased form would read wrong.
PROVIDER_LABELS: dict[str, str] = {
    "ai21": "AI21",
    "allenai": "AllenAI",
    "arcee-ai": "Arcee AI",
    "bytedance-seed": "ByteDance Seed",
    "bytedance": "ByteDance",
    "deepseek": "DeepSeek",
    "ibm-granite": "IBM Granite",
    "meta-llama": "Meta",
    "minimax": "MiniMax",
    "mistralai": "Mistral",
    "moonshotai": "Moonshot AI",
    "nousresearch": "Nous Research",
    "nvidia": "NVIDIA",
    "openai": "OpenAI",
    "openrouter": "OpenRouter",
    "rekaai": "Reka",
    "stepfun": "StepFun",
    "x-ai": "xAI",
    "z-ai": "Z.AI",
}

MAX_DESCRIPTION_LENGTH = 200

# Curated metadata (tier, recommended, hand-written description) keyed by id.
_OVERLAY: dict[str, dict[str, Any]] = {model["id"]: model for model in MODELS}


def _prettify_provider(slug: str) -> str:
    """Turn an OpenRouter author slug into a display name.

    Alias authors are prefixed with `~` (e.g. `~x-ai/grok-latest`).
    """
    slug = slug.lstrip("~")
    if slug in PROVIDER_LABELS:
        return PROVIDER_LABELS[slug]
    return slug.replace("-", " ").title()


def _strip_provider_prefix(name: str, provider: str) -> str:
    """Drop the redundant `"OpenAI: "` prefix — the card badges the provider already."""
    head, separator, tail = name.partition(": ")
    if separator and tail and head.casefold() == provider.casefold():
        return tail
    return name


def _truncate(text: str | None) -> str | None:
    if not text:
        return None
    collapsed = " ".join(text.split())
    if len(collapsed) <= MAX_DESCRIPTION_LENGTH:
        return collapsed
    return collapsed[: MAX_DESCRIPTION_LENGTH - 1].rstrip() + "…"


def _raw_price(pricing: dict[str, Any], key: str) -> float:
    """OpenRouter prices are strings in USD per single token."""
    try:
        return float(pricing.get(key) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def is_importable(raw: dict[str, Any]) -> bool:
    """Whether an OpenRouter entry belongs in the picker.

    Drops entries with no usable context window, and the `openrouter/*` router
    pseudo-models, which report a price of `-1` because it depends on whichever
    model the router picks. Left in, they sort as the cheapest option in the
    picker and would make `calculate_cost` return a negative cost.

    `:free` and `:thinking` variants are kept — they are genuinely distinct models.
    """
    model_id = raw.get("id") or ""
    if not model_id:
        return False

    pricing = raw.get("pricing") or {}
    if any(_raw_price(pricing, key) < 0 for key in ("prompt", "completion")):
        return False

    try:
        context_length = int(raw.get("context_length") or 0)
    except (TypeError, ValueError):
        return False
    return context_length > 0


def _price_per_1m(pricing: dict[str, Any], key: str) -> float:
    return _raw_price(pricing, key) * 1_000_000


def map_openrouter_model(raw: dict[str, Any]) -> dict[str, Any]:
    """Map one OpenRouter entry onto the internal model dict shape.

    The result must carry every key the curated `MODELS` dicts carry, because
    `history_service` indexes `cost_per_1m_input` / `cost_per_1m_output`
    directly on whatever `get_model_by_id` returns.
    """
    model_id: str = raw["id"]
    pricing = raw.get("pricing") or {}
    architecture = raw.get("architecture") or {}
    input_modalities = architecture.get("input_modalities") or []
    supported_parameters = raw.get("supported_parameters") or []

    curated = _OVERLAY.get(model_id, {})
    provider = curated.get("provider") or _prettify_provider(model_id.split("/")[0])
    name = curated.get("name") or _strip_provider_prefix(
        raw.get("name") or model_id, provider
    )

    return {
        "id": model_id,
        "name": name,
        "provider": provider,
        "description": curated.get("description") or _truncate(raw.get("description")),
        "context_length": int(raw.get("context_length") or 0),
        "cost_per_1m_input": _price_per_1m(pricing, "prompt"),
        "cost_per_1m_output": _price_per_1m(pricing, "completion"),
        "tier": curated.get("tier", "balanced"),
        "supports_vision": "image" in input_modalities,
        "supports_tools": "tools" in supported_parameters,
        "supports_reasoning": "reasoning" in supported_parameters,
        "recommended": curated.get("recommended", False),
    }


async def fetch_openrouter_models(timeout: float) -> list[dict[str, Any]]:
    """Fetch and map the live catalog from OpenRouter.

    The `/models` endpoint is public; the API key is sent only when configured.

    Raises:
        httpx.HTTPError: On network failure or non-2xx response
    """
    headers: dict[str, str] = {}
    if settings.ai.openrouter_api_key:
        headers["Authorization"] = f"Bearer {settings.ai.openrouter_api_key}"

    url = f"{settings.ai.openrouter_base_url.rstrip('/')}/models"
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        payload = response.json()

    return [
        map_openrouter_model(raw)
        for raw in payload.get("data", [])
        if is_importable(raw)
    ]


async def get_catalog(redis: Redis) -> list[dict[str, Any]]:
    """Return the model catalog, preferring Redis, then OpenRouter, then curated.

    Always publishes the result to the synchronous snapshot. Never raises.
    """
    use_cache = settings.ai.cache_enabled

    if use_cache:
        try:
            cached = await redis.get(CATALOG_CACHE_KEY)
            if cached:
                models = json.loads(cached)
                set_catalog_snapshot(models)
                return models
        except Exception as exc:
            logger.warning("Model catalog cache read failed: %s", exc)

    try:
        models = await fetch_openrouter_models(settings.ai.catalog_fetch_timeout)
    except Exception as exc:
        logger.warning(
            "OpenRouter catalog fetch failed, falling back to curated models: %s", exc
        )
        return MODELS

    if not models:
        logger.warning("OpenRouter returned an empty catalog, using curated models")
        return MODELS

    if use_cache:
        try:
            await redis.set(
                CATALOG_CACHE_KEY,
                json.dumps(models),
                ex=settings.ai.catalog_cache_ttl,
            )
        except Exception as exc:
            logger.warning("Model catalog cache write failed: %s", exc)

    set_catalog_snapshot(models)
    logger.info("Loaded %d models from OpenRouter", len(models))
    return models
