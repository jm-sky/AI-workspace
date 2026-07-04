# AI Workspace — MVP: Ustalenia

> Dokument roboczy. Zapisuje decyzje podejmowane wspólnie podczas ustalania MVP.
> Status: w trakcie ustaleń.

## North Star / kontekst

- **Odbiorca MVP:** dział IT w firmie (kancelaria podatkowa z wieloma oddziałami/departamentami jako potencjalny showcase). Docelowo platforma ma być **generyczna i konfigurowalna**, ale MVP dowozi jeden konkretny scenariusz na generycznym rdzeniu.
- **Scenariusz „wow":** agent buduje jeden spójny **widok 360°** na temat wybranego podmiotu, sięgając do wielu systemów naraz.

## Scenariusz MVP (przepływ)

- **Podmiot zapytania:** Issue z Jiry.
- **Wejście:** klucz issue (np. `IT-123`).
- **Przepływ agenta:**
  1. Pobierz issue z Jiry.
  2. Wyciągnij **Klienta** — z dedykowanego pola „Klient" w Jirze (pewne źródło).
  3. Rozejdź się po systemach **różnymi kluczami** per system:
     - **GitLab** → po ID zadania (kluczu Jiry).
     - **Gmail** → po adresie e-mail Klienta.
     - **Teams** → po nazwie Klienta w rozmowach.
  4. Złóż wszystko w jeden widok 360°.

## Systemy (MVP)

Gmail, Microsoft Teams, Jira, GitHub, GitLab — wszystkie ze standardowym, publicznym API.
(Powiązania w scenariuszu głównie: GitLab / Gmail / Teams.)

## Decyzje architektoniczne

| # | Obszar | Decyzja |
|---|--------|---------|
| 1 | Sterowanie agenta | **Agentowe (B)** — LLM w pętli (planuje → woła narzędzia → czyta wyniki → decyduje). |
| 2 | Rdzeń pętli agenta | **Tool runner z SDK Anthropic** (`client.beta.messages.tool_runner`); narzędzia jako MCP. Model **`claude-opus-4-8`**, myślenie adaptacyjne. **LangGraph odłożony** do etapu multi-agent (warstwa narzędzi MCP jest przenośna). |
| 3 | Uwierzytelnianie | **Per-user OAuth** — agent działa w imieniu użytkownika (Jira, GitLab, Google, Microsoft). Wymaga bezpiecznego przechowywania + odświeżania tokenów i wstrzykiwania tokenu użytkownika do wywołań narzędzi. |
| 4 | Backend | **Reuse rdzenia gear-stack** (FastAPI, users, OAuth, 2FA, RBAC, multi-tenancy, fundament API) + dołożony moduł agenta i integracje. |
| 5 | Warstwa integracji | **Opcja 2 — własne cienkie serwery MCP** (jeden na dostawcę, opakowują REST API). Jednolity standard MCP, czyste per-user token injection, brak zależności od auth cudzych serwerów. |
| 6 | Interfejs | **Chat-first (A)** — pełny czat: użytkownik pisze zapytanie, agent odpowiada widokiem 360°, można dopytywać. Bogaty output (karta/tabela + Markdown). Ten sam silnik (tool runner + MCP) obsłuży później inne fronty. |
| 7 | Frontend | **Reuse Vue z gear-stack** (Vue 3 + shadcn-vue + TanStack Query + moduł `ai` jako fundament czatu: historia, kontekst, streaming). |

## Zakres platformy (rozszerzenie MVP)

MVP to nie pojedynczy agent, lecz **konfigurowalna platforma agentowa**; scenariusz Jira 360° jest **pierwszym agentem** na tej platformie. Wymagane zdolności:

- **Chat** (chat-first).
- **Routing agentów** — kierowanie zapytania do właściwego agenta.
- **Memory injection** — wstrzykiwanie pamięci do kontekstu (zakresy do ustalenia: sesja/użytkownik/zespół/organizacja/projekt/agent).
- **Tools injection** — wstrzykiwanie dostępnych narzędzi do kontekstu agenta.
- **Tool search tool** — narzędzie do dynamicznego wyszukiwania narzędzi (gdy zestaw tooli rośnie; w SDK Anthropic: `tool_search_tool_regex/bm25` + `defer_loading`).

### Konfiguracja (hierarchia)

Ustawienia na poziomach: **Aplikacja → Tenant → Zespół → Użytkownik** (docelowo też Agent). Przykładowe parametry:

- dostępne modele + model domyślny,
- limity tokenów,
- czy RAG jest dostępny,
- czy narzędzia (tools) są dostępne,
- itd.

## Otwarte punkty (do ustalenia)

- **Model rozwiązywania konfiguracji** między poziomami (kaskada/override, limity jako sufity, allow-listy).
- **Routing agentów:** jawny wybór/@-mention vs automatyczny router LLM; ilu agentów na start.
- **Zakresy memory** i sposób ich wstrzykiwania.
- **Sekwencjonowanie budowy:** prymitywy platformy vs pierwszy agent (Jira 360°) — co pierwsze.
- **Źródło e-maila Klienta** do przeszukania Gmaila: pole w Jirze czy mapowanie z nazwy Klienta.
- **Transport streamingu** wyników/kroków agenta do UI (SSE?).
- **Prezentacja wyniku 360°:** ustrukturyzowany JSON renderowany jako karty/tabele vs sam Markdown.
- **Persystencja:** obiekt Task (stan/historia/artefakty), audit log.
- **Zakres multi-tenancy** w MVP.
