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
| 8 | Rozwiązywanie konfiguracji | **A — kaskada z sufitami/allow-listami (governance).** Wyższy poziom ogranicza niższy: Tenant ustala allow-listę modeli i twarde limity, Zespół zawęża, Użytkownik wybiera w ramach dozwolonego. Efektywna konfiguracja = przecięcie ograniczeń + override wartości. |
| 9 | Routing agentów | **C — hybryda, router jako abstrakcja.** Interfejs „wiadomość → agent" z wymiennymi strategiami. Start: **jawny wybór** użytkownika; **auto-router LLM** dokładany później jako druga strategia, z możliwością jawnego nadpisania. |
| 10 | Definiowanie agentów | **Edytor agentów dla adminów** — agent jest konfigurowalnym obiektem definiowanym przez admina; po zdefiniowaniu jest dostępny dla routera (i użytkowników). Agent scala: model, narzędzia (tools injection), pamięć (memory injection), prompt/personę, metadane routingu. |
| 11 | Schemat obiektu Agent | Pola: **nazwa + opis** (opis używany przez auto-router), **prompt/persona**, **model** (z allow-listy, opcj. `effort`), **narzędzia MCP** (tools injection) + flaga tool search, **zakresy pamięci** (memory injection), **RAG** (on/off + źródła), **metadane routingu** (wyzwalacze/przykłady), **widoczność/uprawnienia** (zespół/tenant), **limity** (opcjonalnie, w ramach sufitów). |
| 12 | Pamięć (memory) | **Zakresy: sesja, użytkownik, agent.** Mechanizm **B (RAG-owy):** pamięć w magazynie wektorowym; automatyczne wstrzykiwanie po przekroczeniu progu podobieństwa semantycznego **+** narzędzie dla agenta do przeszukiwania pamięci na żądanie. **Współdzieli infrastrukturę wektorową z RAG.** |
| 13 | Persystencja i audyt | **Lekki Task/Run + trace** teraz (rozmowy + per uruchomienie: kroki, wywołania modelu/narzędzi wej/wyj, pobrana wiedza, tokeny/koszt, czas, status; powiązane z tenantem/użytkownikiem). Pełny Task (replay/continuation) później. **Audyt dostępny z poziomu czatu**, z przyciskiem kopiowania **całego runu** i **każdego kroku** (łącznie z system promptem) — do debugowania. |
| 14 | Wyjście do UI | **Streaming: SSE** (serwer→klient; WebSocket później, jeśli potrzebna dwukierunkowość/interrupt). **Prezentacja: Markdown (domyślnie) + rejestr bogatych bloków** renderowanych z JSON: karty, tabele, odnośniki do źródeł oraz **wykresy** (np. przychody w roku — wykres liniowy). Katalog bloków rozszerzalny (mermaid, kanban, mapy…) później. |
| 15 | Multi-tenancy | **A na start** — dane tenant-aware i izolacja per-tenant od początku, praktycznie jeden tenant. **B wkrótce** — rejestracja tenanta, onboarding, wybór/przełączanie tenanta. **Użytkownik należy do wielu tenantów** (relacja M:N, przełączanie aktywnego tenanta). Poświadczenia OAuth per-użytkownik; dane (agenci, konfiguracja, pamięć) tenant-scoped. |

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

## Research (workstream planu)

Zgodnie z README research jest pierwszym kamieniem milowym — nie kod produkcyjny. Wyniki dokumentowane w repo (`docs/research/...`). Ścieżki (do potwierdzenia/priorytetyzacji):

- **Platformy AI klasy enterprise (comparables)** — jak to robią gotowe produkty; przegląd i wnioski. Propozycja przeglądu: Glean, Microsoft 365 Copilot / Copilot Studio, Google Agentspace, Dust, Writer, Cohere North, ServiceNow AI, Salesforce Agentforce (lista do potwierdzenia).
- **Techniki pracy z AI (z README)** — RAG, Memory Injection, RAPTOR, Graph RAG, Agentic RAG, Hybrid Search, Query/Model/Prompt/Tool Routing, Context Engineering, Prompt Engineering, Long-term Memory, Context Compression/Caching, Semantic search, Knowledge graphs.
- **Frameworki agentowe (porównanie)** — SDK Anthropic (wybrany rdzeń) vs LangGraph vs inne; kiedy co.
- **Źródła wiedzy / „best of AI"** — przegląd wartościowych stron/kolekcji i papers.

**Deliverable:** notatki i podsumowania w `docs/research/`, stopniowo budujące bazę wiedzy projektu.

## Otwarte punkty (do ustalenia)

- **Magazyn wektorowy + model embeddingów** (wspólny dla pamięci i RAG) — wybór technologii.
- **Sekwencjonowanie budowy:** prymitywy platformy vs pierwszy agent (Jira 360°) — co pierwsze.
- **Źródło e-maila Klienta** do przeszukania Gmaila: pole w Jirze czy mapowanie z nazwy Klienta.
