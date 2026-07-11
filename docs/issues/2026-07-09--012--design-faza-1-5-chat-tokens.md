# Issue 012 — Faza 1.5 krok 1 — tokeny powierzchni i Inter

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Commit:** `d51bf88`  
**Obszar:** frontend (`css`, design tokens)  
**Z tego samego promptu:** [#017](./2026-07-09--017--design-faza-1-5-chat-shell.md), [#018](./2026-07-09--018--design-faza-1-5-tool-steps.md), [#019](./2026-07-09--019--design-faza-1-5-rich-blocks.md)

## Prompt (Claude Code)

> commit, push i potem nastepne kroki wg planu. I trzeba znalezc miejsce/czas na nowy design.

## Decyzja

Fundament wizualny przed zmianami w komponentach:

- `--surface-canvas`, `--surface-raised`, `--hairline` w `style.css`
- Font **Inter** zamiast domyślnego stacku
- Slot w layoutcie pod późniejszy shell czatu (commit `2336a6e`)

Bez tego kroków 2–4 nie da się sensownie stylować stron workspace.

## Implementacja

- `d51bf88` — `feat(design): Faza 1.5 foundation — Inter font + chat surface tokens`

## Weryfikacja

- DevTools: zmienne CSS dostępne w light i dark
- `ChatLayout` / `SidebarInset` używa `bg-surface`
