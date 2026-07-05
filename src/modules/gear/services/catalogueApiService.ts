import { apiClient } from '@/shared/services/apiClient'
import type {
  ICatalogueItemCreate,
  ICatalogueItemUpdate,
  ICatalogueSearchParams,
  IGlobalCatalogueItem,
} from '../types/catalogue.types'
import type { IGearItem } from '../types/gear.types'
import type { TGearItemPriority, TGearItemStatus } from '../types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Catalogue API Service
 *
 * Provides methods to interact with global catalogue API endpoints.
 * GET endpoints are public (no auth required).
 * POST/PATCH/DELETE endpoints require authentication.
 */
export class CatalogueApiService {
  /**
   * Get catalogue items with optional filters
   * Public endpoint - no auth required
   */
  async getCatalogueItems(params?: ICatalogueSearchParams): Promise<IGlobalCatalogueItem[]> {
    const isActive =
      params?.isActive === undefined
        ? true
        : params.isActive

    const response = await apiClient.get<IGlobalCatalogueItem[]>('/gear/catalogue/items', {
      params: {
        query: params?.query,
        category: params?.category,
        brand: params?.brand,
        priceTier: params?.priceTier,
        quality: params?.quality,
        // Important: allow `null` to mean "no filter" (show all)
        isActive,
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
      },
    })
    return response.data
  }

  /**
   * Get a single catalogue item by ID
   * Public endpoint - no auth required
   */
  async getCatalogueItem(itemId: TUUID): Promise<IGlobalCatalogueItem> {
    const response = await apiClient.get<IGlobalCatalogueItem>(`/gear/catalogue/items/${itemId}`)
    return response.data
  }

  /**
   * Create a new catalogue item
   * Requires authentication
   */
  async createCatalogueItem(data: ICatalogueItemCreate): Promise<IGlobalCatalogueItem> {
    const response = await apiClient.post<IGlobalCatalogueItem>('/gear/catalogue/items', data)
    return response.data
  }

  /**
   * Update a catalogue item
   * Requires authentication - only creator or admin can update
   */
  async updateCatalogueItem(itemId: TUUID, data: ICatalogueItemUpdate): Promise<IGlobalCatalogueItem> {
    const response = await apiClient.patch<IGlobalCatalogueItem>(`/gear/catalogue/items/${itemId}`, data)
    return response.data
  }

  /**
   * Delete a catalogue item (soft delete)
   * Requires authentication - only creator or admin can delete
   */
  async deleteCatalogueItem(itemId: TUUID): Promise<void> {
    await apiClient.delete(`/gear/catalogue/items/${itemId}`)
  }

  /**
   * Add a catalogue item to a container
   * Creates a new item in the container based on catalogue item data
   * Requires authentication
   */
  async addCatalogueItemToContainer(
    containerId: TUUID,
    catalogueItemId: TUUID,
    options?: {
      quantity?: number
      status?: TGearItemStatus
      priority?: TGearItemPriority
      copyImage?: boolean
    },
  ): Promise<IGearItem> {
    const response = await apiClient.post<IGearItem>(
      `/gear/containers/${containerId}/items/from-catalogue/${catalogueItemId}`,
      null,
      {
        params: {
          quantity: options?.quantity ?? 1,
          status: options?.status ?? 'owned',
          priority: options?.priority ?? 'medium',
          copy_image: options?.copyImage ?? false,
        },
      },
    )
    return response.data
  }

  /**
   * Link an item to a catalogue item (set catalogue_item_id)
   * Requires authentication
   */
  async linkItemToCatalogue(itemId: TUUID, catalogueItemId: TUUID): Promise<IGearItem> {
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}/link-to-catalogue/${catalogueItemId}`)
    return response.data
  }

  /**
   * Update an item with data from its linked catalogue item
   * Updates only specified fields from catalogue while preserving user-specific fields
   * Requires authentication
   */
  async updateItemFromCatalogue(
    itemId: TUUID,
    fields?: string[],
  ): Promise<IGearItem> {
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}/update-from-catalogue`, null, {
      params: fields ? { fields: fields.join(',') } : undefined,
    })
    return response.data
  }

  /**
   * Unlink an item from the catalogue
   * Clears the catalogueItemId reference
   * Requires authentication
   */
  async unlinkItemFromCatalogue(itemId: TUUID): Promise<IGearItem> {
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}/unlink-from-catalogue`)
    return response.data
  }

  /**
   * Fetch images from catalogue item and attach them to the gear item
   * Requires authentication
   */
  async fetchImagesFromCatalogue(itemId: TUUID): Promise<IGearItem> {
    const response = await apiClient.post<IGearItem>(`/gear/items/${itemId}/fetch-images-from-catalogue`)
    return response.data
  }
}

// Export singleton instance
export const catalogueApiService = new CatalogueApiService()
