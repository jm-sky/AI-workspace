# CLI `users delete` — soft/hard delete (jak family-recipes)

**Status:** `done`  
**Created:** 2026-07-06  
**Source:** [family-recipes/backend/cli/commands/users.py](../../../family-recipes/backend/cli/commands/users.py) (`users delete`)  
**Backport:** [backport-progress.md](../../../backport-progress.md)

## Problem

CLI robi hard delete przez raw `db.delete(user_db)` zamiast `UserRepository.delete_user` z domyślnym soft delete. Brak flagi `--hard` i komunikatów soft vs hard.

## Oczekiwane zachowanie

Jak family-recipes (bez cleanup domenowego family):

- domyślnie soft delete przez repozytorium
- `--hard` — trwałe usunięcie
- osobne ostrzeżenia i komunikaty sukcesu

## Zakres

- [x] `backend/cli/commands/users.py` — `users delete`, `_delete_user_from_db`
- [x] Użyć `UserRepository.delete_user(soft_delete=not hard)`

## Weryfikacja

```bash
./exec.sh users delete user@example.com
./exec.sh users delete user@example.com --hard --yes
```
