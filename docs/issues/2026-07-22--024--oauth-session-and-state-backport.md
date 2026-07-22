# Issue 024 — Backport: OAuth session parity + CSRF state verification

**Data:** 2026-07-22
**Status:** `done`
**Źródło:** gear-stack issues [036](../../../gear-stack/docs/issues/2026-07-21--036--oauth-login-bypasses-session-machinery.md) (OAuth login bypasses session/2FA) + [037](../../../gear-stack/docs/issues/2026-07-21--037--oauth-callback-state-not-verified.md) (OAuth callback `state` never verified server-side)

## Kontekst

W gear-stack naprawiono dwa powiązane problemy bezpieczeństwa w ścieżce OAuth:

1. **036 — session / 2FA parity** — `login_with_oauth` mintował tokeny poza `_issue_login_tokens` (brak `jti`/`tv`/session tracking) i `AuthServiceWith2FA` nie override'ował OAuth, więc konta z 2FA omijały challenge.
2. **037 — CSRF `state`** — backend generował `state`, ale callback go nigdy nie weryfikował (tylko frontend).

AI-workspace już wołał `_issue_login_tokens` w OAuth (wraz z `ensure_personal_workspace` + workspace claims), więc backport 036 to głównie: wydzielenie `_resolve_oauth_user`, override 2FA dla OAuth, oraz jawne `requiresEmailVerification=False`.

## Zmiany

1. **`oauth_state_store.py` (nowy)** — Redis-backed, single-use, TTL'd store dla CSRF `state`, bound do providera.
2. **`auth/router.py`** — `get_oauth_auth_url` → `store_state`; `oauth_callback` → `consume_state` przed exchange (400 przy invalid/expired/replay/mismatch).
3. **`auth/service.py`** — `_resolve_oauth_user` (lookup/link/create + `ensure_personal_workspace`); cienki `login_with_oauth` → resolve → `_issue_login_tokens` → `requiresEmailVerification=False`. Workspace claims nietknięte.
4. **`two_factor/auth_integration.py`** — `_build_two_factor_challenge`; `login_user` refaktor; nowy `login_with_oauth` override (2FA challenge jak password login).
5. **Testy** — `test_oauth_state_store.py`, `test_oauth_2fa_login.py`, `TestLoginWithOAuth` w `test_auth_service.py`.

## Weryfikacja

- Unit: state store (valid / replay / never-issued / provider mismatch), OAuth bez 2FA (tokeny + jti/tv), OAuth z 2FA (challenge, nie tokeny), base `TestLoginWithOAuth`.
- Workspace / tenant claims zachowane przez `_issue_login_tokens` + `ensure_personal_workspace` w `_resolve_oauth_user`.

## Uwaga

Nie dotyczy domeny agent/tenants poza istniejącym wiringiem `tenant_workspace_service` w auth.
