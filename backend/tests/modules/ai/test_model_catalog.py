"""Tests for the live OpenRouter model catalog service."""

import json
from typing import Any

import pytest

from app.modules.ai.services import model_catalog_service as catalog
from app.modules.ai.utils.models_config import (
    MODELS,
    calculate_cost,
    clear_catalog_snapshot,
    get_model_by_id,
    set_catalog_snapshot,
)

# Keys every curated model carries. `history_service` indexes the cost keys
# directly on whatever `get_model_by_id` returns, so the mapper must emit them.
CURATED_KEYS = set(MODELS[0].keys())


@pytest.fixture(autouse=True)
def _reset_snapshot():
    """The catalog snapshot is module-global; never let it leak between tests."""
    clear_catalog_snapshot()
    yield
    clear_catalog_snapshot()


def _raw(**overrides: Any) -> dict[str, Any]:
    """A raw OpenRouter entry, shaped like the real /models payload."""
    raw = {
        "id": "mistralai/mistral-medium-3-5",
        "name": "Mistral: Mistral Medium 3.5",
        "description": "  A dense   128B model.  ",
        "context_length": 262144,
        "pricing": {"prompt": "0.0000015", "completion": "0.0000075"},
        "architecture": {"input_modalities": ["text", "image"]},
        "supported_parameters": ["tools", "reasoning", "temperature"],
    }
    raw.update(overrides)
    return raw


class TestIsImportable:
    def test_keeps_ordinary_model(self):
        assert catalog.is_importable(_raw()) is True

    def test_keeps_free_and_thinking_variants(self):
        assert catalog.is_importable(_raw(id="google/gemma-4-31b:free")) is True
        assert catalog.is_importable(_raw(id="moonshotai/kimi-k2:thinking")) is True

    def test_drops_negative_priced_routers(self):
        """openrouter/auto & friends price at -1; they'd sort as the cheapest model."""
        router = _raw(id="openrouter/auto", pricing={"prompt": "-1", "completion": "-1"})
        assert catalog.is_importable(router) is False

    def test_drops_zero_context(self):
        assert catalog.is_importable(_raw(context_length=0)) is False
        assert catalog.is_importable(_raw(context_length=None)) is False

    def test_drops_missing_id(self):
        assert catalog.is_importable(_raw(id="")) is False


class TestMapOpenrouterModel:
    def test_pricing_strings_become_per_1m_floats(self):
        mapped = catalog.map_openrouter_model(_raw())
        assert mapped["cost_per_1m_input"] == pytest.approx(1.5)
        assert mapped["cost_per_1m_output"] == pytest.approx(7.5)

    def test_free_model_is_zero_not_missing(self):
        mapped = catalog.map_openrouter_model(_raw(pricing={"prompt": "0", "completion": "0"}))
        assert mapped["cost_per_1m_input"] == 0.0
        assert mapped["cost_per_1m_output"] == 0.0

    def test_capabilities_derived_from_architecture_and_parameters(self):
        mapped = catalog.map_openrouter_model(_raw())
        assert mapped["supports_vision"] is True
        assert mapped["supports_tools"] is True
        assert mapped["supports_reasoning"] is True

        text_only = catalog.map_openrouter_model(
            _raw(architecture={"input_modalities": ["text"]}, supported_parameters=["temperature"])
        )
        assert text_only["supports_vision"] is False
        assert text_only["supports_tools"] is False
        assert text_only["supports_reasoning"] is False

    def test_provider_prettified_and_name_deprefixed(self):
        mapped = catalog.map_openrouter_model(_raw())
        assert mapped["provider"] == "Mistral"
        assert mapped["name"] == "Mistral Medium 3.5"

    def test_alias_author_prefix_stripped(self):
        mapped = catalog.map_openrouter_model(
            _raw(id="~x-ai/grok-latest", name="xAI: Grok Latest")
        )
        assert mapped["provider"] == "xAI"
        assert mapped["name"] == "Grok Latest"

    def test_name_without_provider_prefix_is_untouched(self):
        mapped = catalog.map_openrouter_model(_raw(name="Codestral: Mamba"))
        assert mapped["name"] == "Codestral: Mamba"

    def test_description_collapsed_and_truncated(self):
        mapped = catalog.map_openrouter_model(_raw())
        assert mapped["description"] == "A dense 128B model."

        long = catalog.map_openrouter_model(_raw(description="x" * 500))
        assert len(long["description"]) == catalog.MAX_DESCRIPTION_LENGTH
        assert long["description"].endswith("…")

    def test_non_curated_model_gets_defaults(self):
        mapped = catalog.map_openrouter_model(_raw())
        assert mapped["tier"] == "balanced"
        assert mapped["recommended"] is False

    def test_curated_overlay_wins_over_openrouter(self):
        """Curated tier/recommended/name/description survive the live fetch."""
        mapped = catalog.map_openrouter_model(
            _raw(
                id="openai/gpt-4o-mini",
                name="OpenAI: GPT-4o-mini",
                description="Some upstream blurb",
            )
        )
        assert mapped["tier"] == "fast"
        assert mapped["recommended"] is True
        assert mapped["name"] == "GPT-4o Mini"
        assert mapped["description"] == "Fast and affordable model, great for most tasks"
        # ...but live pricing/context still come from OpenRouter.
        assert mapped["cost_per_1m_input"] == pytest.approx(1.5)

    def test_emits_every_curated_key(self):
        """Guards history_service.py, which does model_config["cost_per_1m_input"]."""
        mapped = catalog.map_openrouter_model(_raw())
        assert CURATED_KEYS - set(mapped.keys()) == set()


