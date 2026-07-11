# Issue 009 — MVP kickoff: sesje wieloturowe + kontekst użytkownika

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Commit:** `ed9f4de`  
**Obszar:** backend (`agent`) + frontend (`workspace`)  
**Plan:** [IMPLEMENTATION_KICKOFF.md](../IMPLEMENTATION_KICKOFF.md)  
**Z tego samego promptu:** [#010](./2026-07-09--010--two-tier-agent-audit.md), [#011](./2026-07-09--011--source-routing-guard.md), [#006](./2026-07-09--006--pytest-jsonb-sqlite-compile-error.md)

## Prompt (Claude Code)

> Zaczynamy implementacje. Zobacz IMPLEMENTATION_KICKOFF.md i jeszcze nowe dokumenty, czy plan jest spojny. Mozesz wspomniec w planie o DESIGN.md, ale to na pozniej. Chcd abys duzo dzis zrobil.

## Decyzja

Czat workspace ma działać jak prawdziwa sesja agenta, nie jednorazowe Q&A:

- **Sesje wieloturowe** — historia wiadomości w ramach `chat_session`, kontynuacja wątku.
- **Kontekst użytkownika** — pamięć i profil wstrzykiwane do system promptu.
- **Katalog narzędzi** — agent widzi dostępne integracje (GitHub itd.) w prompcie.

DESIGN.md (Faza 1.5) świadomie odłożony na później w tej samej sesji — najpierw funkcjonalność core.

## Implementacja

- Commit `ed9f4de` — `feat: multi-turn chat sessions + user context & tool catalog in prompt`
- Backend: pętla agenta, persystencja sesji, rozszerzony system prompt
- Frontend: sidebar historii sesji, wiązanie wiadomości z aktywną sesją

## Weryfikacja

- Nowa sesja → kilka wiadomości → odświeżenie strony zachowuje wątek
- Agent ma kontekst z poprzednich tur w tej samej sesji
