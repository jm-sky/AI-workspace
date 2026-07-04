# Research → wnioski dla planu (synteza)

> Konsolidacja wniosków z researchu w jednym miejscu — do wykorzystania później przy implementacji.
> Źródła szczegółowe: `01-enterprise-comparables.md`, `02-ai-techniques.md`, `03-agent-frameworks.md`.
> Decyzje MVP: `../MVP.md`.

## 1. Co research potwierdził (zielone światło dla decyzji)

- **MCP jako standard integracji** (Dust, Copilot Studio, Cohere, ServiceNow, PydanticAI/OpenAI/ADK) → dec. 5 (własne serwery MCP) + przenośność narzędzi między frameworkami.
- **No-code edytor agentów** (Agentspace, Copilot Studio, Dust, Writer AI HQ) → dec. 10–11 (edytor agentów).
- **SDK dostawcy na prosty single-agent loop, framework grafowy na multi-agent** → dec. 2 (tool runner teraz, LangGraph później). Kryteria przełączenia: `03-agent-frameworks.md`.
- **Governance/audyt na poziomie tenantа** (Copilot Studio, ServiceNow Control Tower) → dec. 8 (kaskada z sufitami) + dec. 13 (audyt).
- **Agentic RAG „za darmo" z pętli agenta** → dec. 12 (auto-injection + narzędzie retrieval na żądanie).
- **Selektywna pamięć + kompresja** (context rot) → dec. 12; unikać „wrzuć wszystko".

## 2. Nowe wymagania / do wpięcia w plan

| Wniosek | Skąd | Gdzie w planie |
|---|---|---|
| **Permissions-aware retrieval** (filtr uprawnień przed rankingiem) | Glean; per-user OAuth | Faza 4 (RAG) — twardy wymóg, projektować od początku |
| **Warstwa modelu pod wielu dostawców** (abstrakcja LLM) | Glean/Dust (hub LLM) | konfiguracja „dostępne modele"; zaprojektować abstrakcję mimo startu na SDK Anthropic |
| **Pamięć jako lifecycle** (ADD/UPDATE/DELETE + decay/konsolidacja) | Mem0/Zep, MemoryBank | dec. 12 — interfejs pod pełny lifecycle; MVP: ADD + retrieval |
| **Guardrails** (step limiters, output validators, autonomy policies) | Agentforce, Cohere | przyszłe pole schematu agenta (poza MVP) |
| **Admin „Control Tower"** (inventory agentów + audyt + polityki) | ServiceNow, Writer AI HQ | przyszły panel admina |
| **Eval RAG** (RAGAS: faithfulness/recall/relevance + złote zbiory) | RAGAS, MultiHop-RAG/CRAG | Faza 4 — w CI |
| **A2A obok MCP** (interop agentów) | Google ADK, ServiceNow, Copilot | faza multi-agent — do obserwacji |
| **Self-hosted/prywatne wdrożenie jako wyróżnik** | Cohere North; README | wizja (self-hosted) |

## 3. Reguły projektowe (do trzymania przy implementacji)

- **RAG: start hybrid + reranker**; Graph RAG/RAPTOR tylko lazy/incremental (LazyGraphRAG, EraRAG) i tylko dla cross-document. Nigdy „pełny GraphRAG od zera przy każdej zmianie".
- **Routing to 4 osobne problemy** (model / agent / tool / „kiedy myśleć") — abstrakcja routera ma je rozróżniać.
- **Cegły z SDK Anthropic** zamiast własnych: prompt caching, tool search (`tool_search_tool_*` + `defer_loading`), context editing/compaction, adaptive thinking + `effort`.
- **Checkpointing LangGraph = replay/audyt** — gdy przejdziemy na multi-agent, checkpointer (PostgresSaver) wspiera nasz wymóg replay (dec. 13).
- **Wzorce z Managed Agents** (vaults per-user, agent jako wersjonowany obiekt) — inspiracja dla magazynu tokenów (dec. 3) i edytora agentów (dec. 10), mimo że idziemy self-hosted.

## 4. Wciąż otwarte (wybór technologii)

- Magazyn wektorowy + model embeddingów (wspólny pamięć/RAG).
- Reranker.
- Narzędzie do eval RAG (RAGAS/Langfuse) + złote zbiory.
