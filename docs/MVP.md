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

## Otwarte punkty (do ustalenia)

- **Źródło e-maila Klienta** do przeszukania Gmaila: pole w Jirze czy mapowanie z nazwy Klienta.
- **Persystencja:** obiekt Task (stan/historia/artefakty), audit log.
- **UI / chat:** reuse frontendu Vue z gear-stack czy minimalny własny.
- **Zakres multi-tenancy** w MVP.
