# AI Workspace — instrukcje dla agentów (Claude Code / Cursor)

Chat-first platforma agentowa: OpenRouter + własna pętla tool-calling, integracje MCP, multi-tenancy, SSE.

## Źródła prawdy

| Temat | Plik |
|-------|------|
| Indeks dokumentacji | `docs/README.md` |
| Plan MVP, fazy, decyzje 1–17 | `docs/MVP.md` |
| UX/UI (ChatGPT + Linear) | `DESIGN.md` |
| Prompt startowy implementacji | `docs/IMPLEMENTATION_KICKOFF.md` |
| Wdrożenie Caddy (VPS) | `docs/deployment/CADDY_DEPLOYMENT.md` |
| Konwencje kodu | `.cursorrules` |
| Porównanie z ai-kancelaria (co przenieść) | `docs/research/2026-07-08--006--ai-kancelaria-comparison.md` |
| Kontekst serwera (nie commituj) | `CLAUDE.local.md` |

**Nie zmieniaj decyzji architektonicznych z `MVP.md` bez potwierdzenia użytkownika.**

## Stack

- **Frontend:** Vue 3, shadcn-vue, Pinia, TanStack Query — katalog `src/` (root monorepo)
- **Backend:** FastAPI — `backend/`
- **Baza:** PostgreSQL + Docker Compose (`docker-compose.dev.yml` w root repo)
- **AI:** OpenRouter (OpenAI SDK), własna pętla tool-calling; narzędzia w stylu MCP → format OpenAI tools
- **Streaming:** SSE (serwer → klient)

## VPS OVH (ten host)

| Usługa | Kontener | Port hosta |
|--------|----------|-----------|
| FastAPI | `ai-workspace-app` | **8003** |
| PostgreSQL | `ai-workspace-db` | **5435** |
| Redis | `ai-workspace-redis` | **6382** |
| Vite dev | — | **5176** |

**Produkcja (Caddy):** `ai-workspace.dev-made.it` (SPA), `api.ai-workspace.dev-made.it` (API). Frontend: `/var/www/ai-workspace/`.

**CRITICAL:** NIGDY nie uruchamiaj Dockera w katalogu z prefiksem `_` (np. `_ai-workspace-dev`).

```bash
docker compose -f docker-compose.dev.yml up -d
docker exec ai-workspace-app python -m cli db migrate
docker exec ai-workspace-app python -m pytest tests/ -v
```

Frontend dev: `pnpm dev` (port 5176, proxy `/api` → `localhost:8003`).

## Fazy implementacji

| Faza | Zakres | Status |
|------|--------|--------|
| Krok 0 | Bootstrap z gear-stack | ✅ |
| Faza 0 | Tenants, teams, kaskada config, tokeny OAuth integracji | ✅ |
| **Faza 1** | Agent loop + trace, MCP Jira/GitLab, czat SSE, widok 360° | 🔄 w toku |
| Faza 2 | Gmail + Teams MCP | — |
| Faza 3 | Edytor agentów, router, bogate bloki | — |
| Faza 4 | Pamięć + RAG (pgvector) | — |
| Faza 5 | Auto-router, tool search, onboarding tenantów | — |

Scenariusz MVP: issue Jira → pole Klient → fan-out GitLab → widok 360°.

## Moduły backendu (AI Workspace)

| Moduł | Rola |
|-------|------|
| `auth`, `users`, `two_factor` | JWT, WebAuthn, OAuth logowania |
| `tenants`, `teams` | Multi-tenancy M:N, aktywny workspace w JWT |
| `workspace_config` | Kaskada App→Tenant→Team→User |
| `integrations` | Szyfrowany magazyn tokenów OAuth (Jira, GitLab, …) |
| `agent` | Pętla agenta, Task/Run + trace, SSE |
| `ai` | Legacy gear-stack (chat OpenRouter) — do ewolucji / oddzielenia |

## Konwencje

- Importy frontend: alias `@/`
- Bez średników, single quotes, max 3 atrybuty w linii (Vue)
- Checkbox shadcn-vue: `v-model`, nie `v-model:checked`
- FastAPI: `CurrentUser`, `CurrentTenantContext` jako parametry funkcji
- Migracje: `backend/migrations/NNN_slug.py` z `upgrade`/`downgrade`
- ID: `app.common.id_utils.generate_id`
- i18n: `t('module.section.key')`

## Testy i jakość

```bash
pnpm test:run      # frontend (vitest)
pnpm lint && pnpm type-check
docker exec ai-workspace-app python -m pytest tests/ -v
```

## Cherry-pick z gear-stack

```bash
./scripts/rsync-from-gear-stack.sh          # dry-run
./scripts/rsync-from-gear-stack.sh --apply  # sync (bez docs/)
```

Po zmianach shared core: backport do rodziny core według macierzy w meta-repo `projects/.docs/backport-progress.md`.

## Praca z agentem

- Pytaj przed dużymi / nieodwracalnymi działaniami (deploy prod, force push, zmiana decyzji MVP).
- Commituj tylko na prośbę użytkownika.
- Aktualizuj `docs/MVP.md` (otwarte punkty), gdy coś rozstrzygasz.
