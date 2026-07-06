# CLI `users list` — flaga `--wide` (jak ops-monitor)

**Status:** `done`  
**Created:** 2026-07-06  
**Source:** [ops-monitor/backend/cli/commands/users.py](../../../ops-monitor/backend/cli/commands/users.py) (`users list`)  
**Backport:** [backport-progress.md](../../../backport-progress.md)

## Problem

`./exec.sh users list` nie ma `--wide` / interaktywnych promptów dla `detailed` i `wide` — identyczny stan jak gear-stack (kopia bez ulepszeń z ops-monitor).

## Oczekiwane zachowanie

Jak ops-monitor:

- `--wide/--no-wide/-w` — pełne ID i email bez obcinania
- `--detailed/--no-detailed` z `typer.confirm` gdy brak `--json`
- `--json` pomija prompty

## Zakres

- [x] `backend/cli/commands/users.py` — backport komendy `list` z ops-monitor

## Weryfikacja

```bash
./exec.sh users list --wide --detailed
./exec.sh users list --json
```
