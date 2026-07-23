"""Character-based text chunker for RAG ingest."""


def split_text(
    text: str,
    *,
    chunk_size: int = 1200,
    overlap: int = 150,
    max_chunks: int = 200,
) -> list[str]:
    """Split text into overlapping character windows.

    Skips empty / whitespace-only segments. Hard-caps at ``max_chunks``.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be < chunk_size")
    if max_chunks < 1:
        raise ValueError("max_chunks must be >= 1")

    cleaned = text.strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    length = len(cleaned)
    step = chunk_size - overlap

    while start < length and len(chunks) < max_chunks:
        end = min(start + chunk_size, length)
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        start += step

    return chunks
