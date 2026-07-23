# Plan 006 — RAG basics (retrieval + chunks + ACL)

**Status:** `done`  
**Data:** 2026-07-23  
**Obszar:** backend (`rag` nowy moduł, `agent/tools`, shared embeddings) + opcjonalnie cienkie API  
**Parent:** [004 Second Brain](2026-07-23--004--second-brain-wiki.md) → todo `gate-rag-basics` (drugi wycinek)  
**Poprzedni wycinek:** [005 Memory UPDATE](2026-07-23--005--memory-update.md) ✅  
**Referencje:** MVP #12, #17; permissions-aware retrieval; audyt 2026-07-23

## Cel

Domknąć **podstawy document RAG** pod Second Brain / Faza 4:

1. wspólny **interfejs retrieval** (ACL **przed** rankingiem),
2. tabela **`document_chunks`** + ingest tekstu,
3. tool **`rag_search`** respektujący **`ragEnabled`**,
4. testy izolacji tenant/user.

Po tym planie `gate-rag-basics` = **domknięty** (UPDATE + retrieval/ACL docs). Wiki / LightRAG / Graphiti / attachments → poza zakresem.

## Stan obecny (reuse)

| Element | Gdzie | Uwaga |
|---------|-------|--------|
| Embeddings OpenRouter | `memory/services/embedding_service.py` | `text-embedding-3-small`, dims z config |
| Memory vector search + ACL | `memory/repositories.py` | wzorzec SQL: `tenant_id`+`user_id` przed `<=>` |
| Flaga `ragEnabled` | `workspace_config` cascade | **nieużywana** w agent loop / tools |
| Memory tools / UPDATE | plan 005 | bez zmian kontraktu |
| Migracje | max `061`; plan 002 rezerwuje **`062`** | ten plan → **`063`** |

**Brakuje:** moduł RAG, chunki, interfejs retrieval, `rag_search`, egzekwowanie `ragEnabled`.

## Decyzje

| # | Temat | Decyzja |
|---|--------|---------|
| 1 | Moduł | Nowy `backend/app/modules/rag/` (nie puchnąć `memory`). Memory zostaje „pamięcią życiową”. |
| 2 | Migracja | **`063_document_chunks.py`** (nie kolidować z `062` attachments). |
| 3 | ACL MVP | `tenant_id` + `user_id` w SQL **zawsze przed** rankingiem. Team-shared / OAuth-source ACL = później (wiki team, integracje). |
| 4 | Interfejs | Protocol / ABC: `embed(text)`, `search(query, acl: RetrievalAcl, *, limit, min_similarity) → list[RetrievalHit]`. Implementacja Postgres: `PgChunkRetriever`. Memory **nie** migrujemy w tym PR na ten interfejs (opcjonalny follow-up) — tylko **wydzielamy** `EmbeddingService` do wspólnego miejsca używanego przez memory + rag. |
| 5 | Embedding shared | Przenieść `EmbeddingService` → `app/modules/rag/services/embedding_service.py` (lub `app/common/embeddings.py`); memory importuje stamtąd. Zero zmiany zachowania. |
| 6 | Chunking | Prosty splitter znakowy: `chunk_size=1200`, `overlap=150` (config). Bez LangChain. Chunki puste / whitespace-only → skip. |
| 7 | Ingest źródła MVP | Tylko **tekst** przez API (`source_type=paste`). Bez uploadu plików (to plan 002) i bez wiki (004). |
| 8 | Model dokumentów | `rag_documents` (metadane źródła) + `document_chunks` (tekst + embedding). Delete dokumentu = cascade chunków. |
| 9 | Tool | `rag_search(query, limit?)` — zwraca fragmenty + `document_id` / tytuł / score. **Nie** w `CORE_TOOL_NAMES` na start (katalog profile `memory`+`rag` albo osobno `rag`); gdy `ragEnabled=false` → pusty wynik + message. |
| 10 | Injection | **Brak** auto-injection RAG do system promptu w tym wycinku (agentic RAG przez tool). Memory injection bez zmian. |
| 11 | `ragEnabled` | Resolver już jest. Agent przy budowie registry / execute tool czyta effective config; tool no-op gdy false. |
| 12 | Frontend | **Poza MVP tego planu** (API wystarczy do weryfikacji + tool w czacie). Opcjonalny follow-up: strona Knowledge. |
| 13 | Reranker / RAGAS | Poza zakresem (otwarte punkty MVP). |
| 14 | LightRAG | Poza zakresem (spike po gate). Chunki u nas = fallback no-go LightRAG. |

