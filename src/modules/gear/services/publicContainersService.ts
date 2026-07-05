import { apiClient } from '@/shared/services/apiClient'
import type { IGearContainer } from '../types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Public Containers API Service
 *
 * Provides methods to interact with public container API endpoints.
 * These endpoints do not require authentication.
 */
class PublicContainersApiService {
  /**
   * Get all public containers
   */
  async getPublicContainers(): Promise<IGearContainer[]> {
    const response = await apiClient.get<IGearContainer[]>('/gear/public/containers')
    return response.data
  }

  /**
   * Get a single public container by ID
   */
  async getPublicContainer(id: TUUID): Promise<IGearContainer> {
    const response = await apiClient.get<IGearContainer>(`/gear/public/containers/${id}`)
    return response.data
  }
}

export const publicContainersService = new PublicContainersApiService()

