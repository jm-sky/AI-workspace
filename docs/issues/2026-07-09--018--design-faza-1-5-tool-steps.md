# Issue 018 — Faza 1.5 krok 3 — inline tool steps w wątku

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Commit:** `f6f6570`  
**Obszar:** frontend (`workspace`)  
**Z tego samego promptu:** [#012](./2026-07-09--012--design-faza-1-5-chat-tokens.md), [#017](./2026-07-09--017--design-faza-1-5-chat-shell.md), [#019](./2026-07-09--019--design-faza-1-5-rich-blocks.md)

## Prompt (Claude Code)

> commit, push i potem nastepne kroki wg planu. I trzeba znalezc miejsce/czas na nowy design.

## Decyzja

Podczas wywołań narzędzi użytkownik ma **widzieć postęp w wątku** (jak Claude Code), nie tylko końcową odpowiedź. Kroki narzędzi renderowane inline między wiadomościami — „obecność AI” bez osobnego modala.

## Implementacja

- `f6f6570` — `feat(design): Faza 1.5 inline tool steps — AI presence in the thread`

## Weryfikacja

- Run z GitHub MCP pokazuje kroki w historii czatu
- Kroki zwijalne / czytelne w dark mode
