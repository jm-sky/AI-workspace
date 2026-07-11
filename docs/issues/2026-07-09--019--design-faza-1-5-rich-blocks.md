# Issue 019 — Faza 1.5 krok 4 — rich blocks (karty, tabele)

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Commit:** `6232f5f`  
**Obszar:** frontend (`workspace`)  
**Z tego samego promptu:** [#012](./2026-07-09--012--design-faza-1-5-chat-tokens.md) … [#018](./2026-07-09--018--design-faza-1-5-tool-steps.md)

## Prompt (Claude Code)

> commit, push i potem nastepne kroki wg planu. I trzeba znalezc miejsce/czas na nowy design.

## Decyzja

Odpowiedzi strukturalne (tabele, listy, karty 360°) dostają **premium rendering** zamiast gołego markdown — spójny z tokenami z kroku 1 i bąbelkami z kroku 2.

## Implementacja

- `6232f5f` — `feat(design): Faza 1.5 rich blocks — premium 360° cards & tables`
- `5ba8638` — docs: oznaczenie kroków 1–4 jako done

## Weryfikacja

- Tabela w odpowiedzi agenta: obramowanie hairline, czytelne w dark mode
- Karty nie „wypadają” poza canvas wątku
