import { apiClient } from '@/shared/services/apiClient'
import type {
  ISwitchTenantResponse,
  ITenantCreateRequest,
  ITenantListResponse,
} from '@/modules/tenants/types/tenant'

export async function listTenants(): Promise<ITenantListResponse> {
  const response = await apiClient.get<ITenantListResponse>('/tenants')
  return response.data
}

export async function createTenant(payload: ITenantCreateRequest): Promise<ISwitchTenantResponse> {
  const response = await apiClient.post<ISwitchTenantResponse>('/tenants', payload)
  return response.data
}

export async function switchTenant(tenantId: string, teamId?: string | null): Promise<ISwitchTenantResponse> {
  const response = await apiClient.post<ISwitchTenantResponse>('/tenants/switch', {
    tenantId,
    teamId: teamId ?? null,
  })
  return response.data
}
