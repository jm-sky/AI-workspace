import type { RouteRecordRaw } from 'vue-router'

export const TenantRouteNames = {
  onboarding: 'workspace-onboarding',
} as const

export const TenantRoutePaths = {
  onboarding: '/onboarding/workspace',
} as const

export const tenantRoutes: RouteRecordRaw[] = [
  {
    path: TenantRoutePaths.onboarding,
    name: TenantRouteNames.onboarding,
    component: () => import('@/modules/tenants/pages/WorkspaceOnboardingPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'tenants.onboarding.title',
    },
  },
]
