"""Tests for AI utils (encryption and models_config)."""

import pytest
from cryptography.fernet import Fernet

from app.modules.ai.utils.encryption import decrypt_token, encrypt_token
from app.modules.ai.utils.models_config import (
    MODELS,
    calculate_cost,
    get_model_by_id,
    get_recommended_models,
)


class TestEncryption:
    """Tests for token encryption utilities."""

    def test_encrypt_decrypt_token(self, monkeypatch):
        """Test token encryption and decryption."""
        # Generate test key
        test_key = Fernet.generate_key().decode()
        monkeypatch.setattr(
            "app.modules.ai.utils.encryption.settings.ai.token_encryption_key", test_key
        )

        # Test token
        original_token = "sk-or-v1-test-token-123"

        # Encrypt
        encrypted = encrypt_token(original_token)
        assert encrypted != original_token
        assert len(encrypted) > 0

        # Decrypt
        decrypted = decrypt_token(encrypted)
        assert decrypted == original_token

    def test_encrypt_different_tokens_produce_different_results(self, monkeypatch):
        """Test that different tokens produce different encrypted values."""
        test_key = Fernet.generate_key().decode()
        monkeypatch.setattr(
            "app.modules.ai.utils.encryption.settings.ai.token_encryption_key", test_key
        )

        token1 = "sk-or-v1-token1"
        token2 = "sk-or-v1-token2"

        encrypted1 = encrypt_token(token1)
        encrypted2 = encrypt_token(token2)

        assert encrypted1 != encrypted2


class TestModelsConfig:
    """Tests for models configuration."""

    def test_models_list_not_empty(self):
        """Test that MODELS list is not empty."""
        assert len(MODELS) > 0
        assert len(MODELS) == 10  # Should have 10 configured models

    def test_all_models_have_required_fields(self):
        """Test that all models have required fields."""
        required_fields = [
            "id",
            "name",
            "provider",
            "context_length",
            "cost_per_1m_input",
            "cost_per_1m_output",
        ]

        for model in MODELS:
            for field in required_fields:
                assert field in model, f"Model {model.get('id')} missing field: {field}"

    def test_get_model_by_id_existing(self):
        """Test getting existing model by ID."""
        # Use first model from list
        model_id = MODELS[0]["id"]
        model = get_model_by_id(model_id)

        assert model is not None
        assert model["id"] == model_id

    def test_get_model_by_id_nonexistent(self):
        """Test getting non-existent model."""
        model = get_model_by_id("nonexistent/model")
        assert model is None

    def test_get_recommended_models(self):
        """Test getting recommended models."""
        recommended = get_recommended_models()

        assert len(recommended) > 0
        for model in recommended:
            assert model.get("recommended") is True

    def test_calculate_cost_basic(self):
        """Test cost calculation with known model."""
        model_id = "openai/gpt-4o-mini"
        prompt_tokens = 1000
        completion_tokens = 500

        cost = calculate_cost(model_id, prompt_tokens, completion_tokens)

        # GPT-4o-mini: $0.15/$0.60 per 1M tokens
        # Expected: (1000/1M * 0.15) + (500/1M * 0.60) = 0.00015 + 0.0003 = 0.00045
        assert cost == pytest.approx(0.00045, rel=1e-6)

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        model_id = "openai/gpt-4o-mini"
        cost = calculate_cost(model_id, 0, 0)

        assert cost == 0.0

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation with unknown model."""
        cost = calculate_cost("unknown/model", 1000, 500)
        assert cost == 0.0

    def test_model_ids_are_unique(self):
        """Test that all model IDs are unique."""
        model_ids = [model["id"] for model in MODELS]
        assert len(model_ids) == len(set(model_ids))

    def test_costs_are_positive(self):
        """Test that all costs are positive numbers."""
        for model in MODELS:
            assert model["cost_per_1m_input"] > 0
            assert model["cost_per_1m_output"] > 0

    def test_context_lengths_are_positive(self):
        """Test that all context lengths are positive."""
        for model in MODELS:
            assert model["context_length"] > 0
