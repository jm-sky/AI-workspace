# Chat UX + podział ustawień (Claude-style)

**Status:** in progress  
**Data:** 2026-07-07

## Cel

Uzupełnienie czatu workspace o wskaźnik „myślenia” (bouncing dots + rotujący tekst), panel audytu (trace, system prompt, metadane sesji), selektor modelu oraz podział ustawień na konto użytkownika i ustawienia produktu workspace.

## Stan obecny

| Element | Stan |
|---------|------|
| Loading podczas SSE | Tylko `animate-pulse` + `workspace.chat.thinking` w `WorkspaceChatPage.vue` |
| Audyt | `AgentRunAudit.vue` zawsze widoczny nad czatem — brak przycisku, brak system prompt, brak tokenów/kosztu |
| Historia sesji | Działa w sidebarze `ChatSidebar.vue` + `SessionHistoryList.vue` |
| Model | Backend obsługuje `model` w `POST /agent/chat/stream`; frontend nigdy nie wysyła `model` |
| Katalog modeli | `GET /workspace/config/effective` + `models_config.py`; `GET /ai/models` nie zamontowany |
| Ustawienia | Jedna strona `SettingsPage.vue` — wszystko na jednym scrollu |
| Nawigacja | UserNav: Profile + Settings + Billing; Chat sidebar → `/settings` |

## Podział ustawień

### Konto użytkownika — `/settings/*`

Layout `SettingsLayout.vue` z lewym sidebar-nav:

| Trasa | Zawartość |
|-------|-----------|
| `/settings` | redirect → `/settings/account` |
| `/settings/account` | `PreferencesSettingsCard` — język, motyw, prywatność |
| `/settings/security` | `SecuritySettingsCard` + `DeleteAccountCard` |
| `/settings/connections` | `OAuthConnectionsCard` + skrót do integracji workspace |
| `/settings/storage` | `StorageUsageCard` |

UserNav: Profile, Account, Security, Connections, Billing, Admin (bez monolitu „Settings”).

### Workspace — `/workspace/settings/*`

Layout `WorkspaceSettingsLayout.vue`:

| Trasa | Zawartość |
|-------|-----------|
| `/workspace/settings` | redirect → `/workspace/settings/models` |
| `/workspace/settings/models` | `WorkspaceModelsSettingsCard` — domyślny model |
| `/workspace/settings/integrations` | `IntegrationConnectionsCard` |

Chat sidebar „Ustawienia” → `/workspace/settings`.

## Chat UX

### 1. Wskaźnik myślenia

- `ChatThinkingIndicator.vue` — 3 bouncing dots + rotujący tekst (Myślę…, Analizuje…, …)
- Override z SSE step: tool_call, tool_result
- `useThinkingStatus.ts`; `isStreaming` vs `isLoadingRun` w `useAgentChat`

### 2. Selektor modelu

- Quick: `WorkspaceModelSelector` w `ChatToolbar.vue`
- Pełna konfiguracja: `/workspace/settings/models`
- `useWorkspaceModels` + mount `GET /ai/models`
- Wire `model` w `streamAgentChat`

### 3. Audyt

- `AgentAuditSheet.vue` — Sheet + Tabs: Trace, System prompt, Sesja
- Przycisk w `ChatToolbar`; usunąć inline `AgentRunAudit` z czatu

## Pliki

**Nowe:** ChatThinkingIndicator, useThinkingStatus, ChatToolbar, WorkspaceModelSelector, AgentAuditSheet, SettingsLayout, strony settings/*, WorkspaceSettingsLayout, workspace settings pages, API serwisy, useWorkspaceModels.

**Modyfikacje:** useAgentChat, WorkspaceChatPage, AgentRunAudit, ChatComposer, routes, ChatSidebar, ChatHeader/UserNav, backend router, i18n.

## Weryfikacja

```bash
pnpm lint && pnpm type-check
docker exec ai-workspace-app python -m pytest tests/ -v -k "phase0 or agent"
```

**Test manualny:** thinking indicator, model selector + settings sync, podział /settings vs /workspace/settings, audyt z system prompt i tokenami.