## Schemat DB

### `rag_documents`

| Kolumna | Typ | Uwaga |
|---------|-----|-------|
| `id` | `String(36)` PK | `generate_id()` |
| `tenant_id` | `String(36)` | ACL |
| `user_id` | `String(36)` | ACL |
| `title` | `Text` | wyświetlana etykieta |
| `source_type` | `String(40)` | MVP: `paste` (później: `attachment`, `wiki`, …) |
| `source_ref` | `String(200)` nullable | id zewnętrzne (attachment/wiki) — null dla paste |
| `metadata` | `JSONB` nullable | |
| `created_at` / `updated_at` | `DateTime(tz)` | |

Indeks: `(tenant_id, user_id, created_at DESC)`.

### `document_chunks`

| Kolumna | Typ | Uwaga |
|---------|-----|-------|
| `id` | `String(36)` PK | |
| `document_id` | FK → `rag_documents` ON DELETE CASCADE | |
| `tenant_id` / `user_id` | denormalizacja pod ACL w search | |
| `chunk_index` | `Integer` | kolejność w dokumencie |
| `content` | `Text` | |
| `token_estimate` | `Integer` nullable | opcjonalnie `len//4` |
| `embedding` | `vector(N)` | N = `AI_MEMORY_EMBEDDING_DIMENSIONS` (ten sam model co memory) |
| `created_at` | `DateTime(tz)` | |

Indeksy: `(tenant_id, user_id)`, `(document_id, chunk_index)`, HNSW `vector_cosine_ops` na `embedding`.

## Architektura

```
POST /rag/documents { title, content }  →  chunk + embed + store
GET  /rag/documents                     →  list (ACL)
DELETE /rag/documents/{id}              →  cascade

Agent: rag_search(query)
         │
         ▼
   RagService.search  ──► PgChunkRetriever
         │                     │
         │                     ├─ WHERE tenant_id AND user_id
         │                     └─ ORDER BY embedding <=> query
         ▼
   { chunks: [{ content, score, documentId, title, chunkIndex }] }

EmbeddingService (shared) ← memory create/update + rag ingest/search
```

### Interfejs (szkic)

```python
@dataclass(frozen=True)
class RetrievalAcl:
    tenant_id: str
    user_id: str

@dataclass(frozen=True)
class RetrievalHit:
    id: str
    content: str
    score: float
    document_id: str
    metadata: dict[str, Any]

class ChunkRetriever(Protocol):
    async def search(
        self,
        *,
        query_embedding: list[float],
        acl: RetrievalAcl,
        limit: int,
        min_similarity: float,
    ) -> list[RetrievalHit]: ...
```

### API (minimalne)

| Method | Path | Opis |
|--------|------|------|
| `POST` | `/rag/documents` | `{ title, content }` → document + chunks |
| `GET` | `/rag/documents` | lista dokumentów usera (bez embeddingów) |
| `GET` | `/rag/documents/{id}` | meta + lista chunków (content, bez vector) |
| `DELETE` | `/rag/documents/{id}` | 204 / 404 ACL |
| `POST` | `/rag/search` | `{ query, limit? }` — to samo co tool (wygodne do debug) |

Limity: `content` max np. **100_000** znaków na ingest; max chunków per doc np. **200** (twardy cap).

### Agent

- Profil: dodać `"rag"` do `github-workspace` (i `jira-360` jeśli memory jest).
- Rejestracja `RagSearchTool` gdy `"rag" in profile`.
- **Nie** core tool (żeby nie puchnąć zawsze-on listy); discovery przez tool_search gdy włączone, albo pełny katalog gdy poniżej threshold.
- Prompt GitHub: jedna linia — `rag_search` do wiedzy ze źródeł użytkownika (gdy RAG włączony).

