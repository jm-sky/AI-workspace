# Issue 016 — Model picker — wydajność otwarcia (lazy load)

**Data:** 2026-07-10  
**Status:** `done`  
**Obszar:** frontend (`workspace`)

## Prompt (Claude Code)

> Model picker - need optimization, open takes ages. Maybe virtual scroll, lazy load.

## Problem

`WorkspaceModelComboBox.vue` nad katalogiem **343 modeli** OpenRouter:

- Przy otwarciu montuje 50 ciężkich `CommandItem` + `WorkspaceModelCard` (~20 węzłów DOM każdy)
- shadcn `Command` filtruje po `textContent` — pierwszy znak wyszukiwania montuje **wszystkie** modele naraz
- Efekt: wielosekundowe opóźnienie przy otwarciu comboboxa

## Rozwiązanie

- Filtr programowy (`filterModels` po `name` / `id` / `provider`) przed mountem
- Zawsze `slice(0, RENDER_LIMIT)` — nigdy całego katalogu
- Lekki wiersz w comboboxie (nazwa, tier, cena, provider); pełne karty tylko w przeglądarce modeli ([#015](./2026-07-10--015--openrouter-model-browser.md))
- Bez virtual scroll (slice wystarcza)

## Acceptance criteria

- [x] Otwarcie comboboxa < 300 ms na desktopie
- [x] Wpisanie znaku wyszukiwania nie mountuje 343 kart
- [x] Zachowana funkcjonalność wyboru i skrótu do pełnej przeglądarki
