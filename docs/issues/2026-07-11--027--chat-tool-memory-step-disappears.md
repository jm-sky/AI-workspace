# Chat — krok narzędzia (memory) znika po zakończeniu runu

**Status:** `todo`  
**Created:** 2026-07-11  
**Obszar:** frontend (`workspace` / chat), ewentualnie synchronizacja historii z backendem  
**Powiązane:** [#018](./2026-07-09--018--design-faza-1-5-tool-steps.md) (inline tool steps)

## Problem

Po użyciu narzędzia **memory** krok narzędzia jest **widoczny przez chwilę** w wątku czatu (podczas streamingu / trwającego runu), a po zakończeniu odpowiedzi **znika** — zostaje tylko końcowa wiadomość asystenta (LLM).

Oczekiwane zachowanie (zgodnie z Fazą 1.5 / issue 018): kroki narzędzi pozostają w historii wątku, tak jak podczas streamingu.

## Kroki reprodukcji

1. Uruchom czat z agentem mającym dostęp do narzędzia memory.
2. Wywołaj akcję wymuszającą użycie memory (np. zapis / odczyt pamięci).
3. Obserwuj wątek podczas streamingu — krok memory jest widoczny.
4. Po zakończeniu runu krok znika; widoczna jest wyłącznie odpowiedź LLM.

## Hipotezy (do weryfikacji)

- Frontend nadpisuje / filtruje wiadomości po `run.completed` lub po refetch historii sesji.
- Backend nie utrwala kroków tool w historii wiadomości (tylko SSE na żywo).
- Mapowanie typów wiadomości (tool step vs assistant) gubi wpisy przy merge stanu lokalnego z API.

## Zakres naprawy

- [ ] Utrwalić kroki narzędzi (w tym memory) w historii czatu po zakończeniu runu.
- [ ] Spójność: to samo zachowanie po odświeżeniu strony / ponownym wejściu w sesję.
- [ ] Test regresji dla innych narzędzi (nie tylko memory), jeśli problem jest wspólny.

## Weryfikacja

- Run z memory → krok pozostaje w wątku po zakończeniu odpowiedzi.
- Odświeżenie strony → krok nadal widoczny w historii sesji.
