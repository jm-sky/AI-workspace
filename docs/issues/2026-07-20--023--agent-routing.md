# Issue 023 — Agent routing (auto-router + 2–3 agenci)

**Data:** 2026-07-20  
**Status:** `planned`  
**Priorytet:** P0  
**Faza MVP:** 3/5 (dec. #9 — hybryda; auto-router przyspieszony)  
**Wzorzec Kancelarii:** [#069](../../../ai-kancelaria/docs/alfa/issues/2026-069-routing-pattern.md) — u nich to **filtr tooli po intencji** w jednym agencie; u nas cel = **wybór agenta** (prompt + lista tooli)

## Cel

Abstrakcja „wiadomość → agent” z wymiennymi strategiami (dec. #9):

1. **Jawny wybór** użytkownika (UI / `agentKey`) — już częściowo w API.
2. **Auto-router** — wybór agenta na podstawie wiadomości (start: keyword lub lekki LLM; fallback na domyślnego).

Przygotować **2–3 agentów** — każdy z własnym:
- system promptem / personą,
- listą narzędzi (profil),
- opcjonalnie zakresami pamięci / metadanymi routingu.

Przykładowy zestaw na dogfooding (do potwierdzenia):
- `github-workspace` — repo / issues / PR (istnieje),
- `general` / `chat` — rozmowa + memory, bez lub z minimalnymi toolami,
- trzeci kandydat: `gmail` (po Fazie 2) albo wariant „research / docs” jeśli pojawi się wcześniej.

## Stan obecny (Workspace)

- `agent_key` w API; FE hardcoded `github-workspace`.
- Statyczne `AGENT_PROMPTS` + `AGENT_TOOL_PROFILES`.
- Brak UI pickera i auto-routera.

## Stan Kancelarii (po pullu 2026-07)

- ✅ `router.py` — `classify_intent()` keyword-based → `sprawy` | `portal_wiedza` | `combined` | `general`.
- Filtruje **serwery MCP / tooli**, nie osobne obiekty Agent z różnymi promptami.
- `ROUTING_ENABLED=true` domyślnie.

## Zakres (propozycja)

- [ ] Rejestr agentów (min. 2–3) — prompt + tools + opis dla routera
- [ ] Strategia `ExplicitAgentRouter` (z requestu / sesji)
- [ ] Strategia `AutoAgentRouter` (keyword MVP → później LLM)
- [ ] UI: wybór agenta + wskaźnik „auto” / wybranego agenta w sesji
- [ ] Audyt: `agentKey` + powód routingu w trace
- [ ] Spójność z tool search (#022): po wyborze agenta → core tools + profil (+ search)

## Poza zakresem

- Pełny edytor agentów dla adminów (Faza 3 — osobny chunk).
- Sub-agenty równoległe (Kancelaria #072) — osobna decyzja.
