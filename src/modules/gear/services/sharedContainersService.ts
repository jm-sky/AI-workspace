/**
 * Shared Containers API Service
 *
 * Provides methods to interact with shared container API endpoints.
 * Shared containers are accessed via tokens, allowing read-only access to non-public containers.
 */

import { apiClient } from '@/shared/services/apiClient'
import type { IGearContainer } from '../types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

export interface IShareToken {
  token: string
  containerId: TUUID
  expiresAt: string | null
  createdAt: string
  shareUrl: string
}

export interface IShareTokenCreate {
  expiresAt?: string | null
}

class SharedContainersApiService {
  /**
   * Get a shared container by token
   * @param token - Share token
   * @returns Shared container
   */
  async getSharedContainer(token: string): Promise<IGearContainer> {
    const response = await apiClient.get<IGearContainer>(`/gear/shared/containers/${token}`)
    return response.data
  }

  /**
   * Get all share tokens for a container
   * @param containerId - Container ID
   * @returns List of share tokens
   */
  async getShareTokens(containerId: TUUID): Promise<IShareToken[]> {
    const response = await apiClient.get<IShareToken[]>(`/gear/containers/${containerId}/share-tokens`)
    return response.data
  }

  /**
   * Create a share token for a container
   * @param containerId - Container ID
   * @param data - Share token creation data
   * @returns Created share token
   */
  async createShareToken(containerId: TUUID, data: IShareTokenCreate = {}): Promise<IShareToken> {
    const response = await apiClient.post<IShareToken>(`/gear/containers/${containerId}/share-tokens`, data)
    return response.data
  }

  /**
   * Revoke a share token
   * @param containerId - Container ID
   * @param token - Share token to revoke
   */
  async revokeShareToken(containerId: TUUID, token: string): Promise<void> {
    await apiClient.delete(`/gear/containers/${containerId}/share-tokens/${token}`)
  }
}

export const sharedContainersService = new SharedContainersApiService()
