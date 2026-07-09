# Issue 008 — Strona Pamięci — brak tła (canvas)

**Data:** 2026-07-09
**Status:** `done` (2026-07-09)
**Obszar:** frontend / workspace / design (Faza 1.5)

## Rozwiązanie (2026-07-09)

`WorkspaceMemoryPage.vue`: lista wpisów dostała canvas czatu
(`rounded-xl border border-hairline bg-surface-canvas` + `divide-hairline`),
a oba boksy sterujące — `rounded-xl border border-hairline bg-surface-raised`
(zamiast `bg-muted/20`, które gasło w dark mode). Nagłówek zostaje na `bg-surface`.

Pozostaje otwarte: `WorkspaceModelsSettingsPage.vue` /
`WorkspaceIntegrationsSettingsPage.vue` renderują gołe karty — do przeglądu osobno.

## Objaw

`/workspace/memory` wygląda „płasko” — treść leży bezpośrednio na tle layoutu,
bez wyodrębnionego panelu, w przeciwieństwie do czatu.

## Przyczyna

`ChatLayout.vue:10` daje `SidebarInset` klasę `bg-surface` (tło aplikacji).
Strony mają wnieść własny **canvas**.

`WorkspaceChatPage.vue:100` robi to poprawnie:
```
class="flex min-h-0 flex-1 flex-col overflow-y-auto rounded-xl border border-hairline bg-surface-canvas"
```

`WorkspaceMemoryPage.vue:77` — root to tylko:
```
class="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden px-4 py-3 sm:px-6"
```

Brak `bg-surface-canvas` / `border-hairline` / `rounded-xl`. Strona pamięci nie
została objęta przebudową tokenów z Fazy 1.5 (commit `d51bf88` wprowadził
`--surface-canvas` i `--hairline`, `src/css/style.css:100-103` oraz `:142-145`).

## Propozycja naprawy

Owinąć zawartość `WorkspaceMemoryPage.vue` w canvas spójny z czatem — nagłówek
strony (ikona `Brain` + tytuł) zostaje na tle `bg-surface`, a lista wpisów +
formularz dodawania trafiają do panelu `rounded-xl border border-hairline
bg-surface-canvas`.

Uwaga: wewnętrzny box formularza używa dziś `bg-muted/20` (`:90`) — na canvasie
trzeba sprawdzić kontrast w dark mode (`--surface-canvas: oklch(0.155 0 0)`),
prawdopodobnie lepiej `bg-surface-raised` lub `bg-muted/40`.

Przy okazji sprawdzić `WorkspaceModelsSettingsPage.vue` i
`WorkspaceIntegrationsSettingsPage.vue` — renderują gołe karty, mogą mieć ten sam brak.

## Weryfikacja

`/workspace/memory` w light i dark mode: panel odcina się od tła jak canvas czatu;
zaokrąglenie i hairline zgodne; formularz czytelny w dark mode.
