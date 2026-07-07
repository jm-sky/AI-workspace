import type { RouteRecordRaw } from 'vue-router'

export const SettingsRoutePaths = {
  settings: import.meta.env.VITE_SETTINGS_PATH ?? '/settings',
  account: `${import.meta.env.VITE_SETTINGS_PATH ?? '/settings'}/account`,
  security: `${import.meta.env.VITE_SETTINGS_PATH ?? '/settings'}/security`,
  connections: `${import.meta.env.VITE_SETTINGS_PATH ?? '/settings'}/connections`,
  storage: `${import.meta.env.VITE_SETTINGS_PATH ?? '/settings'}/storage`,
  integrationsOAuthCallback:
    import.meta.env.VITE_INTEGRATIONS_OAUTH_CALLBACK_PATH
    ?? '/settings/integrations/callback/:provider',
} as const

export const SettingsRouteNames = {
  settings: 'settings',
  account: 'settings-account',
  security: 'settings-security',
  connections: 'settings-connections',
  storage: 'settings-storage',
  integrationsOAuthCallback: 'integrations-oauth-callback',
} as const

export const settingsRoutes: RouteRecordRaw[] = [
  {
    path: SettingsRoutePaths.settings,
    component: () => import('@/layouts/SettingsLayout.vue'),
    meta: {
      requiresAuth: true,
      requiresTenant: true,
    },
    children: [
      {
        path: '',
        redirect: { name: SettingsRouteNames.account },
      },
      {
        path: 'account',
        name: SettingsRouteNames.account,
        component: () => import('@/modules/settings/pages/AccountSettingsPage.vue'),
        meta: { title: 'settings.nav.account' },
      },
      {
        path: 'security',
        name: SettingsRouteNames.security,
        component: () => import('@/modules/settings/pages/SecuritySettingsPage.vue'),
        meta: { title: 'settings.nav.security' },
      },
      {
        path: 'connections',
        name: SettingsRouteNames.connections,
        component: () => import('@/modules/settings/pages/ConnectionsSettingsPage.vue'),
        meta: { title: 'settings.nav.connections' },
      },
      {
        path: 'storage',
        name: SettingsRouteNames.storage,
        component: () => import('@/modules/settings/pages/StorageSettingsPage.vue'),
        meta: { title: 'settings.nav.storage' },
      },
    ],
  },
  {
    path: SettingsRoutePaths.integrationsOAuthCallback,
    name: SettingsRouteNames.integrationsOAuthCallback,
    component: () => import('@/modules/settings/pages/IntegrationOAuthCallbackPage.vue'),
    meta: {
      title: 'settings.integrations.callback.processing_title',
      requiresAuth: true,
      requiresTenant: true,
    },
  },
]
