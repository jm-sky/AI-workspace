# Research 04 — Źródła wiedzy / „best of AI"

> Ścieżka 4 workstreamu research. Kuratorowana lista wartościowych źródeł do budowy bazy wiedzy projektu.
> Data: 2026-07. Dokument żywy — dopisywać wartościowe znaleziska.
> ⭐ = wysoki priorytet dla naszego projektu.

## Fundament: agenci i context engineering (Anthropic)

Najbliższe naszemu rdzeniowi (SDK Anthropic, tool runner) — czytać w pierwszej kolejności.

- ⭐ **Building Effective Agents** — kiedy agent vs workflow, wzorce (prompt chaining, routing, orchestrator-workers, evaluator-optimizer). https://www.anthropic.com/research/building-effective-agents
- ⭐ **Effective Context Engineering for AI Agents** — „najmniejszy zestaw wysokosygnałowych tokenów"; system prompt, narzędzia, przykłady, historia. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- ⭐ **Writing Tools for Agents** — jak projektować opisy/specyfikacje narzędzi (kluczowe dla naszych serwerów MCP i „tools injection"). https://www.anthropic.com/engineering/writing-tools-for-agents
- **Building Effective AI Agents — Architecture Patterns (PDF)** — przykłady produkcyjne (Coinbase, Intercom, Thomson Reuters). https://resources.anthropic.com/building-effective-ai-agents

## Protokoły integracji

- ⭐ **Model Context Protocol** — spec + dokumentacja (rdzeń naszej warstwy narzędzi, dec. 5). https://modelcontextprotocol.io
- **A2A (Agent-to-Agent)** — protokół interop agentów (na fazę multi-agent). https://a2a-protocol.org (patrz też Google ADK)

## Frameworki agentowe (dokumentacja)

- ⭐ **LangGraph** — graf stanów, checkpointing, multi-agent (nasza faza multi-agent). https://langchain-ai.github.io/langgraph/
- **PydanticAI** — type-safe, MCP-native (potencjalny komplement). https://ai.pydantic.dev
- **Google ADK** — hierarchiczny, natywne A2A. https://google.github.io/adk-docs/

## RAG, retrieval i ewaluacja

- ⭐ **RAGAS** — metryki eval (faithfulness/context precision/recall) — od Fazy 4. https://docs.ragas.io
- **Microsoft LazyGraphRAG** — Graph RAG w koszcie vector RAG (jeśli graf). https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
- **RAGFlow — RAG 2025 review** — przegląd stanu RAG. https://ragflow.io/blog/rag-review-2025-from-rag-to-context
- **awesome-generative-ai-guide (rag research table)** — bieżący przegląd papers RAG. https://github.com/aishwaryanr/awesome-generative-ai-guide

## Pamięć agentów

- ⭐ **Agent Memory Paper List** — „Memory in the Age of AI Agents: A Survey". https://github.com/Shichun-Liu/Agent-Memory-Paper-List
- **Mem0** — pamięć jako lifecycle (extract/update). https://mem0.ai
- **Zep** — temporalny knowledge graph pamięci. https://www.getzep.com

## Routing modeli

- **vLLM Semantic Router** — open-source router mixture-of-models (wzorzec model routingu). https://github.com/vllm-project/semantic-router

## Kolekcje / awesome-listy (implementacje do podejrzenia)

- ⭐ **awesome-llm-apps** — 100+ gotowych appek Agent & RAG (fork-and-ship). https://github.com/Shubhamsaboo/awesome-llm-apps
- **awesome-ai-agents-2026** — 300+ agentów/frameworków + benchmarki. https://github.com/ARUNAGIRINATHAN-K/awesome-ai-agents-2026

## Książki

- ⭐ **AI Engineering** (Chip Huyen) — inżynieria systemów LLM, eval, inference, MLOps.
- **LLM Engineering Handbook** (Paul Iusztin, Maxime Labonne) — vector search, prompt chaining, eval, RAG end-to-end.

## Blogi / ludzie (praktyka i eval)

- **Latent Space** (AI Engineer) — https://www.latent.space
- **Chip Huyen** — https://huyenchip.com/blog
- **Simon Willison** (LLM, praktyka) — https://simonwillison.net
- **Eugene Yan** (ML/LLM systemy, eval) — https://eugeneyan.com
- **Hamel Husain** (evals) — https://hamel.dev
- **Dust blog** (enterprise agents / MCP — najbliższy naszej wizji) — https://blog.dust.tt

## Jak używać
- Do bazy wiedzy projektu: przy każdej fazie z `../MVP.md` sięgać po ⭐ z odpowiedniej sekcji.
- Notatki z lektur zapisywać jako kolejne `docs/research/YYYY-MM-DD--NNN--slug.md` i dodawać wiersz w `docs/research/README.md`.

## Źródła (skąd ta lista)
- https://www.firecrawl.dev/blog/best-ai-resources
- https://medium.com/javarevisited/10-best-resources-to-learn-ai-and-llm-engineering-in-2025-cbb5f69a5f6d
- https://github.com/Shubhamsaboo/awesome-llm-apps
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
