"""Migration: RAG documents + chunks with pgvector.

Usage:
    python migrations/063_document_chunks.py upgrade
    python migrations/063_document_chunks.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine

EMBEDDING_DIMENSIONS = 1536


async def table_exists(conn, table_name: str) -> bool:
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    print("Applying document chunks (RAG) migration...")

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("✓ pgvector extension enabled")

        if not await table_exists(conn, "rag_documents"):
            await conn.execute(text("""
                    CREATE TABLE rag_documents (
                        id VARCHAR(36) PRIMARY KEY,
                        tenant_id VARCHAR(36) NOT NULL
                            REFERENCES tenants(id) ON DELETE CASCADE,
                        user_id VARCHAR(36) NOT NULL
                            REFERENCES users(id) ON DELETE CASCADE,
                        title TEXT NOT NULL,
                        source_type VARCHAR(40) NOT NULL DEFAULT 'paste',
                        source_ref VARCHAR(200),
                        metadata JSONB,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT chk_rag_source_type CHECK (
                            source_type IN ('paste', 'attachment', 'wiki')
                        )
                    )
                """))
            await conn.execute(text("""
                    CREATE INDEX idx_rag_documents_tenant_user
                    ON rag_documents(tenant_id, user_id, created_at DESC)
                    """))
            print("✓ Created rag_documents table")
        else:
            print("✓ rag_documents table already exists")

        if not await table_exists(conn, "document_chunks"):
            await conn.execute(text(f"""
                    CREATE TABLE document_chunks (
                        id VARCHAR(36) PRIMARY KEY,
                        document_id VARCHAR(36) NOT NULL
                            REFERENCES rag_documents(id) ON DELETE CASCADE,
                        tenant_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        token_estimate INTEGER,
                        embedding vector({EMBEDDING_DIMENSIONS}),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT uq_document_chunks_doc_index
                            UNIQUE (document_id, chunk_index)
                    )
                """))
            await conn.execute(text("""
                    CREATE INDEX idx_document_chunks_tenant_user
                    ON document_chunks(tenant_id, user_id)
                    """))
            await conn.execute(text("""
                    CREATE INDEX idx_document_chunks_document
                    ON document_chunks(document_id, chunk_index)
                    """))
            await conn.execute(text("""
                    CREATE INDEX idx_document_chunks_embedding
                    ON document_chunks
                    USING hnsw (embedding vector_cosine_ops)
                    """))
            print("✓ Created document_chunks table")
        else:
            print("✓ document_chunks table already exists")

    print("Document chunks (RAG) migration complete.")


async def downgrade() -> None:
    print("Reverting document chunks (RAG) migration...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS document_chunks CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS rag_documents CASCADE;"))
    print("✓ Dropped document_chunks and rag_documents")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "upgrade"
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
