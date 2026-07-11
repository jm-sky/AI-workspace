# Issue 011 — Source routing guard (ochrona przed wyciekiem kontekstu)

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Commit:** `2336a6e` (guard + JSONB fix w tym samym commicie)  
**Obszar:** backend (`agent`)  
**Z tego samego promptu:** [#009](./2026-07-09--009--multi-turn-chat-sessions-kickoff.md), [#006](./2026-07-09--006--pytest-jsonb-sqlite-compile-error.md)

## Prompt (Claude Code)

Część sesji kickoff (`IMPLEMENTATION_KICKOFF.md`) — wymaganie bezpieczeństwa przy multi-source workspace.

## Decyzja

Agent nie może mieszać kontekstu między źródłami (np. GitHub repo A vs B) bez jawnej autoryzacji ścieżki. **Source routing guard** weryfikuje, że żądanie narzędzia dotyczy dozwolonego źródła skonfigurowanego dla sesji/użytkownika.

Slot na późniejszy design pass (Faza 1.5) został dodany w tym samym commicie — infrastruktura pod wizualną warstwę czatu.

## Implementacja

- Commit `2336a6e` — `feat: source routing guard + Faza 1.5 design slot; fix JSONB-on-SQLite tests`
- Testy SQLite: [#006](./2026-07-09--006--pytest-jsonb-sqlite-compile-error.md)

## Weryfikacja

- Tool call do niedozwolonego źródła → odrzucone / bezpieczny błąd
- Dozwolone źródło (np. podłączony GitHub) → normalna ścieżka
