# Issue 017 — Faza 1.5 krok 2 — shell czatu (bąbelki, composer)

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Commit:** `ea8620a`  
**Obszar:** frontend (`workspace`)  
**Z tego samego promptu:** [#012](./2026-07-09--012--design-faza-1-5-chat-tokens.md), [#018](./2026-07-09--018--design-faza-1-5-tool-steps.md), [#019](./2026-07-09--019--design-faza-1-5-rich-blocks.md)

## Prompt (Claude Code)

> commit, push i potem nastepne kroki wg planu. I trzeba znalezc miejsce/czas na nowy design.

## Decyzja

Główny ekran aplikacji = czat. Wzorzec ChatGPT/Claude:

- **Achromatyczne bąbelki** user/assistant (bez kolorowych „kart”)
- **Premium composer** — wyraźne tło, hairline, zaokrąglenie (`bg-surface-canvas`)
- Więcej miejsca na treść, mniej wizualnego szumu w toolbarze

## Implementacja

- `ea8620a` — `feat(design): Faza 1.5 chat shell — achromatic bubbles + premium composer`

## Weryfikacja

- Wiadomości user/assistant odcinają się od tła canvas
- Composer widoczny na mobile bez zlewania z tłem
