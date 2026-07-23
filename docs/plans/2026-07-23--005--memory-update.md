# Plan 005 — Memory UPDATE (lifecycle)

**Status:** `done`  
**Data:** 2026-07-23  
**Obszar:** backend (`memory`, `agent/tools`) + frontend (`workspace` memory browser)  
**Parent:** [004 Second Brain](2026-07-23--004--second-brain-wiki.md) → todo `gate-rag-basics` (pierwszy wycinek)  
**Referencje:** MVP dec. #12 (pamięć), research `2026-07-04--002` (ADD/UPDATE/DELETE), audyt 2026-07-23

## Cel

Domknąć brakujący **UPDATE** w cyklu życia flat `memory_entries`: poprawa treści (z re-embeddingiem), opcjonalna zmiana scope/metadata — z ACL jak przy delete, tool dla agenta i edycja w UI.

**Po tym planie `gate-rag-basics` nadal otwarty** (brak document RAG / wspólnego retrieval). Ten dokument świadomie wycina tylko UPDATE, żeby zrobić go dobrze przed chunkami.

## Stan obecny (reuse)

| Element | Gdzie | Uwaga |
|---------|-------|--------|
| Model + ACL get/delete | `memory/repositories.py` `get_by_id` / `delete` | filtr `tenant_id` + `user_id` |
| Create + embed | `MemoryService.create_entry` | OpenRouter → raw SQL insert |
| Search / injection | `search` / `build_injection_context` | bez zmian |
| API | `GET/POST /memory`, `POST /memory/search`, `DELETE /memory/{id}` | brak PATCH |
| Toole | `memory_search`, `memory_save` | w `CORE_TOOL_NAMES` |
| UI | `WorkspaceMemoryPage` + `useMemoryBrowser` | add + delete, brak edit |
| Migracja | `059_memory_entries.py` | kolumna `updated_at` już jest |

**Brakuje:** `repo.update`, `service.update_entry`, `PATCH`, tool `memory_update`, edit UI, testy ACL/re-embed.

**Migracja DB:** niepotrzebna (schemat bez zmian).

## Decyzje (ustalone w tym planie)

| # | Temat | Decyzja |
|---|--------|---------|
| 1 | HTTP | `PATCH /memory/{entry_id}` — partial update; 404 gdy brak lub cudzy wpis (jak delete) |
| 2 | Pola mutowalne | `content`, `scope`, `metadata` (partial). **Niemutowalne:** `id`, `tenant_id`, `user_id`, `source`, `created_at` |
| 3 | Scope | Zmiana dozwolona. Przy `scope=agent` ustaw `agent_key` z kontekstu requestu/tool (bieżący agent); przy `scope=session` — `session_id` z kontekstu (API: opcjonalne `sessionId` w body; tool: bieżąca sesja). Przy `scope=user` wyczyść `agent_key` i `session_id`. |
| 4 | Re-embed | Tylko gdy `content` jest w body **i** różni się od aktualnego (po `strip`). Samo `scope`/`metadata` → update SQL bez wywołania embeddera. |
| 5 | Pusty PATCH | Odrzuć `422` gdy body nie zawiera żadnego z: `content`, `scope`, `metadata`. |
| 6 | Content | Jak create: `min_length=1`, `max_length=8000` po trim. |
| 7 | Tool | Osobny `memory_update` (nie rozszerzać `memory_save`). Parametry: `id` (wymagane), `content` i/lub `scope`. Bez `metadata` w toolu MVP (prostszy kontrakt dla LLM). |
| 8 | CORE tools | Dodać `memory_update` do `CORE_TOOL_NAMES` + rejestracji przy profilu `memory`. |
| 9 | Prompt | Jedna linia w `github_workspace.py`: popraw/aktualizuj istniejący fakt przez `memory_update` (po `memory_search`), nie duplikuj `memory_save`. |
| 10 | UI | Inline edit na liście (ikona Edit → textarea + Save/Cancel). Bez nowego dialogu/modala. Scope w edycji: Select jak przy add. |
| 11 | Source | Zostaje oryginalny (`user` / `agent` / …) — UPDATE nie zmienia provenance create. |
| 12 | Facade Graphiti | Poza zakresem. `update_entry` na `MemoryService` = miejsce pod przyszły backend. |

## Architektura

```
PATCH /memory/{id}  ──► MemoryService.update_entry
                              │
                              ├─ get_by_id (ACL) → 404
                              ├─ jeśli content zmieniony → EmbeddingService.embed
                              └─ MemoryRepository.update (raw SQL / ORM + embedding)

Agent: memory_search → id → memory_update(id, content|scope)
UI:    Edit → PATCH → odśwież wiersz lokalnie
```

### Schema (Pydantic)

```python
class MemoryEntryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=8000)
    scope: MemoryScopeLiteral | None = None
    agentKey: str | None = Field(default=None, alias="agent_key")  # tylko gdy scope=agent z API
    sessionId: str | None = Field(default=None, alias="session_id")  # gdy scope=session z API
    metadata: dict[str, Any] | None = None
    # walidator: ≥1 pole spośród content|scope|metadata
```

Response: istniejący `MemoryEntryResponse` (ze świeżym `updatedAt`).

### Repository `update`

