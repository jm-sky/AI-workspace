# Deployment — AI Workspace

Dokumentacja wdrożenia na VPS (OVH) z Caddy jako reverse proxy.

## Pliki

| Plik | Opis |
|---|---|
| [`ai-workspace.caddy`](ai-workspace.caddy) | Konfiguracja vhostów Caddy (źródło prawdy w repo) |
| [`CADDY_DEPLOYMENT.md`](CADDY_DEPLOYMENT.md) | Instrukcja wdrożenia Caddy, DNS, backend `.env`, weryfikacja |

## Domeny

| Domena | Rola |
|---|---|
| `ai-workspace.dev-made.it` | Frontend SPA |
| `api.ai-workspace.dev-made.it` | FastAPI backend |

DNS skonfigurowany (2026-07-06). Kolejny krok: wdrożenie pliku `.caddy` na serwer i deploy aplikacji — patrz [`CADDY_DEPLOYMENT.md`](CADDY_DEPLOYMENT.md).

## Serwer

- Caddy: `/etc/caddy/` (`sites-available/` + symlinki w `sites-enabled/`)
- Frontend static: `/var/www/ai-workspace/`
- Backend: Docker (`ai-workspace-app`), port hosta **8003**
