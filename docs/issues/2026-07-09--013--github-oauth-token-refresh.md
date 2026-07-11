# Issue 013 — GitHub OAuth — odświeżanie wygasłego tokena

**Data:** 2026-07-09  
**Status:** `done` (2026-07-09)  
**Obszar:** backend (`integrations`) + frontend (`workspace`)

## Prompt (Claude Code)

> Refresh token for Github integration  
> Token for 'github' expired — re-authenticate (provider refresh not yet implemented)

## Decyzja

Integracja GitHub ma **automatycznie odświeżać** token OAuth zamiast wymuszać pełną re-autoryzację przy każdym wygaśnięciu. Użytkownik widzi komunikat tylko gdy refresh się nie powiedzie (revoked scope, wygasły refresh token).

## Implementacja

- Commit `b5be254` — `feat(integrations): implement GitHub OAuth token refresh`
- Backend: refresh flow w providerze GitHub
- Frontend: obsługa stanu „token wygasł” z próbą silent refresh

## Weryfikacja

- Wygasły access token → automatyczny refresh → MCP/GitHub działa bez ponownego logowania
- Refresh niemożliwy → czytelny komunikat z CTA do re-auth
