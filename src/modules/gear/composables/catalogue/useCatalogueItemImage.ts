import { useQueryClient } from '@tanstack/vue-query'
import { catalogueItemImageApiService } from '@/modules/gear/services/catalogueItemImageApiService'
import type { ICatalogueItemImage } from '@/modules/gear/types/catalogueItemImage.types'
import type { TUUID } from '@/shared/types/base.type'

export function useCatalogueItemImage() {
  const queryClient = useQueryClient()

  const invalidate = async (catalogueItemId: TUUID) => {
    await queryClient.invalidateQueries({ queryKey: ['catalogue', 'items'] })
    await queryClient.invalidateQueries({ queryKey: ['catalogue', 'item', catalogueItemId] })
  }

  async function uploadImage(catalogueItemId: TUUID, file: File, isPrimary: boolean = false): Promise<ICatalogueItemImage> {
    const image = await catalogueItemImageApiService.uploadImage(catalogueItemId, file, isPrimary)
    await invalidate(catalogueItemId)
    return image
  }

  async function uploadImageFromUrl(
    catalogueItemId: TUUID,
    url: string,
    isPrimary: boolean = false,
    hostLocally: boolean = true,
  ): Promise<ICatalogueItemImage> {
    const image = await catalogueItemImageApiService.uploadImageFromUrl(catalogueItemId, url, isPrimary, hostLocally)
    await invalidate(catalogueItemId)
    return image
  }

  async function deleteImage(catalogueItemId: TUUID, imageId: TUUID): Promise<void> {
    await catalogueItemImageApiService.deleteImage(imageId)
    await invalidate(catalogueItemId)
  }

  async function togglePrimaryImage(catalogueItemId: TUUID, imageId: TUUID): Promise<boolean> {
    const isPrimary = await catalogueItemImageApiService.togglePrimaryImage(catalogueItemId, imageId)
    await invalidate(catalogueItemId)
    return isPrimary
  }

  async function reorderImages(catalogueItemId: TUUID, imageOrders: Array<{ id: TUUID; order: number }>): Promise<void> {
    await catalogueItemImageApiService.reorderImages(catalogueItemId, imageOrders)
    await invalidate(catalogueItemId)
  }

  return {
    uploadImage,
    uploadImageFromUrl,
    deleteImage,
    togglePrimaryImage,
    reorderImages,
  }
}

