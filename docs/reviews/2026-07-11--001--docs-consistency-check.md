# Review: spójność dokumentacji projektu

**Data:** 2026-07-11
**Status:** `done`
**Zakres:** cała dokumentacja w `docs/` + `README.md` + `DESIGN.md` + `CLAUDE.md` + `.cursorrules`, skonfrontowana ze stanem faktycznym kodu (`backend/app/modules/`, `src/modules/`, migracje, `.env.example`).
**Powiązane:** [`MVP.md`](../MVP.md) · [`README.md`](../README.md) · [`IMPLEMENTATION_KICKOFF.md`](../IMPLEMENTATION_KICKOFF.md) · [`ai-kancelaria-comparison.md`](../research/2026-07-08--006--ai-kancelaria-comparison.md)

---

## Metoda

Przeczytane: `README.md`, `CLAUDE.md`, `.cursorrules`, `docs/README.md`, `docs/MVP.md`, `docs/IMPLEMENTATION_KICKOFF.md`, `DESIGN.md`, `docs/design/README.md`, `docs/deployment/*`, `docs/plans/README.md`, `docs/issues/README.md`, `docs/research/*` (w tym nowo dodane `chatgpt-settings-reference.md` i `2026-07-08--006--ai-kancelaria-comparison.md`), `docs/reviews/README.md`.

Skonfrontowane z kodem: struktura modułów `backend/app/modules/` i `src/modules/`, `backend/app/modules/agent/tools/__init__.py`, `backend/app/modules/integrations/` (providers, router), `backend/app/core/config.py` + `.env.example`, migracje `backend/migrations/059-061`, `git log` (daty ostatnich zmian per plik).

Nie oceniałem jakości kodu ani testów — tylko spójność dokumentacji z planem i ze stanem repo.

---

## Ustalenia

### A. Rozjazd statusu faz między dokumentami (ważne)

| Plik | Ostatnia zmiana | Co pokazuje |
|---|---|---|
| `docs/README.md` (nagłówek) | 2026-07-08 | „Faza 1 (Jira 360° end-to-end) — 🔄 w toku" |
| `CLAUDE.md` (tabela faz) | 2026-07-08 | Faza 1 „🔄 w toku", brak wiersza Faza 1.5 |
| `docs/MVP.md` / `IMPLEMENTATION_KICKOFF.md` | 2026-07-09 | „Logika Fazy 1 domknięta" ✅, **Faza 1.5 (design pass)** w toku, kroki 1–4 ✅ |

`docs/README.md` i `CLAUDE.md` nie zostały zaktualizowane, gdy Fazę 1 zamknięto i otwarto Fazę 1.5 dzień później. Ktoś czytający wyłącznie te dwa pliki (czyli oficjalny punkt wejścia + instrukcje agenta) ma nieaktualny obraz — nie wie, że trwa design pass ani że ma 4/6 kroków gotowe.

**Propozycja:** dodać wiersz „Faza 1.5" do tabeli faz w `CLAUDE.md` i zaktualizować nagłówek `docs/README.md` przy każdej zmianie statusu fazy (albo trzymać status wyłącznie w `MVP.md` i linkować z reszty, zamiast duplikować w 3 miejscach).

---

### B. Faza 4 (pamięć/RAG) już częściowo zaimplementowana, ale plan pokazuje ją jako nierozpoczętą

`docs/MVP.md` — tabela faz: `Faza 4 | Pamięć + RAG (pgvector) | —`.

W kodzie już istnieje:
- `backend/migrations/059_memory_entries.py` — `CREATE EXTENSION vector`, kolumna `embedding vector(N)`, indeks HNSW cosine.
- `backend/app/modules/memory/` — pełny moduł (repositories, embedding_service, memory_service).
- `backend/app/modules/agent/tools/memory.py` — `MemorySearchTool` / `MemorySaveTool`, **zarejestrowane w obu profilach narzędzi** (`github-workspace`, `jira-360`) w `agent/tools/__init__.py`.
- `.env.example`: `AI_MEMORY_EMBEDDING_MODEL=openai/text-embedding-3-small` już skonfigurowany.

