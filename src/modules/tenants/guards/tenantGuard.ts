import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useTenantWorkspace } from '@/modules/tenants/composables/useTenantWorkspace'
import { TenantRouteNames } from '@/modules/tenants/config/routes'
import { config } from '@/shared/config/config'
import { hasTenantContext } from '@/shared/utils/jwtDecoder'
import type { NavigationGuardNext, RouteLocationNormalized, Router } from 'vue-router'

export async function tenantGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
): Promise<void> {
  if (!config.backend.enabled) {
    next()
    return
  }

  const requiresTenant = to.matched.some((route) => route.meta.requiresTenant)
  const isOnboarding = to.name === TenantRouteNames.onboarding

  if (!requiresTenant && !isOnboarding) {
    next()
    return
  }

  const authStore = useAuthStore()
  if (!authStore.token) {
    next()
    return
  }

  const redirectTarget = typeof to.query.redirectTo === 'string'
    ? to.query.redirectTo
    : AuthRoutePaths.dashboard

  if (hasTenantContext(authStore.token)) {
    if (isOnboarding) {
      next(redirectTarget)
      return
    }
    next()
    return
  }

  try {
    const { bootstrapTenantContext } = useTenantWorkspace()
    const status = await bootstrapTenantContext()

    if (status === 'ready') {
      if (isOnboarding) {
        next(redirectTarget)
        return
      }
      next()
      return
    }

    if (isOnboarding) {
      next()
      return
    }

    next({
      name: TenantRouteNames.onboarding,
      query: { redirectTo: to.fullPath },
    })
  } catch (error) {
    console.warn('[tenantGuard] Failed to resolve tenant context', error)
    if (isOnboarding) {
      next()
      return
    }
    next({
      name: TenantRouteNames.onboarding,
      query: { redirectTo: to.fullPath },
    })
  }
}

export function protectTenantRoutes(router: Router): void {
  router.beforeEach(tenantGuard)
}
