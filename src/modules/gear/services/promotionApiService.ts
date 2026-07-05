import { apiClient } from '@/shared/services/apiClient'
import type { IGlobalCatalogueItem } from '../types/catalogue.types'
import type { IItemPromotionStatus, IPromoteItemResponse } from '../types/promotion.types'
import type { TUUID } from '@/shared/types/base.type'

/**
 * API service for item promotion to catalogue
 */
class PromotionApiService {
  /**
   * Promote an item to catalogue
   */
  async promoteItem(itemId: TUUID): Promise<IPromoteItemResponse> {
    const response = await apiClient.post<IPromoteItemResponse>(`/gear/items/${itemId}/promote`)
    return response.data
  }

  /**
   * Get promotion status for an item
   */
  async getPromotionStatus(itemId: TUUID): Promise<IItemPromotionStatus> {
    const response = await apiClient.get<IItemPromotionStatus>(`/gear/items/${itemId}/promotion-status`)
    return response.data
  }

  /**
   * Add item to catalogue (admin only - bypasses threshold)
   */
  async addToCatalogue(itemId: TUUID): Promise<IGlobalCatalogueItem> {
    const response = await apiClient.post<IGlobalCatalogueItem>(`/gear/items/${itemId}/add-to-catalogue`)
    return response.data
  }
}

export const promotionApiService = new PromotionApiService()

