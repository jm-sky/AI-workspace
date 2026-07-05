import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, ref } from 'vue'
import { catalogueApiService } from '@/modules/gear/services/catalogueApiService'
import type {
  ICatalogueSearchParams,
  IGlobalCatalogueItem,
  IGlobalCatalogueItemCreate,
  IGlobalCatalogueItemUpdate,
} from '@/modules/gear/types/catalogue.types'
import type { IGearItem } from '@/modules/gear/types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

export function useCatalogue(options?: { enableItemsQuery?: boolean }) {
  const queryClient = useQueryClient()

  // Search parameters
  const searchParams = ref<ICatalogueSearchParams>({
    query: null,
    category: null,
    brand: null,
    priceTier: null,
    quality: null,
    isActive: true,
    skip: 0,
    limit: 100,
  })

  // ========== Queries ==========

  const {
    data: catalogueItems,
    isLoading: isLoadingItems,
    error: itemsError,
    refetch: refetchItems,
  } = useQuery({
    queryKey: ['catalogue', 'items', searchParams],
    queryFn: () => catalogueApiService.getCatalogueItems(searchParams.value),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: options?.enableItemsQuery ?? false, // Only fetch when explicitly enabled
  })

  const catalogueItemsArray = computed(() => catalogueItems.value ?? [])

  // Get single catalogue item
  const getCatalogueItem = (itemId: TUUID) => {
    return useQuery({
      queryKey: ['catalogue', 'item', itemId],
      queryFn: () => catalogueApiService.getCatalogueItem(itemId),
      staleTime: 5 * 60 * 1000,
    })
  }

  // ========== Mutations ==========

  // Create catalogue item
  const createCatalogueItemMutation = useMutation({
    mutationFn: (data: IGlobalCatalogueItemCreate) => catalogueApiService.createCatalogueItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['catalogue', 'items'] })
    },
  })

  // Update catalogue item
  const updateCatalogueItemMutation = useMutation({
    mutationFn: ({ itemId, data }: { itemId: TUUID; data: IGlobalCatalogueItemUpdate }) =>
      catalogueApiService.updateCatalogueItem(itemId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['catalogue', 'items'] })
      queryClient.invalidateQueries({ queryKey: ['catalogue', 'item', variables.itemId] })
    },
  })

  // Delete catalogue item (soft delete)
  const deleteCatalogueItemMutation = useMutation({
    mutationFn: (itemId: TUUID) => catalogueApiService.deleteCatalogueItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['catalogue', 'items'] })
    },
  })

  // Add catalogue item to container
  const addToContainerMutation = useMutation({
    mutationFn: ({
      containerId,
      catalogueItemId,
      options,
    }: {
      containerId: TUUID
      catalogueItemId: TUUID
      options?: {
        quantity?: number
        status?: 'owned' | 'missing' | 'toBuy'
        priority?: 'critical' | 'high' | 'medium' | 'low'
        copyImage?: boolean
      }
    }) => catalogueApiService.addCatalogueItemToContainer(containerId, catalogueItemId, options),
    onSuccess: () => {
      // Refresh the V2 gear queries (the pages read from this cache)
      queryClient.invalidateQueries({ queryKey: ['gear'] })
    },
  })

  // Link item to catalogue
  const linkToCatalogueMutation = useMutation({
    mutationFn: ({ itemId, catalogueItemId }: { itemId: TUUID; catalogueItemId: TUUID }) =>
      catalogueApiService.linkItemToCatalogue(itemId, catalogueItemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gear'] })
    },
  })

  // Update item from catalogue
  const updateFromCatalogueMutation = useMutation({
    mutationFn: ({ itemId, fields }: { itemId: TUUID; fields?: string[] }) =>
      catalogueApiService.updateItemFromCatalogue(itemId, fields),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gear'] })
    },
  })

  // Fetch images from catalogue
  const fetchImagesFromCatalogueMutation = useMutation({
    mutationFn: (itemId: TUUID) => catalogueApiService.fetchImagesFromCatalogue(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gear'] })
    },
  })

  // Unlink item from catalogue
  const unlinkFromCatalogueMutation = useMutation({
    mutationFn: (itemId: TUUID) => catalogueApiService.unlinkItemFromCatalogue(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gear'] })
    },
  })

  // ========== Helper Methods ==========

  const updateSearchParams = (params: Partial<ICatalogueSearchParams>) => {
    searchParams.value = { ...searchParams.value, ...params }
  }

  const clearFilters = () => {
    searchParams.value = {
      query: null,
      category: null,
      brand: null,
      priceTier: null,
      quality: null,
      isActive: true,
      skip: 0,
      limit: 100,
    }
  }

  const createCatalogueItem = async (data: IGlobalCatalogueItemCreate): Promise<IGlobalCatalogueItem> => {
    return await createCatalogueItemMutation.mutateAsync(data)
  }

  const updateCatalogueItem = async (
    itemId: TUUID,
    data: IGlobalCatalogueItemUpdate,
  ): Promise<IGlobalCatalogueItem> => {
    return await updateCatalogueItemMutation.mutateAsync({ itemId, data })
  }

  const deleteCatalogueItem = async (itemId: TUUID): Promise<void> => {
    await deleteCatalogueItemMutation.mutateAsync(itemId)
  }

  const addCatalogueItemToContainer = async (
    containerId: TUUID,
    catalogueItemId: TUUID,
    options?: {
      quantity?: number
      status?: 'owned' | 'missing' | 'toBuy'
      priority?: 'critical' | 'high' | 'medium' | 'low'
      copyImage?: boolean
    },
  ): Promise<IGearItem> => {
    return await addToContainerMutation.mutateAsync({ containerId, catalogueItemId, options })
  }

  const linkItemToCatalogue = async (itemId: TUUID, catalogueItemId: TUUID): Promise<IGearItem> => {
    return await linkToCatalogueMutation.mutateAsync({ itemId, catalogueItemId })
  }

  const updateItemFromCatalogue = async (itemId: TUUID, fields?: string[]): Promise<IGearItem> => {
    return await updateFromCatalogueMutation.mutateAsync({ itemId, fields })
  }

  const fetchImagesFromCatalogue = async (itemId: TUUID): Promise<IGearItem> => {
    return await fetchImagesFromCatalogueMutation.mutateAsync(itemId)
  }

  const unlinkItemFromCatalogue = async (itemId: TUUID): Promise<IGearItem> => {
    return await unlinkFromCatalogueMutation.mutateAsync(itemId)
  }

  return {
    // State
    searchParams,
    catalogueItems: catalogueItemsArray,
    isLoadingItems,
    itemsError,

    // Queries
    getCatalogueItem,
    refetchItems,

    // Mutations
    createCatalogueItem,
    updateCatalogueItem,
    deleteCatalogueItem,
    addCatalogueItemToContainer,
    linkItemToCatalogue,
    updateItemFromCatalogue,
    fetchImagesFromCatalogue,
    unlinkItemFromCatalogue,

    // Mutation states
    isCreating: computed(() => createCatalogueItemMutation.isPending.value),
    isUpdating: computed(() => updateCatalogueItemMutation.isPending.value),
    isDeleting: computed(() => deleteCatalogueItemMutation.isPending.value),
    isAddingToContainer: computed(() => addToContainerMutation.isPending.value),
    isLinking: computed(() => linkToCatalogueMutation.isPending.value),
    isUpdatingFromCatalogue: computed(() => updateFromCatalogueMutation.isPending.value),
    isFetchingImages: computed(() => fetchImagesFromCatalogueMutation.isPending.value),
    isUnlinking: computed(() => unlinkFromCatalogueMutation.isPending.value),

    // Helpers
    updateSearchParams,
    clearFilters,
  }
}
