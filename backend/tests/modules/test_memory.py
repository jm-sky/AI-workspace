"""Tests for memory embedding utilities."""

from app.modules.memory.repositories import MemoryRepository
from app.modules.memory.services.embedding_service import EmbeddingService


def test_vector_to_pg_literal():
    vector = [0.1, 0.2, 0.3]
    literal = EmbeddingService.vector_to_pg_literal(vector)
    assert literal == "[0.10000000,0.20000000,0.30000000]"


def test_scope_filter_sql_with_agent_and_session():
    sql = MemoryRepository._scope_filter_sql("github-workspace", "run-1")
    assert "agent_key = :agent_key" in sql
    assert "session_id = :session_id" in sql
    assert "IS NULL" not in sql


def test_scope_filter_sql_without_optional_filters():
    sql = MemoryRepository._scope_filter_sql(None, None)
    assert "scope = 'agent'" in sql
    assert "scope = 'session'" in sql
    assert "agent_key =" not in sql
    assert "session_id =" not in sql
