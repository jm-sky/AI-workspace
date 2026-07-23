"""Shared text embedding client (OpenRouter / OpenAI-compatible)."""

import logging

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate text embeddings via OpenRouter (OpenAI-compatible API)."""

    def __init__(self, api_key: str | None = None):
        key = api_key or settings.ai.openrouter_api_key
        if not key:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        self.model = settings.ai.memory_embedding_model
        self.dimensions = settings.ai.memory_embedding_dimensions
        self.client = AsyncOpenAI(
            api_key=key,
            base_url=settings.ai.openrouter_base_url,
        )

    async def embed(self, text: str) -> list[float]:
        """Return embedding vector for a single text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text.strip(),
            dimensions=self.dimensions,
        )
        embedding = response.data[0].embedding
        if len(embedding) != self.dimensions:
            logger.warning(
                "Embedding dimension mismatch: expected %s, got %s",
                self.dimensions,
                len(embedding),
            )
        return embedding

    @staticmethod
    def vector_to_pg_literal(vector: list[float]) -> str:
        """Format vector for pgvector SQL literal."""
        return "[" + ",".join(f"{v:.8f}" for v in vector) + "]"
