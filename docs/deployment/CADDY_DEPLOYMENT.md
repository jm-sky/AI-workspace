# Caddy — konfiguracja AI Workspace

**Ostatnia aktualizacja:** 2026-07-06

Konfiguracja Caddy dla dwóch domen na `dev-made.it`, wzorowana na gear-stack ([`../gear-stack/docs/deployment/gear-stack.caddy`](../../../gear-stack/docs/deployment/gear-stack.caddy)) i family-recipes.

## Domeny

| Domena | Rola | Backend |
|---|---|---|
| `ai-workspace.dev-made.it` | Frontend SPA (statyczne pliki) | `/api/*` → `localhost:8003` |
| `api.ai-workspace.dev-made.it` | API bezpośrednio | `localhost:8003` |

**DNS:** rekordy A/AAAA dla obu domen wskazują na VPS (`146.59.16.37`). Caddy wystawia certyfikaty TLS automatycznie po wdrożeniu konfiguracji.

Plik konfiguracyjny w repozytorium: [`ai-workspace.caddy`](ai-workspace.caddy)

## Infrastruktura Caddy na serwerze

| Element | Ścieżka |
|---|---|
| Główny config | `/etc/caddy/Caddyfile` → `import sites-enabled/*.caddy` |
| Dostępne vhosty | `/etc/caddy/sites-available/` |
| Włączone vhosty | `/etc/caddy/sites-enabled/` (symlinki) |

## Wdrożenie na serwerze

```bash
# 1. Skopiuj konfigurację (z katalogu projektu)
sudo cp docs/deployment/ai-workspace.caddy /etc/caddy/sites-available/ai-workspace.caddy
sudo chown caddy:caddy /etc/caddy/sites-available/ai-workspace.caddy
sudo chmod 644 /etc/caddy/sites-available/ai-workspace.caddy

# 2. Włącz site (symlink)
sudo ln -sf /etc/caddy/sites-available/ai-workspace.caddy /etc/caddy/sites-enabled/ai-workspace.caddy

# 3. Walidacja i reload
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Główny `Caddyfile` importuje wszystkie pliki z `sites-enabled/*.caddy` — nie trzeba go edytować ręcznie.

## Co zawiera konfiguracja

- **Security headers** — CSP (reCaptcha, Sentry), HSTS, X-Frame-Options, itd.
- **Cache** — długi cache dla hashowanych assetów Vite (`/assets/*`), brak cache dla HTML
- **SPA routing** — `try_files {path} /index.html`
- **Reverse proxy** — `/api/*` na frontendowej domenie + osobna subdomena API
- **TLS** — automatyczny certyfikat Let's Encrypt (`tls jan.madeyski@dev-made.it`)

Nagłówki CSP w backendzie (`backend/app/core/security_headers.py`) powinny być zsynchronizowane z Caddy — `connect-src` obejmuje `https://*.ai-workspace.dev-made.it` (obecnie w kodzie jest jeszcze `gear-stack.ovh` z dziedziczenia — do aktualizacji przy pierwszym deployu produkcyjnym).

## Kolejne kroki po wdrożeniu Caddy

### 1. Katalog deploy frontendu

```bash
sudo mkdir -p /var/www/ai-workspace
sudo chown -R caddy:deploy /var/www/ai-workspace
sudo chmod -R 775 /var/www/ai-workspace
sudo chmod g+s /var/www/ai-workspace
```

### 2. Build i deploy frontendu

```bash
pnpm build
./scripts/frontend_build_deploy.sh
```

> **Uwaga:** skrypt `scripts/frontend_build_deploy.sh` wdraża build do `/var/www/ai-workspace`.

Produkcyjny build powinien używać `.env.production` z `VITE_API_BASE_URL=https://api.ai-workspace.dev-made.it/api` (wzorzec jak gear-stack — API na osobnej subdomenie).

### 3. Zmienne backendu (`backend/.env`)

Po przejściu na domeny produkcyjne ustaw m.in.:

```env
ENVIRONMENT=production
DEBUG=false

CORS_ORIGINS=["https://ai-workspace.dev-made.it","http://localhost:5176"]
ALLOWED_HOSTS=["api.ai-workspace.dev-made.it","ai-workspace.dev-made.it","localhost","127.0.0.1"]

FRONTEND_URL=https://ai-workspace.dev-made.it
WEBAUTHN_RP_ID=ai-workspace.dev-made.it
WEBAUTHN_ORIGIN=https://ai-workspace.dev-made.it
STORAGE_BASE_URL=https://api.ai-workspace.dev-made.it
```

Po zmianie `.env` przeutwórz kontener backendu (sam `restart` nie przeładowuje env):

```bash
cd backend
docker compose -f docker-compose.dev.yml up -d --force-recreate app
```

### 4. Porty projektu (izolacja na VPS)

| Usługa | Kontener | Port hosta |
|---|---|---|
| FastAPI | `ai-workspace-app` | **8003** |
| PostgreSQL | `ai-workspace-db` | **5435** |
| Redis | `ai-workspace-redis` | **6382** |
| Vite dev | — | **5176** |

## Weryfikacja

```bash
# Status Caddy
sudo systemctl status caddy

# API przez Caddy
curl -s https://api.ai-workspace.dev-made.it/health
# Oczekiwane: {"status":"healthy"}

# Nagłówki bezpieczeństwa frontendu
curl -I https://ai-workspace.dev-made.it | grep -E "(Content-Security-Policy|X-Frame-Options|Strict-Transport-Security)"

# Logi
sudo journalctl -u caddy -f
```

## Uwagi

- Frontend docelowo używa `VITE_API_BASE_URL=https://api.ai-workspace.dev-made.it/api` — requesty API idą na subdomenę API, tak jak w gear-stack.
- Blok `handle /api/*` w Caddy jest zapasowy; główna ścieżka to subdomena `api.ai-workspace.dev-made.it`.
- Backend nasłuchuje na `127.0.0.1:8003` (`APP_PORT=8003` w `backend/.env`).
- Frontend serwowany z `/var/www/ai-workspace/` (właściciel: `caddy:deploy`).

## Aktualizacja konfiguracji

1. Edytuj `docs/deployment/ai-workspace.caddy` w repozytorium
2. Skopiuj na serwer (patrz sekcja „Wdrożenie na serwerze”)
3. `sudo caddy validate --config /etc/caddy/Caddyfile`
4. `sudo systemctl reload caddy`

## Referencje

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Content Security Policy Reference](https://content-security-policy.com/)
- gear-stack: [`../../../gear-stack/docs/deployment/CADDY_DEPLOYMENT.md`](../../../gear-stack/docs/deployment/CADDY_DEPLOYMENT.md)
