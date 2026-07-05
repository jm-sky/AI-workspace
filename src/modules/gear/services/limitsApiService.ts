import { apiClient } from '@/shared/services/apiClient'
import type { IUserLimits } from '../types/limits.types'

/**
 * Limits API Service
 *
 * Provides methods to interact with account limits API endpoints.
 * All methods require authentication (token is added automatically via interceptor).
 */
class LimitsApiService {
  /**
   * Get user account limits and current usage
   */
  async getUserLimits(): Promise<IUserLimits> {
    const response = await apiClient.get<IUserLimits>('/gear/me/limits')
    return response.data
  }
}

export const limitsApiService = new LimitsApiService()

