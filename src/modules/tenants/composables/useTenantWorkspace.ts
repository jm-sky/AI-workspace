import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import {
  createTenant,
  listTenants,
  switchTenant,
} from '@/modules/tenants/services/tenantApiService'
import { useTenantStore } from '@/modules/tenants/store/useTenantStore'
import { hasTenantContext } from '@/shared/utils/jwtDecoder'
import type { ISwitchTenantResponse, ITenant, ITenantCreateRequest } from '@/modules/tenants/types/tenant'

export type TenantBootstrapStatus = 'ready' | 'onboarding'

function applySwitchResponse(response: ISwitchTenantResponse) {
  const authStore = useAuthStore()
  const tenantStore = useTenantStore()

  authStore.setToken(response.accessToken)
  authStore.setRefreshToken(response.refreshToken)
  tenantStore.setActiveTenant(response.tenant)
  tenantStore.syncFromToken(response.accessToken)
}

export function useTenantWorkspace() {
  const authStore = useAuthStore()
  const tenantStore = useTenantStore()

  const bootstrapTenantContext = async (): Promise<TenantBootstrapStatus> => {
    if (!authStore.token) {
      return 'onboarding'
    }

    if (hasTenantContext(authStore.token)) {
      tenantStore.syncFromToken(authStore.token)
      return 'ready'
    }

    const { tenants } = await listTenants()
    tenantStore.setAvailableTenants(tenants)

    if (tenants.length === 1) {
      applySwitchResponse(await switchTenant(tenants[0].id))
      return 'ready'
    }

    if (tenants.length === 0) {
      return 'onboarding'
    }

    return 'onboarding'
  }

  const createWorkspace = async (payload: ITenantCreateRequest): Promise<ITenant> => {
    const response = await createTenant(payload)
    applySwitchResponse(response)
    return response.tenant
  }

  const selectWorkspace = async (tenantId: string): Promise<ITenant> => {
    const response = await switchTenant(tenantId)
    applySwitchResponse(response)
    return response.tenant
  }

  const loadTenants = async (): Promise<ITenant[]> => {
    const { tenants } = await listTenants()
    tenantStore.setAvailableTenants(tenants)
    return tenants
  }

  return {
    activeTenant: tenantStore.activeTenant,
    availableTenants: tenantStore.availableTenants,
    bootstrapTenantContext,
    createWorkspace,
    selectWorkspace,
    loadTenants,
  }
}

export async function resolvePostAuthPath(redirectTo?: string): Promise<string> {
  const { bootstrapTenantContext } = useTenantWorkspace()
  const status = await bootstrapTenantContext()

  if (status === 'onboarding') {
    const query = redirectTo ? `?redirectTo=${encodeURIComponent(redirectTo)}` : ''
    return `/onboarding/workspace${query}`
  }

  return redirectTo ?? '/workspace'
}
