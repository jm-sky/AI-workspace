import { apiClient } from '@/shared/services/apiClient'
import type { IImageOrderUpdate, IItemImage } from '@/modules/gear/types/itemImage.types'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Item Image API Service
 *
 * Provides methods to interact with item image API endpoints.
 * All methods require authentication (token is added automatically via interceptor).
 */
class ItemImageApiService {
  /**
   * Upload image for an item
   *
   * @param itemId - Item ID
   * @param file - Image file to upload
   * @param isPrimary - Whether this should be the primary image
   * @returns Uploaded image metadata
   */
  async uploadImage(itemId: TUUID, file: File, isPrimary: boolean = false): Promise<IItemImage> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_primary', isPrimary.toString())

    const response = await apiClient.post<IItemImage>(`/gear/items/${itemId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  /**
   * Create image for an item from external URL
   *
   * @param itemId - Item ID
   * @param url - External image URL
   * @param isPrimary - Whether this should be the primary image
   * @param hostLocally - If true, download and store image. If false, only save external URL.
   * @returns Created image metadata
   */
  async uploadImageFromUrl(itemId: TUUID, url: string, isPrimary: boolean = false, hostLocally: boolean = true): Promise<IItemImage> {
    const response = await apiClient.post<IItemImage>(`/gear/items/${itemId}/images/from-url`, {
      url,
      isPrimary,
      hostLocally,
    })
    return response.data
  }

  /**
   * Get all images for an item
   *
   * @param itemId - Item ID
   * @returns List of images
   */
  async getImages(itemId: TUUID): Promise<IItemImage[]> {
    const response = await apiClient.get<IItemImage[]>(`/gear/items/${itemId}/images`)
    return response.data
  }

  /**
   * Delete an image
   *
   * @param imageId - Image ID
   * @returns void
   */
  async deleteImage(imageId: TUUID): Promise<void> {
    await apiClient.delete(`/gear/items/images/${imageId}`)
  }

  /**
   * Reorder images for an item
   *
   * @param itemId - Item ID
   * @param imageOrders - Array of {id, order} objects
   * @returns void
   */
  async reorderImages(itemId: TUUID, imageOrders: IImageOrderUpdate[]): Promise<void> {
    await apiClient.put(`/gear/items/${itemId}/images/reorder`, { imageOrders })
  }

  /**
   * Toggle primary status for image (set if not primary, unset if already primary)
   *
   * @param itemId - Item ID
   * @param imageId - Image ID to toggle primary status
   * @returns True if image is now primary, False if it was unset
   */
  async togglePrimaryImage(itemId: TUUID, imageId: TUUID): Promise<boolean> {
    const response = await apiClient.put<{ is_primary: boolean }>(`/gear/items/${itemId}/images/${imageId}/primary`)
    return response.data.is_primary
  }
}

export const itemImageApiService = new ItemImageApiService()
