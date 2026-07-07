# Prompt startowy dla implementacji (Opus / Claude Code)

> Wklej poniższą treść jako pierwszy prompt w sesji Claude Code (Opus 4.8) na serwerze/maszynie dev.
> Źródło prawdy o planie: `docs/MVP.md`, `docs/README.md`, `docs/research/`.

---

Jesteś Claude Code (Opus 4.8) i zaczynasz implementację MVP **AI Workspace** zgodnie z gotowym planem w tym repo.

**Najpierw przeczytaj:** `docs/README.md` → `docs/MVP.md` → `docs/research/2026-07-04--000--implications.md`. To jest źródło prawdy; nie zmieniaj decyzji bez potwierdzenia użytkownika.

## Zasady nienaruszalne (z decyzji 1–17)

- **Rdzeń agenta:** **OpenRouter (API zgodne z OpenAI) + własna pętla tool-calling.** Klient OpenAI SDK skierowany na OpenRouter; pętlę agentową piszemy sami (pełna kontrola nad trace/audytem). Narzędzia **MCP** konwertowane do formatu tool-calling OpenAI. **Model domyślny — do ustalenia** (konfigurowalny per agent/tenant, cost-sensitive; Claude drogi). **NIE** tool_runner Anthropic, **NIE** LiteLLM, **NIE** LangGraph na tym etapie.
- **Backend:** reuse rdzenia gear-stack (FastAPI). **Monorepo z layoutem gear-stacka** (frontend Vue w roocie + `backend/`).
- **Frontend:** reuse Vue z gear-stack (moduł `ai`), **chat-first**, streaming **SSE**.
- **Auth:** **per-user OAuth** (Jira, GitLab, Google, Microsoft). Szyfrowany magazyn tokenów + odświeżanie; wstrzykiwanie tokenu użytkownika do wywołań narzędzi MCP.
- **Konfiguracja:** kaskada z sufitami/allow-listami (Aplikacja→Tenant→Zespół→Użytkownik): dostępne modele + domyślny, limity tokenów, RAG on/off, tools on/off. Efektywna konfiguracja = przecięcie ograniczeń + override.
- **Multi-tenancy:** tenant-aware i izolacja od dnia 1, praktycznie jeden tenant. Użytkownik należy do wielu tenantów (M:N). Dane tenant-scoped.
- **Persystencja/audyt:** lekki **Task/Run + trace** (kroki, wywołania modelu/narzędzi wej/wyj, pobrana wiedza, tokeny/koszt, czas, status). Audyt **dostępny z czatu**, z kopiowaniem całego runu i każdego kroku (łącznie z system promptem).
- **Baza wektorowa:** pgvector **za interfejsem** (dopiero Faza 4).
- **Integracje:** **własne cienkie serwery MCP** per dostawca.

## Krok 0 — Bootstrap (kopia gear-stack) ✅

**Status:** ukończony 2026-07-05.

| Zadanie | Status |
|---------|--------|
| Kod gear-stack w repo (layout: frontend w roocie + `backend/`) | ✅ |
| Zachowane `docs/` i `README.md` AI Workspace | ✅ |
| Pominięte pliki narracyjne gear-stack (`BUGS.md`, `CHANGELOG.md`, …) | ✅ |
| `src/`, `public/`, `tests/`, `scripts/`, `.github/`, konfiguracja build | ✅ |
| `LICENSE` (proprietary — kopiowanie bez zgody zabronione) | ✅ |
| `.gitattributes`, `.cursorrules` (oczyszczone z szumu gear-stack) | ✅ |
| `exec.sh` zachowany | ✅ |
| Commit bootstrap | ✅ |
| Build/env smoke test | ⏳ WIP |
| Świeży `CLAUDE.md` dla AI Workspace | ✅ |

**Uwagi po bootstrapie:** kod dziedziczy nazewnictwo gear-stack w Docker/env (`gear-stack-app`, `VITE_APP_ID=gear-stack`) — rename w osobnym kroku. Nie oczekuj, że wszystko od razu się buduje.

