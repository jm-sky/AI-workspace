# Issue 016 — Model picker — wydajność otwarcia (lazy load)

**Data:** 2026-07-10  
**Status:** `in progress`  
**Obszar:** frontend (`workspace`)

## Prompt (Claude Code)

> Model picker - need optimization, open takes ages. Maybe virtual scroll, lazy load.

## Problem

`WorkspaceModelComboBox.vue` nad katalogiem **343 modeli** OpenRouter:

- Przy otwarciu montuje 50 ciężkich `CommandItem` + `WorkspaceModelCard` (~20 węzłów DOM każdy)
- shadcn `Command` filtruje po `textContent` — pierwszy znak wyszukiwania montuje **wszystkie** modele naraz
- Efekt: wielosekundowe opóźnienie przy otwarciu comboboxa

## Decyzja (planowana)

- **Własna lista** zamiast shadcn Command dla dużych katalogów (lub `Listbox` reka-ui z programowym filtrem)
- **Lazy mount** kart — tylko widoczny viewport (virtual scroll lub slice + IntersectionObserver)
- **Lekki wiersz** w comboboxie, pełna karta dopiero w przeglądarce modeli ([#015](./2026-07-10--015--openrouter-model-browser.md))
- Filtrowanie po polach modelu (`name`, `id`), nie po DOM

## Stan

Sesja Claude Code `fe1af5bf` (2026-07-10) — analiza root cause, subagent; **brak commita** na moment tworzenia tego issue.

## Acceptance criteria

- [ ] Otwarcie comboboxa < 300 ms na desktopie
- [ ] Wpisanie znaku wyszukiwania nie mountuje 343 kart
- [ ] Zachowana funkcjonalność wyboru i skrótu do pełnej przeglądarki
