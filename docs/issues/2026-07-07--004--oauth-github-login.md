# OAuth GitHub — logowanie (źródło backportu)

**Status:** `done`  
**Created:** 2026-07-07  
**Moduł:** `auth` (shared core)

## Opis

Pierwsza implementacja logowania przez GitHub OAuth w rodzinie core. Backport do pozostałych projektów: [gear-stack #014](../../gear-stack/docs/issues/2026-07-07--014--oauth-github-login.md).

## Zakres (ai-workspace)

- `GitHubOAuthProvider` w `backend/app/core/oauth.py` (login, callback `/auth/github`)
- Integracje GitHub App — osobny flow (`GITHUB_INTEGRATION_OAUTH_*`) — tylko w ai-workspace
- `OAuthGitHubButton`, `useOAuth.ts`, trasa `fixedOAuthProvider: 'github'`

## Backporty

| Projekt | Issue |
|---------|-------|
| gear-stack | [014](../../gear-stack/docs/issues/2026-07-07--014--oauth-github-login.md) |
| family-recipes | [004](../../family-recipes/docs/issues/2026-07-07--004--oauth-github-login.md) |
| ops-monitor | [006](../../ops-monitor/docs/issues/2026-07-07--006--oauth-github-login.md) |
| zbory-chwz | [004](../../zbory-chwz/docs/issues/2026-07-07--004--oauth-github-login.md) |