- Wejście: `entry_id`, `tenant_id`, `user_id`, opcjonalne pola + opcjonalny `embedding`.
- `get_by_id` → jeśli None: return None.
- Update: `content` / `scope` / `agent_key` / `session_id` / `entry_metadata` / `updated_at=now()`.
- Embedding: raw SQL `UPDATE … SET embedding = CAST(:embedding AS vector)` gdy przekazany; inaczej nie tykać kolumny embedding.
- Commit w **service** (spójnie z create/delete).

Uwaga: dziś create używa raw SQL (embedding), delete ORM. Update może mieszać: ORM dla pól skalarnych + raw SQL dla embedding, albo jeden raw `UPDATE` — preferuj **jeden raw UPDATE** jak create (mniej rozjazdu ORM/embedding).

### Service `update_entry`

1. `get_by_id` → None → return None (router 404).
2. Zastosuj reguły scope (agent_key / session_id).
3. Jeśli content zmieniony → embed; else embedding=None.
4. `repo.update(…)` → commit → `_to_response`.

### Tool `MemoryUpdateTool`

```json
{
  "id": "string (required)",
  "content": "string (optional)",
  "scope": "user|agent|session (optional)"
}
```

- Wymagane ≥1 z `content`/`scope`.
- ACL przez service; brak wpisu → `{"error": "Memory not found"}` (nie leak cross-tenant).
- `memory_enabled=false` → jak save: `updated: false`.

### Frontend

| Plik | Zmiana |
|------|--------|
| `memoryApiService.ts` | `updateMemory(id, body)` → PATCH |
| `types/memory.ts` | `IMemoryEntryUpdate` |
| `useMemoryBrowser.ts` | `editMemory(id, …)` — patch lokalnej listy / semanticResults |
| `WorkspaceMemoryPage.vue` | stan `editingId`, inline form |
| `i18n` en + pl | edit / save / cancel / updated / updateFailed |

Wzorce UI: istniejące Button ghost + ikony lucide (`Pencil`, `Check`, `X`); tokeny Fazy 1.5 (`border-hairline`, `bg-surface-raised`).

## Testy

| Case | Oczekiwanie |
|------|-------------|
| Update content (unit/integration z mock embed) | `updated_at` rośnie; embed wywołany 1×; search po nowej treści trafia |
| Update tylko scope | embed **nie** wywołany; `agent_key`/`session_id` zgodne z regułami |
| Cross-user / cross-tenant PATCH | 404 |
| Pusty body | 422 |
| Tool bez id / bez pól | error w JSON tool result |
| `memory_enabled=false` | tool nie mutuje |

Minimalny zestaw do commita: rozszerzyć `tests/modules/test_memory.py` o logikę scope/re-embed (pure unit gdzie da się bez DB) + testy service z mockowanym `EmbeddingService` / repo jeśli wzorzec w repo na to pozwala. Preferuj testy bez żywego OpenRouter.

## Todos

| ID | Treść |
|----|--------|
| be-repo-service | `MemoryRepository.update` + `MemoryService.update_entry` + schema `MemoryEntryUpdate` |
| be-api | `PATCH /memory/{entry_id}` |
| be-tool | `MemoryUpdateTool` + rejestracja + `CORE_TOOL_NAMES` + prompt hint |
| fe-api-ui | API client, composable, inline edit, i18n |
| tests | ACL 404, re-embed vs no-re-embed, walidacja body, tool errors |
| docs-touch | W `004` przy todo `gate-rag-basics` odnotować: UPDATE ✅ / RAG chunks nadal open; status tego planu → `done` |

## Poza zakresem (świadomie)

- Tabela chunków / `rag_search` / interfejs VectorStore  
- Spike LightRAG / Graphiti  
- Merge / decay / konsolidacja pamięci  
- Zmiana `source` przy update  
- Bulk update  
- Soft-delete / deprecate  

## Ryzyka

| Ryzyko | Mitygacja |
|--------|-----------|
| Agent zapisuje duplikat zamiast update | Prompt + tool description: najpierw search, potem update po `id` |
| Re-embed koszt / latency | Tylko przy zmianie content |
| API podaje cudzy `agentKey` | Service: dla toola zawsze bieżący `agent_key`; dla API przy `scope=agent` akceptuj `agentKey` z body **albo** wymuś z kontekstu workspace — **MVP: body `agentKey` opcjonalne, fallback do query/context brak → 422 jeśli scope=agent bez klucza** |
| Rozjazd ORM vs embedding | Jeden raw UPDATE w repo |

## Otwarte punkty (do potwierdzenia przed kodem)

1. **API `scope=agent` bez `agentKey`:** 422 vs domyślny klucz z nagłówka/sesji workspace? Propozycja: **422** (jawność). Tool zawsze zna `agent_key`.
2. **Czy UI pozwala zmienić scope przy edycji?** Propozycja: **tak** (Select).
3. **Czy `metadata` w PATCH API w tym PR?** Propozycja: **tak w schemacie**, UI na razie nie edytuje metadata (tylko content + scope).

## Kryteria done

- [x] PATCH działa z ACL 404  
- [x] Re-embed tylko przy zmianie content  
- [x] Agent ma `memory_update` w core tools  
- [x] UI: edycja content (+ scope) end-to-end  
- [x] Testy z tabeli powyżej zielone  
- [x] Plan 005 → `done`; wzmianka w 004 / opcjonalnie MVP otwarte punkty  
