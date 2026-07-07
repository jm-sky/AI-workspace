import { apiClient } from '@/shared/services/apiClient'
import type {
  IntegrationAuthUrlResponse,
  IntegrationConnectRequest,
  IntegrationConnection,
  IntegrationOAuthCallbackRequest,
  IntegrationSetup,
} from '@/modules/settings/types/integration'

class IntegrationService {
  async getSetup(): Promise<IntegrationSetup> {
    const response = await apiClient.get<IntegrationSetup>('/integrations/oauth/setup')
    return response.data
  }

  async listConnections(): Promise<IntegrationConnection[]> {
    const response = await apiClient.get<{ connections: IntegrationConnection[] }>(
      '/integrations/oauth/connections',
    )
    return response.data.connections
  }

  async getAuthUrl(payload: IntegrationConnectRequest): Promise<IntegrationAuthUrlResponse> {
    const response = await apiClient.post<IntegrationAuthUrlResponse>(
      '/integrations/oauth/auth-url',
      payload,
    )
    return response.data
  }

  async completeCallback(
    provider: string,
    payload: IntegrationOAuthCallbackRequest,
  ): Promise<IntegrationConnection> {
    const response = await apiClient.post<IntegrationConnection>(
      `/integrations/oauth/callback/${provider}`,
      payload,
    )
    return response.data
  }

  async deleteConnection(connectionId: string): Promise<void> {
    await apiClient.delete(`/integrations/oauth/connections/${connectionId}`)
  }
}

export const integrationService = new IntegrationService()
