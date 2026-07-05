# Dokumentacja AI Workspace — indeks

Punkt wejścia do planu MVP i wyników researchu. Projekt jest w **fazie wizji i architektury**; plan MVP jest ustalony, research (runda 1) zrobiony.

## Nawigacja

### Wizja
- [`../README.md`](../README.md) — wizja produktu (AI Workspace / AI Operating System).

### Plan MVP
- [`MVP.md`](MVP.md) — **główny dokument planu**: 15 decyzji architektonicznych, schemat agenta, sekwencja budowy (fazy) i otwarte punkty. Zacznij tutaj.

### Research (`research/`)
- [`research/00-implications.md`](research/00-implications.md) — **synteza: research → wnioski dla planu** (co potwierdzone, co dopiąć, reguły projektowe). Czytać razem z `MVP.md`.
- [`research/01-enterprise-comparables.md`](research/01-enterprise-comparables.md) — 8 platform enterprise (Glean, Google Agentspace, Dust, Microsoft Copilot Studio, Salesforce Agentforce, Writer, ServiceNow, Cohere North).
- [`research/02-ai-techniques.md`](research/02-ai-techniques.md) — techniki AI: rodzina RAG, routing, context engineering, pamięć (+ koszt GraphRAG, eval RAG, lifecycle pamięci).
- [`research/03-agent-frameworks.md`](research/03-agent-frameworks.md) — frameworki agentowe: SDK Anthropic vs LangGraph + kryteria przełączenia.
- [`research/04-knowledge-sources.md`](research/04-knowledge-sources.md) — kuratorowana baza źródeł / „best of AI".

## Skrót decyzji (z `MVP.md`)

| # | Obszar | Decyzja |
|---|--------|---------|
| 1–2 | Rdzeń agenta | Agentowy; **tool runner SDK Anthropic** + narzędzia jako **MCP**; `claude-opus-4-8`; LangGraph przy multi-agent |
| 3 | Auth | **Per-user OAuth** (Jira, GitLab, Google, Microsoft) |
| 4 | Backend | **Reuse rdzenia gear-stack** (FastAPI, users, OAuth, RBAC, multi-tenancy) |
| 5 | Integracje | **Własne cienkie serwery MCP** per dostawca |
| 6–7 | UI | **Chat-first**; **reuse Vue z gear-stack** |
| 8 | Konfiguracja | **Kaskada z sufitami/allow-listami** (App→Tenant→Zespół→Użytkownik) |
| 9–11 | Agenci | Routing **hybrydowy** (start jawny wybór); **edytor agentów dla adminów**; schemat agenta |
| 12 | Pamięć | Zakresy sesja/użytkownik/agent; **RAG-owa** (semantic + narzędzie na żądanie) |
| 13 | Audyt | **Lekki Task/Run + trace**; audyt w czacie z kopiowaniem runu/kroku |
| 14 | Wyjście | **SSE** + Markdown + bogate bloki (karty/tabele/wykresy) |
| 15 | Multi-tenancy | **A teraz** (tenant-aware), **B wkrótce**; user w wielu tenantach (M:N) |

Scenariusz MVP: agent buduje **widok 360°** wokół **issue z Jiry** (Jira → Klient → fan-out do GitLab/Gmail/Teams).

## Zasady dla dokumentacji
- Nowe notatki z researchu: kolejne `research/NN-*.md`, linkowane w `research/00-implications.md`.
- Decyzje i otwarte punkty aktualizować w `MVP.md`.
