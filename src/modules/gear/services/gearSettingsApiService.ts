import { apiClient } from '@/shared/services/apiClient'
import type {
  IGearSettings,
  IUpdateGearSettingsDto,
} from '../types/gearSettings.types'

/**
 * Gear Settings API Service
 *
 * Provides methods to interact with gear settings API endpoints.
 * All methods require authentication (token is added automatically via interceptor).
 */
class GearSettingsApiService {
  /**
   * Get gear settings for the authenticated user
   */
  async getSettings(): Promise<IGearSettings> {
    const response = await apiClient.get<IGearSettings>('/me/gear-settings')
    return response.data
  }

  /**
   * Update gear settings for the authenticated user
   */
  async updateSettings(updates: IUpdateGearSettingsDto): Promise<IGearSettings> {
    const response = await apiClient.patch<IGearSettings>('/me/gear-settings', updates)
    return response.data
  }
}

export const gearSettingsApiService = new GearSettingsApiService()

