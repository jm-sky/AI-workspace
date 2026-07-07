import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  getTenantIdFromToken,
  getTenantRoleFromToken,
} from '@/shared/utils/jwtDecoder'
import type { ITenant } from '@/modules/tenants/types/tenant'

export const useTenantStore = defineStore('tenant', () => {
  const activeTenant = ref<ITenant | null>(null)
  const availableTenants = ref<ITenant[]>([])

  const activeTenantId = computed(() => activeTenant.value?.id ?? null)
  const activeTenantRole = computed(() => activeTenant.value?.role ?? null)

  const setActiveTenant = (tenant: ITenant | null) => {
    activeTenant.value = tenant
  }

  const setAvailableTenants = (tenants: ITenant[]) => {
    availableTenants.value = tenants
  }

  const syncFromToken = (token: string | null) => {
    if (!token) {
      activeTenant.value = null
      return
    }

    const tenantId = getTenantIdFromToken(token)
    const tenantRole = getTenantRoleFromToken(token)

    if (!tenantId || !tenantRole) {
      activeTenant.value = null
      return
    }

    if (activeTenant.value?.id === tenantId) {
      activeTenant.value = {
        ...activeTenant.value,
        role: tenantRole,
      }
      return
    }

    const fromList = availableTenants.value.find((tenant) => tenant.id === tenantId)
    activeTenant.value = fromList
      ? { ...fromList, role: tenantRole }
      : {
          id: tenantId,
          name: tenantId,
          role: tenantRole,
          createdAt: new Date().toISOString(),
        }
  }

  const clear = () => {
    activeTenant.value = null
    availableTenants.value = []
  }

  return {
    activeTenant,
    availableTenants,
    activeTenantId,
    activeTenantRole,
    setActiveTenant,
    setAvailableTenants,
    syncFromToken,
    clear,
  }
})
