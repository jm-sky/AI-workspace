# Issue 006 — pytest: JSONB nie kompiluje się na SQLite (dług test-infra)

**Data:** 2026-07-09
**Status:** `todo`
**Obszar:** backend / test infrastructure

## Objaw

`docker exec ai-workspace-app python -m pytest tests/` — ~125 błędów `ERROR` przy
setupie fixture'ów + 7 `FAILED`. Trace:

```
sqlalchemy.exc.CompileError: (in table 'memory_entries', column 'entry_metadata'):
Compiler <SQLiteTypeCompiler> can't render element of type JSONB
AttributeError: 'SQLiteTypeCompiler' object has no attribute 'visit_JSONB'
```

Dotyczy każdego testu, którego fixture robi `Base.metadata.create_all` na SQLite —
modele używają `postgresql.JSONB` (`memory_entries`, `agent_runs`, `agent_run_steps`,
`ai_*` itd.), a testowy silnik to SQLite in-memory.

## Zakres (ważne)

**To dług wcześniej istniejący**, nie regresja. Potwierdzone na czystym baseline
`683855c` (bez zmian z sesji wieloturowych): `tests/test_main.py` daje te same
dwa `CompileError` errory. Testy nietknięte przez JSONB przechodzą (np.
`tests/modules/test_agent_loop.py` — 3 passed).

## Propozycja naprawy

Zarejestrować kompilację `JSONB` → `JSON` dla dialektu SQLite w `tests/conftest.py`
(lub wspólnym module modeli):

```python
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles

@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"
```

Alternatywa: testy integracyjne uruchamiać na realnym Postgresie (kontener
`ai-workspace-db` już działa) zamiast SQLite — spójne z produkcją, ale wolniejsze.

## Weryfikacja

Po naprawie: `pytest tests/` bez `CompileError`; liczba passed rośnie z 142.

To shared-core-ish (conftest) — rozważyć backport wzorca do rodziny core wg
macierzy w meta-repo `projects/.docs/backport-progress.md`.
