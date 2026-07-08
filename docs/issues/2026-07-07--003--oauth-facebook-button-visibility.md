# OAuth Facebook — widoczność przycisku niezależnie od Google

**Status:** `done`  
**Created:** 2026-07-07  
**Moduł:** `auth` (shared core)  
**Source:** [gear-stack #013](../../gear-stack/docs/issues/2026-07-07--013--oauth-facebook-button-visibility.md)

## Problem

`OAuthFacebookButton` jest pokazywany gdy włączony jest Google OAuth, bez sprawdzenia `config.oauth.facebook.enabled`.

Dotyczy `LoginForm.vue` i `RegisterForm.vue`.

## Oczekiwane zachowanie

Każdy provider widoczny tylko przy własnej konfiguracji; sekcja OAuth gdy włączony jest którykolwiek provider.

## Zakres

- [x] Backport wzorca z gear-stack / zbory-chwz `LoginForm.vue`
- [x] `LoginForm.vue`, `RegisterForm.vue`

## Weryfikacja

Tylko Google / tylko Facebook / oba / żaden — poprawna widoczność przycisków na login i register.