To jest sprzeczne z zasadą z `MVP.md` („pionowy plaster najpierw, potem generalizacja") — pamięć semantyczna (jądro Fazy 4) powstała już przy okazji Fazy 1, ale plan tego nie odnotowuje. To dobra wiadomość (przewaga nad ai-kancelaria wg researchu #006 się potwierdza), ale dokumentacja powinna to odzwierciedlać, żeby nie zaplanować Fazy 4 od zera.

**Propozycja:** zaktualizować status Fazy 4 na 🔄 (częściowo: embedding + tool search/save gotowe; RAG nad dokumentacją, próg trafności „nie mam danych" i model rerankera — nadal otwarte, zgodnie z punktem P1 #9 z researchu ai-kancelaria).

---

### C. Domyślny model różni się od rekomendacji z researchu, a „Otwarte punkty" tego nie odzwierciedlają

`docs/research/2026-07-06--005--model-selection.md` rekomenduje **Gemini Flash** jako domyślny model. `docs/MVP.md` → „Otwarte punkty" nadal pokazuje to jako nierozstrzygnięte („do potwierdzenia po A/B").

W `.env.example` / `backend/app/core/config.py` faktyczny skonfigurowany domyślny model to:
```
WORKSPACE_DEFAULT_MODEL=qwen/qwen3-30b-a3b-instruct-2507
WORKSPACE_DEFAULT_ALLOWED_MODELS=["qwen/qwen3-30b-a3b-instruct-2507","google/gemini-2.5-flash","google/gemini-2.5-flash-lite","anthropic/claude-sonnet-4.5"]
```

Czyli decyzja **faktycznie zapadła** (Qwen3 30B, nie Gemini Flash) i działa w kodzie, ale plan wciąż mówi „do ustalenia" i nie wyjaśnia, dlaczego wybór odbiega od rekomendacji researchu. To rozjazd między „co jest w `.env.example`" a „co mówi `MVP.md`" — następna osoba/agent może próbować zmienić default na Gemini Flash, myśląc, że realizuje zamkniętą rekomendację, i nadpisać świadomą decyzję (albo odwrotnie: uznać Qwen3 za przypadkowe niedopatrzenie).

**Propozycja:** rozstrzygnąć jawnie w `MVP.md` — czy Qwen3 30B jest nowym defaultem po A/B (i wtedy zamknąć otwarty punkt z uzasadnieniem), czy to tymczasowe ustawienie do zmiany.

---

### D. Decyzja #3 („per-user OAuth: Jira, GitLab, Google, Microsoft") jest szersza niż stan implementacji

`docs/MVP.md` dec. #3 i `IMPLEMENTATION_KICKOFF.md` traktują Jira/GitLab/Google/Microsoft jednolicie jako „per-user OAuth". W kodzie:

- `backend/app/modules/integrations/providers/` ma **tylko** `github.py` — pełny flow `auth-url` + `callback/{provider}` + zdefiniowane scope'y (`GITHUB_OAUTH_SCOPES`).
- Jira i GitLab (`IntegrationProvider.JIRA`, `.GITLAB` w `types.py`) **nie mają** klasy providera OAuth — tokeny trafiają przez ogólny `PUT /tokens` (ręczne wprowadzenie, prawdopodobnie PAT), nie przez authorization-code flow.

To może być świadomy i rozsądny wybór (Jira Server/Data Center i GitLab self-hosted często nie mają łatwego OAuth), ale plan tego nie mówi wprost — czytelnik `MVP.md` założy, że Jira ma taki sam self-service OAuth jak GitHub.

**Propozycja:** doprecyzować dec. #3 — rozróżnić „OAuth (GitHub, docelowo Google/Microsoft)" od „token ręczny/PAT (Jira, GitLab)", albo opisać plan dociągnięcia OAuth dla Jira/GitLab jeśli to tylko tymczasowe uproszczenie.

---

### E. Nieudokumentowany drugi agent (`github-workspace`)

W `backend/app/modules/agent/tools/__init__.py` i `prompts/github_workspace.py` istnieje w pełni zaimplementowany agent „GitHub + memory" (`AGENT_TOOL_PROFILES["github-workspace"]`), **będący wartością domyślną** parametru `agent_key` w `build_tool_registry(...)`. Ma własny prompt, narzędzia GitHub (MCP), memory search/save.

`MVP.md` i `docs/README.md` opisują scenariusz MVP wyłącznie jako **Jira → Klient → fan-out GitLab/Gmail/Teams** (`jira-360`). Agent `github-workspace` nie jest wspomniany nigdzie w planie, otwartych punktach ani w Fazach — nie wiadomo, czy to:
- eksperyment/dogfooding przy okazji integracji GitHub OAuth,
- pierwszy krok pod przyszły „router agentów" (dec. #9–11),
- czy coś do wycięcia/przeniesienia poza MVP.

**Propozycja:** dopisać do `MVP.md` (Faza 1 lub sekcja „Rozstrzygnięcia") jedno zdanie o statusie i celu tego agenta — inaczej kolejna sesja może go przypadkiem usunąć albo rozbudować w złym kierunku.

---

### F. Nowy plik `docs/chatgpt-settings-reference.md` łamie własną konwencję dokumentacji i jest osierocony

`docs/README.md` § „Zasady dla dokumentacji": pliki w `issues/`, `reviews/`, `research/`, `plans/` mają nazwę `YYYY-MM-DD--NNN--slug.md` i muszą być dopisane do `README.md` danego katalogu.

`docs/chatgpt-settings-reference.md`:
- leży bezpośrednio w `docs/`, nie w `docs/research/`,
- nie ma numeru/daty w nazwie,
- nie jest wpisany w `docs/research/README.md` ani w nawigacji `docs/README.md`,
- nie jest powiązany z żadnym otwartym punktem w `MVP.md` (personalizacja/ustawienia AI pojawia się pośrednio w dec. #8 i w wizji `CLAUDE.md` root, ale nie ma wprost odniesienia).

Efekt: dokument istnieje w repo, ale nikt idący za `docs/README.md` (udokumentowaną ścieżką nawigacji) go nie znajdzie.

**Propozycja:** przenieść do `docs/research/2026-07-1x--007--chatgpt-settings-reference.md`, dodać wiersz w `docs/research/README.md`, i dopisać w `MVP.md` → Otwarte punkty odniesienie („ustawienia/personalizacja AI — patrz research #007; mapuje się na Fazę 3 (edytor agentów/custom instructions) i Fazę 4 (pamięć wielopoziomowa: fakty/profile/projekt/sesja)").

---

### G. `DESIGN.md` i `docs/design/` nie są w nawigacji `docs/README.md`

`CLAUDE.md` wymienia `DESIGN.md` jako jedno ze „źródeł prawdy". `docs/design/README.md` istnieje i indeksuje referencje ChatGPT/Linear. Ale **`docs/README.md`** (główny indeks nawigacyjny) nie ma sekcji „Design" — nie linkuje ani do `../DESIGN.md`, ani do `design/README.md`. Cała Faza 1.5 (design pass, aktualnie w toku) opiera się na dokumencie, do którego nie prowadzi żadna ścieżka z głównego indeksu.

**Propozycja:** dodać sekcję „Design" do `docs/README.md` obok „Plan MVP" i „Deployment".

---

### H. `DESIGN.md` wspomina AuthKit jako referencję, ale nie ma dla niej materiału

`DESIGN.md` § „Visual references" opisuje **AuthKit** („modern component styling, subtle lighting effects, blur/glass, elegant cards") na równi z ChatGPT i Linear. Ale `docs/design/refero/` ma tylko `chatgpt/` i `linear/` — brak `authkit/`, i `docs/design/README.md` (indeks) też wymienia tylko te dwa źródła.

Nie wiadomo, czy AuthKit to: referencja tylko „z pamięci" (bez zebranych materiałów refero.design), czy zapomniano dociągnąć pliki, czy sekcję należy usunąć.

**Propozycja:** albo dociągnąć `docs/design/refero/authkit/` (DESIGN.md + tailwind.css jak dla pozostałych dwóch), albo usunąć wzmiankę o AuthKit z `DESIGN.md`, żeby dokument nie obiecywał czegoś, czego nie ma.

---

### I. Listy modułów w `CLAUDE.md` i `.cursorrules` są mocno nieaktualne

**`CLAUDE.md`** § „Moduły backendu" wymienia 9 modułów: `auth, users, two_factor, tenants, teams, workspace_config, integrations, agent, ai`.
Faktyczny `backend/app/modules/` ma **18** katalogów — brakuje w opisie: `admin, billing, feature_limits, gear, gear_settings, logs, mcp, memory, settings, stats`. W szczególności brakuje **`memory`** (pgvector, patrz punkt B) i **`mcp`** (klient MCP GitHub) — obu kluczowych dla obecnej fazy.

**`.cursorrules`** § „Modules (inherited from gear-stack)" dla frontendu: `auth, user, settings, admin, ai, gear (legacy), stats`.
Faktyczny `src/modules/` = `admin, auth, billing, settings, tenants, user, workspace`. Brakuje **`workspace`** — czyli dokładnie modułu czatu/360°/Faza 1–1.5, najważniejszego w tej chwili — oraz `tenants`/`billing`. Jednocześnie lista wymienia `gear` i `ai`, których w `src/modules/` w ogóle nie ma (to moduły backendowe, nie frontendowe).

**Propozycja:** zaktualizować obie listy zgodnie ze stanem repo; rozważyć krótką adnotację przy modułach dziedziczonych z gear-stack, które są legacy/do usunięcia (`gear`, `gear_settings`, `billing`, `feature_limits`?) vs docelowe dla AI Workspace (`agent`, `memory`, `mcp`, `integrations`, `workspace_config`).

---

## Drobne obserwacje (bez zmian architektonicznych)

- `docs/reviews/README.md` był pusty (`— | — | — | —`) — ten dokument jest pierwszym wpisem; dodałem wiersz w indeksie.
- `docs/MVP.md` § „Otwarte punkty" nie wspomina „do dopracowania w Fazie 1.5" z `IMPLEMENTATION_KICKOFF.md` (puste stany, micro-interactions, weryfikacja wizualna dev/prod) — warto scalić w jedno miejsce, żeby nie utrzymywać dwóch list otwartych zadań w dwóch plikach.
- Konwencja `docs/README.md` mówi „dodaj wiersz w README.md danego katalogu" przy nowym wpisie — `docs/research/2026-07-08--006--ai-kancelaria-comparison.md` **jest** poprawnie zaindeksowany (dobry przykład, w kontraście do punktu F).
- Porty/domeny w `CLAUDE.md`, `.cursorrules`, `docs/deployment/*` i `backend/docker-compose.dev.yml` są spójne (8003/5435/6382/5176) — bez zastrzeżeń.

---

## Priorytetyzacja

| # | Ustalenie | Wpływ | Nakład poprawki |
|---|-----------|-------|------------------|
| A | Status faz rozjechany (`docs/README.md`/`CLAUDE.md` vs `MVP.md`) | Wysoki — pierwszy punkt wejścia dla nowej sesji/agenta | Niski |
| I | Listy modułów nieaktualne (brak `memory`, `mcp`, `workspace`) | Wysoki — agent może nie odkryć istniejącego kodu i zduplikować robotę | Niski |
| E | Nieudokumentowany agent `github-workspace` | Średni-wysoki — ryzyko przypadkowej regresji/usunięcia | Niski |
| B | Faza 4 częściowo zrobiona, plan mówi „—" | Średni — błędne planowanie zakresu przyszłych faz | Niski |
| D | Dec. #3 OAuth zbyt ogólna vs Jira/GitLab = PAT | Średni — mylące dla przyszłej integracji Google/Microsoft OAuth | Niski |
| C | Default model: Qwen3 w kodzie vs „otwarty punkt" w planie | Średni — niejasne czy to decyzja czy tymczasowość | Niski (decyzja do potwierdzenia z użytkownikiem) |
| F | `chatgpt-settings-reference.md` osierocony | Niski-średni — na razie tylko referencja, nic nie zależy | Niski |
| G | `DESIGN.md`/`docs/design/` brak w nawigacji | Niski-średni — utrudnia onboarding do Fazy 1.5 | Bardzo niski |
| H | AuthKit bez materiału źródłowego | Niski | Do decyzji (dociągnąć vs usunąć) |

---

## Rekomendowane następne kroki

1. Ujednolicić status faz — jedno źródło prawdy (`MVP.md`), reszta plików tylko linkuje/podsumowuje i jest aktualizowana przy każdej zmianie fazy.
2. Zaktualizować listy modułów w `CLAUDE.md` i `.cursorrules` do stanu faktycznego (`memory`, `mcp`, `workspace` w szczególności).
3. Dopisać do `MVP.md` krótkie wyjaśnienie agenta `github-workspace` i zrewidować status Fazy 4 (pgvector już częściowo gotowe).
4. Rozstrzygnąć z użytkownikiem: (a) czy Qwen3 30B jest ostatecznym defaultem, (b) doprecyzowanie dec. #3 OAuth vs PAT dla Jira/GitLab.
5. Przenieść `chatgpt-settings-reference.md` do `docs/research/` z numerem i wpisem w indeksie; dodać sekcję „Design" do `docs/README.md`; zdecydować co z AuthKit w `DESIGN.md`.

Chętnie zrobię 2–3 (mechaniczne, niskiego ryzyka) od razu po Twoim potwierdzeniu — 4 i część 5 (decyzje) zostawiam do wspólnego omówienia.