class FakeRedis:
    def __init__(self, initial: str | None = None):
        self.store: dict[str, str] = {}
        if initial is not None:
            self.store[catalog.CATALOG_CACHE_KEY] = initial
        self.set_calls: list[tuple[str, int]] = []

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.store[key] = value
        self.set_calls.append((key, ex))


class TestGetCatalog:
    @pytest.mark.asyncio
    async def test_falls_back_to_curated_when_fetch_fails(self, monkeypatch):
        async def boom(_timeout):
            raise TimeoutError("openrouter unreachable")

        monkeypatch.setattr(catalog, "fetch_openrouter_models", boom)

        models = await catalog.get_catalog(FakeRedis())

        assert models is MODELS
        # A failed fetch must not poison the snapshot with a partial catalog.
        assert get_model_by_id("mistralai/mistral-medium-3-5") is None

    @pytest.mark.asyncio
    async def test_falls_back_when_openrouter_returns_empty(self, monkeypatch):
        async def empty(_timeout):
            return []

        monkeypatch.setattr(catalog, "fetch_openrouter_models", empty)
        assert await catalog.get_catalog(FakeRedis()) is MODELS

    @pytest.mark.asyncio
    async def test_cache_hit_skips_fetch(self, monkeypatch):
        async def boom(_timeout):
            raise AssertionError("fetch must not be called on a cache hit")

        monkeypatch.setattr(catalog, "fetch_openrouter_models", boom)
        cached = [catalog.map_openrouter_model(_raw())]

        models = await catalog.get_catalog(FakeRedis(initial=json.dumps(cached)))

        assert models == cached

    @pytest.mark.asyncio
    async def test_fetch_populates_cache_and_snapshot(self, monkeypatch):
        mapped = [catalog.map_openrouter_model(_raw())]

        async def ok(_timeout):
            return mapped

        monkeypatch.setattr(catalog, "fetch_openrouter_models", ok)
        redis = FakeRedis()

        models = await catalog.get_catalog(redis)

        assert models == mapped
        assert json.loads(redis.store[catalog.CATALOG_CACHE_KEY]) == mapped
        assert redis.set_calls[0][1] > 0  # a TTL was set
        assert get_model_by_id("mistralai/mistral-medium-3-5") is not None

    @pytest.mark.asyncio
    async def test_survives_broken_redis(self, monkeypatch):
        class BrokenRedis:
            async def get(self, key):
                raise ConnectionError("redis down")

            async def set(self, key, value, ex=None):
                raise ConnectionError("redis down")

        async def ok(_timeout):
            return [catalog.map_openrouter_model(_raw())]

        monkeypatch.setattr(catalog, "fetch_openrouter_models", ok)

        models = await catalog.get_catalog(BrokenRedis())
        assert len(models) == 1


class TestSnapshotBackedPricing:
    def test_snapshot_prices_models_outside_the_curated_list(self):
        live = catalog.map_openrouter_model(_raw())
        assert get_model_by_id(live["id"]) is None

        set_catalog_snapshot([live])

        assert get_model_by_id(live["id"])["name"] == "Mistral Medium 3.5"
        # 1000 in @ $1.50/1M + 500 out @ $7.50/1M
        assert calculate_cost(live["id"], 1000, 500) == pytest.approx(0.00525)

    def test_snapshot_overrides_curated_pricing(self):
        repriced = catalog.map_openrouter_model(
            _raw(id="openai/gpt-4o-mini", pricing={"prompt": "0.000001", "completion": "0.000002"})
        )
        set_catalog_snapshot([repriced])

        assert calculate_cost("openai/gpt-4o-mini", 1_000_000, 0) == pytest.approx(1.0)

    def test_clearing_restores_curated_pricing(self):
        set_catalog_snapshot([catalog.map_openrouter_model(_raw(id="openai/gpt-4o-mini"))])
        clear_catalog_snapshot()

        # Back to the curated $0.15/$0.60.
        assert calculate_cost("openai/gpt-4o-mini", 1000, 500) == pytest.approx(0.00045)

    def test_empty_snapshot_is_transparent(self):
        assert get_model_by_id("openai/gpt-4o-mini")["name"] == "GPT-4o Mini"
        assert get_model_by_id("nonexistent/model") is None
