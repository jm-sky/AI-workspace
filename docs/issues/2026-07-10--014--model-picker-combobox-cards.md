# Issue 014 — Model picker — combobox z kartami (moc, cena, sortowanie)

**Data:** 2026-07-10  
**Status:** `done` (2026-07-10)  
**Commit:** `0fe73fe`  
**Obszar:** frontend (`workspace`)  
**Z tego samego promptu:** [#015](./2026-07-10--015--openrouter-model-browser.md), [#016](./2026-07-10--016--model-picker-performance.md)

## Prompt (Claude Code)

> Jak skonczyles - commit, push.  
> Potem: model picker poprosze lepszy: combobox z wyszukiwarka. Modele jako cards z info o mocy i cenie + ewentualnie features. Sortowanie. Dodajmy kilka modeli do wyboru Claude Haiku, Opus, i pare popularnych.

## Decyzja

Płaski `<select>` zastępujemy **comboboxem** z wyszukiwarką i kartami modeli:

- **Tier** (frontier / balanced / fast) jako proxy „mocy”
- **Cena** — blended per 1M tokenów (input+output)
- **Features** — vision, tools (ikony na karcie)
- **Sortowanie** — recommended, power, price, context, name
- **Kuratela** — popularne modele (Claude Haiku/Opus, Qwen itd.) na początku listy

Katalog początkowo statyczny (`models_config`); live OpenRouter → [#015](./2026-07-10--015--openrouter-model-browser.md).

## Implementacja

- Commit `0fe73fe` — `feat(models): searchable model picker with capability/price cards`
- Komponenty: `WorkspaceModelComboBox.vue`, `WorkspaceModelCard.vue`, `aiModelFormat.ts`

## Weryfikacja

- Combobox otwiera się z wyszukiwarką i kartami
- Sortowanie zmienia kolejność
- Wybrany model widoczny w toolbarze czatu
