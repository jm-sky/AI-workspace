import type { RouteRecordRaw } from 'vue-router'

export const SettingsRoutePaths = {
  settings: import.meta.env.VITE_SETTINGS_PATH ?? '/settings',
  integrationsOAuthCallback:
    import.meta.env.VITE_INTEGRATIONS_OAUTH_CALLBACK_PATH
    ?? '/settings/integrations/callback/:provider',
} as const

export const SettingsRouteNames = {
  settings: 'settings',
  integrationsOAuthCallback: 'integrations-oauth-callback',
} as const

export const settingsRoutes: RouteRecordRaw[] = [
  {
    path: SettingsRoutePaths.settings,
    name: SettingsRouteNames.settings,
    component: () => import('@/pages/settings/SettingsPage.vue'),
    meta: { title: 'settings.page.title' },
  },
  {
    path: SettingsRoutePaths.integrationsOAuthCallback,
    name: SettingsRouteNames.integrationsOAuthCallback,
    component: () => import('@/modules/settings/pages/IntegrationOAuthCallbackPage.vue'),
    meta: { title: 'settings.integrations.callback.processing_title', requiresAuth: true },
  },
]