### Oryginalna checklista (archiwum)

- Wciągnij kod gear-stack do tego repo, **zachowując layout gear-stacka** (frontend w roocie + `backend/`).
- **Nie nadpisuj** naszego `docs/` ani `README.md`. Pomiń: `gear-stack/docs/`, jego `README.md`, `CLAUDE.md`, pliki narracyjne (`BUGS.md`, `CHANGELOG.md`, `DEPLOYMENT.md`, `FEATURES.md`, `MIGRATION_*`, `V2_*`, `screenshot.png`) oraz `.git`.
- Zacommituj jako `chore: bootstrap monorepo from gear-stack (mirrored layout, WIP)`.
- Napisz świeży `CLAUDE.md` dla AI Workspace (konwencje z gear-stack + specyfika tego projektu).

## Faza 0 — Fundament

- **Model danych:** Tenant, Zespół, Użytkownik + członkostwo **M:N user↔tenant** (aktywny tenant); reuse auth/users/RBAC z gear-stack. Wszystko tenant-scoped.
- **Resolver konfiguracji kaskadowej** (sufity/allow-listy + override).
- **Magazyn tokenów per-user OAuth** (szyfrowanie at-rest, refresh) + abstrakcja wstrzykiwania tokenu do wywołań MCP.

## Faza 1 — Pionowy plaster (Jira 360° end-to-end)

- **Moduł agenta** na tool runnerze + **trace/audyt** per uruchomienie.
- **Dwa cienkie serwery MCP:** Jira + GitLab, z per-user token injection. Narzędzia: Jira `get_issue` (+ odczyt pola „Klient"), GitLab `search` po kluczu Jiry.
- **Przepływ:** klucz issue Jiry → pobierz issue → wyciągnij Klienta → szukaj w GitLab → złóż **widok 360°**.
- **Czat** (reuse modułu `ai`) + **SSE** (streaming kroków i odpowiedzi); render wyniku: Markdown + minimalny rejestr bogatych bloków (karta/tabela; wykresy w Fazie 3).
- **Audyt w czacie** z kopiowaniem runu i kroków (z system promptem).

## Prerekwizyty — dopytaj użytkownika PRZED uruchomieniem

- `OPENROUTER_API_KEY` (dostęp do OpenRouter). **Domyślny model:** rekomendacja **Gemini Flash** (patrz `docs/research/2026-07-06--005--model-selection.md`); potwierdź z użytkownikiem, sprawdź aktualne ID/ceny na OpenRouter, docelowo zwaliduj A/B na zadaniu 360°.
- Aplikacje OAuth dla **Jira + GitLab** (client id/secret, scopes, redirect URI).
- Instancje testowe **Jira + GitLab**.

## Praktyki pracy

- Pracuj na gałęzi; **commituj i pushuj regularnie**. `docs/` pozostaje źródłem prawdy — aktualizuj „Otwarte punkty" w `MVP.md`, gdy je rozstrzygasz.
- Frontend: **pnpm**. Backend: docker compose (`backend/docker-compose.dev.yml`). **Zasada bezpieczeństwa: NIGDY nie uruchamiaj Dockera, jeśli katalog projektu zaczyna się od podkreślenia** (`_`).
- **Zweryfikuj pionowy plaster end-to-end** na realnych Jira+GitLab, zanim uznasz go za gotowy.
- **Pytaj przed** dużymi/nieodwracalnymi lub „na zewnątrz" działaniami. Nie twórz PR-a, dopóki użytkownik nie poprosi.

## Nie buduj teraz (odłożone)

Auto-router LLM, pamięć/RAG (Faza 4), pełny onboarding multi-tenant (B), guardrails, admin „control tower", katalog bloków ponad karty/tabele/wykresy. (Multi-model zapewnia OpenRouter — nie buduj własnej warstwy abstrakcji dostawców.)

**Zacznij od:** przeczytania dokumentów → potwierdzenia prerekwizytów z użytkownikiem → wykonania Kroku 0 (bootstrap).
