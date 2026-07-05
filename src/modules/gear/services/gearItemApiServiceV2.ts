/**
 * API service for unified gear items (V2)
 *
 * This service communicates with the backend /gear/v2 endpoints.
 * All requests use the unified item model.
 *
 * @module gear/services/v2/api
 */

import { HttpStatusCode, isAxiosError } from 'axios'
import { apiClient } from '@/shared/services/apiClient'
import type {
  IBatchOrderUpdateItem,
  ICreateGearItemV2Dto,
  IGearItemFiltersV2,
  IGearItemServiceV2,
  IGearItemV2,
  IUpdateGearItemV2Dto,
} from '../types/gear.types.v2'
import type { TUUID } from '@/shared/types/base.type'

/**
 * API service implementation for unified gear items (V2)
 */
export const gearItemApiServiceV2: IGearItemServiceV2 = {
  // ===== Create =====

  async createItem(data: ICreateGearItemV2Dto): Promise<IGearItemV2> {
    const response = await apiClient.post<IGearItemV2>('/gear/v2/items', data)
    return response.data
  },

  // ===== Read =====

  async getItems(filters?: IGearItemFiltersV2): Promise<IGearItemV2[]> {
    const params = new URLSearchParams()

    if (filters?.itemType) {
      params.append('itemType', filters.itemType)
    }
    if (filters?.parentItemId !== undefined) {
      // Use 'null' string to indicate filtering for items with no parent (root items)
      // Backend interprets 'null' as IS NULL filter
      params.append('parentItemId', filters.parentItemId === null ? 'null' : filters.parentItemId)
    }
    if (filters?.isPublic !== undefined) {
      params.append('isPublic', String(filters.isPublic))
    }
    if (filters?.favorite !== undefined) {
      params.append('favorite', String(filters.favorite))
    }
    if (filters?.status) {
      params.append('status', filters.status)
    }
    if (filters?.priority) {
      params.append('priority', filters.priority)
    }
    if (filters?.category) {
      params.append('category', filters.category)
    }

    const response = await apiClient.get<IGearItemV2[]>('/gear/v2/items', { params })
    return response.data
  },

  async getItemById(id: TUUID): Promise<IGearItemV2 | undefined> {
    try {
      const response = await apiClient.get<IGearItemV2>(`/gear/v2/items/${id}`)
      return response.data
    } catch (error: unknown) {
      if (isAxiosError(error) && error.response?.status === HttpStatusCode.NotFound) {
        return undefined
      }
      throw error
    }
  },

  async getChildren(parentItemId: TUUID): Promise<IGearItemV2[]> {
    const response = await apiClient.get<IGearItemV2[]>(`/gear/v2/items/${parentItemId}/children`)
    return response.data
  },

  // ===== Update =====

  async updateItem(id: TUUID, data: IUpdateGearItemV2Dto): Promise<IGearItemV2> {
    const response = await apiClient.patch<IGearItemV2>(`/gear/v2/items/${id}`, data)
    return response.data
  },

  async batchUpdateOrder(items: IBatchOrderUpdateItem[]): Promise<IGearItemV2[]> {
    const response = await apiClient.patch<IGearItemV2[]>('/gear/v2/items/batch/order', {
      items,
    })
    return response.data
  },

  async moveItem(itemId: TUUID, targetParentId: TUUID | null): Promise<IGearItemV2> {
    const params = new URLSearchParams()
    if (targetParentId) {
      params.append('targetParentId', targetParentId)
    }

    const response = await apiClient.patch<IGearItemV2>(
      `/gear/v2/items/${itemId}/move`,
      null,
      { params }
    )
    return response.data
  },

  // ===== Delete =====

  async deleteItem(id: TUUID): Promise<void> {
    await apiClient.delete(`/gear/v2/items/${id}`)
  },
}
