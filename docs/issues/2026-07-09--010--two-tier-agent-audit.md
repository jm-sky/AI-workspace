# Issue 010 — Audyt dwuwarstwowy agenta

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Commit:** `39c65ca`  
**Obszar:** backend (`agent`) + frontend (`workspace`)  
**Z tego samego promptu:** [#009](./2026-07-09--009--multi-turn-chat-sessions-kickoff.md) (kickoff + „potem audyt dwuwarstwowy”)

## Prompt (Claude Code)

> Tak. teraz commit i push, potem audyt dwuwarstwowy

## Decyzja

Ślad działania agenta dzielimy na dwie warstwy widoczności:

1. **Warstwa użytkownika** — zredagowane podsumowanie kroków (bez wrażliwych danych w promptach/narzędziach).
2. **Warstwa admina** — pełny raw trace (system prompt, tool calls, odpowiedzi) z retencją.

Uzasadnienie: zwykły użytkownik widzi „co agent robił”, admin/debug ma pełną forensics bez mieszania uprawnień.

## Implementacja

- Commit `39c65ca` — `feat: two-tier agent audit (redacted summary + admin raw tier with retention)`
- UI: przycisk Audyt/Trace w toolbarze czatu (sheet z historią kroków)
- Powiązane poprawki UI: [#007](./2026-07-09--007--audit-sheet-no-padding.md) (padding w sheet)

## Weryfikacja

- Użytkownik widzi skrócony audyt po zakończeniu runu
- Admin ma dostęp do pełnego tieru (zgodnie z rolą)
