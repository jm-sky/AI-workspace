# Issue 007 — Audyt/Trace (sheet) — brak paddingu treści

**Data:** 2026-07-09
**Status:** `todo`
**Obszar:** frontend / workspace / design (Faza 1.5)

## Objaw

W panelu audytu (`AgentAuditSheet.vue`, otwieranym z `ChatToolbar`) treść zakładek
**Trace / System prompt / Sesja** przykleja się do lewej i prawej krawędzi sheeta.
Nagłówek wygląda poprawnie, reszta nie.

## Przyczyna

W shadcn-vue (nowa wersja slotów) `SheetContent` **nie ma własnego paddingu**:

`src/components/ui/sheet/SheetContent.vue:40`
```
'bg-background ... fixed z-50 flex flex-col gap-4 shadow-lg transition ...'
```

Padding wnoszą wyłącznie `SheetHeader` i `SheetFooter` (`p-4` — `SheetHeader.vue:11`,
`SheetFooter.vue:11`). W `AgentAuditSheet.vue:42` root dostaje tylko:

```
class="flex w-full flex-col gap-0 overflow-hidden sm:max-w-lg"
```

Skoro `SheetHeader` jest użyty, a `Tabs`/`TabsList`/`TabsContent` są renderowane
bezpośrednio w `SheetContent`, to tylko nagłówek ma marginesy — `TabsList` i cała
zawartość zakładek dotykają krawędzi.

## Propozycja naprawy

Nie dodawać paddingu do współdzielonego `SheetContent` (to shared core z gear-stack —
zmiana dotknęłaby wszystkich sheetów i wymagałaby backportu). Zamiast tego opaddingować
sekcję Tabs lokalnie w `AgentAuditSheet.vue`:

- `TabsList` → `mx-4 shrink-0` (wyrównanie do `p-4` nagłówka),
- każdy `TabsContent` → `px-4 pb-4` obok istniejących `min-h-0 flex-1 overflow-y-auto pt-4`,
- pusty stan (`workspace.audit.noRun`) → dodać `px-4`.

Alternatywa (mniej inwazyjna wizualnie): jeden wrapper `<div class="flex min-h-0 flex-1
flex-col px-4 pb-4">` wokół `Tabs` — ale wtedy scrollbar `TabsContent` jest wcięty od
krawędzi sheeta, co wygląda gorzej przy długim trace. Preferowany wariant pierwszy
(padding na zawartości, scroll przy krawędzi).

## Weryfikacja

Otworzyć czat → toolbar → Audyt. Sprawdzić wszystkie trzy zakładki:
odstęp treści od krawędzi zgodny z nagłówkiem; scrollbar trace'a przy krawędzi sheeta;
`pre` z system promptem nie dotyka krawędzi.
