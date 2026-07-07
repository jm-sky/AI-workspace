"""Tests for memory embedding utilities."""

from app.modules.memory.services.embedding_service import EmbeddingService


def test_vector_to_pg_literal():
    vector = [0.1, 0.2, 0.3]
    literal = EmbeddingService.vector_to_pg_literal(vector)
    assert literal == "[0.10000000,0.20000000,0.30000000]"
