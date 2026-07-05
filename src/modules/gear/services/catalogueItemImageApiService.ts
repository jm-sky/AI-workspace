import { apiClient } from '@/shared/services/apiClient'
import type { ICatalogueItemImage, IImageOrderUpdate } from '@/modules/gear/types/catalogueItemImage.types'
import type { TUUID } from '@/shared/types/base.type'

class CatalogueItemImageApiService {
  async uploadImage(catalogueItemId: TUUID, file: File, isPrimary: boolean = false): Promise<ICatalogueItemImage> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<ICatalogueItemImage>(
      `/gear/catalogue/items/${catalogueItemId}/images`,
      formData,
      {
        params: { is_primary: isPrimary },
        headers: { 'Content-Type': 'multipart/form-data' },
      },
    )

    return response.data
  }

  async uploadImageFromUrl(
    catalogueItemId: TUUID,
    url: string,
    isPrimary: boolean = false,
    hostLocally: boolean = true,
  ): Promise<ICatalogueItemImage> {
    const response = await apiClient.post<ICatalogueItemImage>(`/gear/catalogue/items/${catalogueItemId}/images/from-url`, {
      url,
      isPrimary,
      hostLocally,
    })
    return response.data
  }

  async getImages(catalogueItemId: TUUID): Promise<ICatalogueItemImage[]> {
    const response = await apiClient.get<ICatalogueItemImage[]>(`/gear/catalogue/items/${catalogueItemId}/images`)
    return response.data
  }

  async deleteImage(imageId: TUUID): Promise<void> {
    await apiClient.delete(`/gear/catalogue/items/images/${imageId}`)
  }

  async reorderImages(catalogueItemId: TUUID, imageOrders: IImageOrderUpdate[]): Promise<void> {
    await apiClient.put(`/gear/catalogue/items/${catalogueItemId}/images/reorder`, { imageOrders })
  }

  async togglePrimaryImage(catalogueItemId: TUUID, imageId: TUUID): Promise<boolean> {
    const response = await apiClient.put<{ is_primary: boolean }>(
      `/gear/catalogue/items/${catalogueItemId}/images/${imageId}/primary`,
    )
    return response.data.is_primary
  }
}

export const catalogueItemImageApiService = new CatalogueItemImageApiService()

