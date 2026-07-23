# Plan — Design pass UI polish (ChatGPT + soft shadows)

**Data:** 2026-07-14  
**Branch:** `feature/design-pass-ui-polish`  
**Status:** `done`  
**Brief:** [`DESIGN.md`](../../DESIGN.md), refero [`chatgpt/`](../design/refero/chatgpt/), [`linear/`](../design/refero/linear/)

## Cel

Doprowadzić shell czatu (desktop + mobile) do wzorca **ChatGPT** — achromatyczny chrome, płaski canvas rozmowy, ghost sidebar — z **delikatnymi cieniami** i blur na composerze (premium/modern, bez neonu).

## Audyt (przed zmianami)

| Obszar | Stan | Docelowo (ChatGPT + DESIGN.md) |
|--------|------|--------------------------------|
| Tło główne | `bg-surface` = slate-300 (szaro-niebieskie) | Biały canvas `#ffffff` |
| Obszar wiadomości | Dodatkowy box z borderem wewnątrz layoutu | Płaski scroll na canvasie, bez „karty w karcie” |
| Sidebar sesji | Outline buttons, primary border na active | Ghost rows, hover veil `#0000000d` |
| Header | Osobny pasek, logo z scale hover | Minimalny hairline + blur, mniej szumu |
| Composer | shadow-lg — OK kierunek | Wzmocnić tokeny cienia + backdrop blur |
| Mobile | Sidebar sheet OK; composer ucięty przy małej wysokości | Pełna wysokość dvh, sticky composer |
| Dark mode | Linear-style layers — OK | Zachować warstwy + subtelne cienie |

## Zakres implementacji

### 1. Tokeny (`src/css/style.css`)

- Naprawić `--color-surface` (canvas zamiast slate-300).
- Sidebar light: `#f9f9f9` (Sidebar Mist).
- Tokeny cieni: `--shadow-soft`, `--shadow-composer`, `--shadow-sidebar`.
- Hover veil jako utility.

### 2. Shell (`ChatLayout`, `ChatHeader`)

- Canvas tło, subtelny cień sidebara.
- Header: hairline + `backdrop-blur`, bez agresywnego hover logo.

### 3. Czat (`WorkspaceChatPage`, `ChatComposer`, `ChatToolbar`)

- Usunąć wewnętrzny bordered container.
- Empty state: heading 24px/600 + helper copy.
- Composer: spójny token cienia, zaokrąglenie 24px.

### 4. Historia sesji (`SessionHistoryList`)

- Ghost „New chat”, search bez ciężkich obramowań.
- Wiersze sesji bez border; active = subtelne tło.

### 5. Sidebar nav (`sidebarMenuButtonVariants`)

- Achromatyczne hover/active zamiast primary/sky.

## Poza zakresem (follow-up)

- Login/guest layouts (osobny pass).
- Pełna migracja primary z sky na achromatic chrome.
- Model selector w headerze sidebara (jak ChatGPT) — większa zmiana IA.

## Weryfikacja

- [x] Desktop: canvas biały, brak „box in box”, composer unosi się z cieniem.
- [x] Mobile 390px: sidebar sheet, composer widoczny, brak horizontal scroll.
- [x] Dark mode: warstwy czytelne, cienie subtelne.
- [x] `pnpm lint && pnpm type-check`

## Konto testowe (dev)

- Email: `ui-test@example.com`
- Hasło: `UiTestPassword123!`
