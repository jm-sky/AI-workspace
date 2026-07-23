# Issue 021 — Backport 2FA i shared-core UX z gear-stack

**Data:** 2026-07-08  
**Status:** `done` (2026-07-08)  
**Commit:** `683855c`  
**Obszar:** shared core (auth, frontend)

## Prompt

Backport z rodziny core (gear-stack jako źródło) — bez dedykowanego promptu w sesji 8–10 lipca; commit na `develop` 08.07.

## Decyzja

ai-workspace dziedziczy boilerplate gear-stack. Poprawki 2FA i UX z referencji muszą być zsynchronizowane, żeby auth i logowanie zachowywały się tak samo jak w pozostałych apkach VPS.

## Implementacja

- `683855c` — `Backport 2FA fixes and shared-core UX from gear-stack.`

## Weryfikacja

- 2FA enrollment/login zgodne z gear-stack
- Brak regresji w flow logowania
