# Issue 015 — Przeglądarka modeli OpenRouter (filtry vision/tools/cena)

**Data:** 2026-07-10  
**Status:** `done` (2026-07-10)  
**Commit:** `bf8175b`  
**Obszar:** backend (`ai`) + frontend (`workspace`)  
**Z tego samego promptu:** [#014](./2026-07-10--014--model-picker-combobox-cards.md) (wcześniejszy prompt: combobox), [#016](./2026-07-10--016--model-picker-performance.md)

## Prompt (Claude Code)

> Model picker - mozemy dodac strone/modal z lepszym wyszukiwaniem. Np. modele z vision+tool sortowane wg ceny, z kosztem max $10 wyjscie.

## Decyzja

Zamiast ograniczać się do statycznej listy, **pobieramy live katalog OpenRouter** (~340+ modeli) i dajemy pełną przeglądarkę:

- Filtry: vision, tools, max cena wyjścia, kontekst
- Sortowanie jak w comboboxie
- Osobna strona/modal — combobox zostaje na szybki wybór w czacie

Uzasadnienie: użytkownik sam dobiera model pod zadanie (taniej vs mocniej) bez deployu nowej wersji aplikacji.

## Implementacja

- Commit `bf8175b` — `feat(models): live OpenRouter catalog + filterable model browser`
- Backend: endpoint katalogu z cache OpenRouter
- Frontend: `WorkspaceModelsSettingsPage.vue`, filtry w `filterModels.ts`

## Weryfikacja

- Filtr „vision + tools + max $10 output” zwraca sensowny podzbiór
- Wybór z przeglądarki ustawia model aktywnej sesji
