/**
 * AI API Service
 * Handles all API calls for AI features
 */

import { apiClient } from '@/shared/services/apiClient'
import type {
  IAiChatRequest,
  IAiChatResponse,
  IAiHistoryDetail,
  IAiHistoryListResponse,
  IAiHistoryQuery,
  IAiModelsResponse,
  IAiSettings,
  IAiSetTokenRequest,
  IAiSetTokenResponse,
  IAiUpdateSettings,
} from '../types'

class AiApiService {
  /**
   * Send chat message to AI
   */
  async chat(request: IAiChatRequest): Promise<IAiChatResponse> {
    const response = await apiClient.post<IAiChatResponse>('/ai/chat', request)
    return response.data
  }

  /**
   * Get available AI models
   */
  async getModels(): Promise<IAiModelsResponse> {
    const response = await apiClient.get<IAiModelsResponse>('/ai/models')
    return response.data
  }

  /**
   * Get AI settings
   */
  async getSettings(forceRefresh = false): Promise<IAiSettings> {
    const url = forceRefresh
      ? `/ai/settings?_t=${Date.now()}`
      : '/ai/settings'
    const response = await apiClient.get<IAiSettings>(url)
    return response.data
  }

  /**
   * Update AI settings
   */
  async updateSettings(updates: IAiUpdateSettings): Promise<IAiSettings> {
    const response = await apiClient.put<IAiSettings>('/ai/settings', updates)
    return response.data
  }

  /**
   * Set API token
   */
  async setApiToken(request: IAiSetTokenRequest): Promise<IAiSetTokenResponse> {
    const response = await apiClient.post<IAiSetTokenResponse>('/ai/settings/token', request)
    return response.data
  }

  /**
   * Remove API token
   */
  async removeApiToken(): Promise<void> {
    await apiClient.delete('/ai/settings/token')
  }

  /**
   * Get AI history list
   */
  async getHistory(query?: IAiHistoryQuery): Promise<IAiHistoryListResponse> {
    const params = new URLSearchParams()
    if (query?.limit) params.append('limit', query.limit.toString())
    if (query?.offset) params.append('offset', query.offset.toString())
    if (query?.operationType) params.append('operation_type', query.operationType)

    const response = await apiClient.get<IAiHistoryListResponse>(
      `/ai/history?${params.toString()}`,
    )
    return response.data
  }

  /**
   * Get AI history detail
   */
  async getHistoryDetail(id: string): Promise<IAiHistoryDetail> {
    const response = await apiClient.get<IAiHistoryDetail>(`/ai/history/${id}`)
    return response.data
  }

  /**
   * Delete AI history item
   */
  async deleteHistoryItem(id: string): Promise<void> {
    await apiClient.delete(`/ai/history/${id}`)
  }

  /**
   * Clear all AI history
   */
  async clearHistory(): Promise<void> {
    await apiClient.delete('/ai/history')
  }
}

export const aiApiService = new AiApiService()