### Config

Reuse `settings.ai.memory_embedding_*` + opcjonalnie:

| Key | Default | Opis |
|-----|---------|------|
| `AI_RAG_CHUNK_SIZE` | 1200 | znaki |
| `AI_RAG_CHUNK_OVERLAP` | 150 | znaki |
| `AI_RAG_SIMILARITY_THRESHOLD` | jak memory / 0.5 | min score |
| `AI_RAG_SEARCH_LIMIT` | 8 | default tool/API |

`WORKSPACE_DEFAULT_RAG_ENABLED` — bez zmiany semantyki cascade; upewnić się w `.env.example` że flaga jest opisana.

## Testy

| Case | Oczekiwanie |
|------|-------------|
| ACL search | User B / inny tenant → 0 hitów na chunki usera A |
| Ingest | 1 doc → ≥1 chunk; embedding nie-null |
| Delete | dokument + chunki znikają |
| `ragEnabled=false` | tool zwraca pustą listę + message; brak wyjątku |
| Chunker | overlap / puste segmenty; cap 200 chunków |
| Shared embed | memory + rag używają tego samego serwisu (import path) |
| Migracja | upgrade/downgrade `063` (smoke w CI jeśli wzorzec istnieje) |

Bez żywego OpenRouter: mock `EmbeddingService.embed`.

## Todos

| ID | Treść |
|----|--------|
| shared-embed | Przenieś `EmbeddingService` do wspólnego miejsca; popraw importy memory |
| migration-063 | `rag_documents` + `document_chunks` + HNSW |
| rag-module | repo, chunker, `RagService` (ingest/search/delete), schemas, router |
| retriever-iface | `RetrievalAcl` / `RetrievalHit` / `PgChunkRetriever` |
| agent-tool | `rag_search` + profil + prompt; gate na `ragEnabled` |
| tests | ACL, ingest, tool disabled, chunker |
| docs-touch | 004 `gate-rag-basics` → closed; 006 → done; krótka wzmianka MVP Faza 4 |

## Poza zakresem

- UI Knowledge browser  
- Attachments → chunki (plan 002)  
- Wiki pages → chunki (004 / 4.5)  
- Auto-injection RAG do promptu  
- Reranker, hybrid BM25, RAGAS  
- LightRAG / Graphiti  
- Refaktor `MemoryRepository.search_similar` na `ChunkRetriever`  
- Team-shared documents  

## Ryzyka

| Ryzyko | Mitygacja |
|--------|-----------|
| Koszt embed przy dużym paste | Cap znaków + max chunków; jasny 422 |
| Duplikacja embed code | Jedna klasa shared od razu |
| Kolizja migracji 062 | Twardo **063** |
| Agent woła RAG gdy wyłączony | Tool no-op + opis toola „when RAG enabled” |
| Mylenie memory vs RAG | Osobny moduł + osobne toole; prompt: fakty→memory, źródła→rag |

## Otwarte punkty (do potwierdzenia przed kodem)

1. **Domyślne `ragEnabled`:** zostawić cascade / env jak dziś, czy w dev ustawić default `true` żeby tool był widoczny od razu? Propozycja: **bez zmiany defaultu**; w `.env.example` skomentować jak włączyć.
2. **Profil tooli:** `rag` osobno w `AGENT_TOOL_PROFILES` vs zawsze razem z `memory`? Propozycja: **osobny** `"rag"` w profilu `github-workspace`.
3. **UI:** potwierdzenie — **brak UI** w tym PR (tylko API + tool).

## Kryteria done (gate-rag-basics)

- [x] Migracja 063 + ingest/search/delete z ACL  
- [x] Interfejs retrieval + Pg implementacja  
- [x] `rag_search` + respektowanie `ragEnabled`  
- [x] Shared `EmbeddingService`  
- [x] Testy ACL / disabled / chunker zielone  
- [x] Plan 004: `gate-rag-basics` oznaczony jako domknięty (UPDATE + RAG basics)  
