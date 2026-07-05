import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IItemPromotionStatus } from '../../types/promotion.types'
import { promotionApiService } from '../../services/promotionApiService'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Composable for managing item promotion to catalogue
 */
export function useItemPromotion(itemId: Ref<TUUID | undefined>) {
  const { t } = useI18n()
  const queryClient = useQueryClient()
  const { handleError } = useHandleError()

  // Query for promotion status
  const {
    data: promotionStatus,
    isLoading: isStatusLoading,
    refetch: refetchStatus,
  } = useQuery<IItemPromotionStatus>({
    queryKey: ['item-promotion-status', itemId],
    queryFn: () => {
      if (!itemId.value) {
        throw new Error('Item ID is required')
      }
      return promotionApiService.getPromotionStatus(itemId.value)
    },
    enabled: computed(() => !!itemId.value),
  })

  // Mutation for promoting item
  const promoteMutation = useMutation({
    mutationFn: () => {
      if (!itemId.value) {
        throw new Error('Item ID is required')
      }
      return promotionApiService.promoteItem(itemId.value)
    },
    onSuccess: () => {
      toast.success(t('gear.promotion.success'))
      // Invalidate promotion status query
      queryClient.invalidateQueries({ queryKey: ['item-promotion-status', itemId] })
      // Also invalidate item query to get updated promoteCount
      queryClient.invalidateQueries({ queryKey: ['item', itemId.value] })
    },
    onError: (error: unknown) => {
      handleError(error)
    },
  })

  // Mutation for adding item to catalogue (admin)
  const addToCatalogueMutation = useMutation({
    mutationFn: () => {
      if (!itemId.value) {
        throw new Error('Item ID is required')
      }
      return promotionApiService.addToCatalogue(itemId.value)
    },
    onSuccess: async () => {
      toast.success(t('gear.promotion.addedToCatalogue'))
      // Invalidate promotion status and item queries, then refetch
      await queryClient.invalidateQueries({ queryKey: ['item-promotion-status', itemId] })
      await refetchStatus()
      queryClient.invalidateQueries({ queryKey: ['item', itemId.value] })
      queryClient.invalidateQueries({ queryKey: ['catalogue', 'items'] })
    },
    onError: (error: unknown) => {
      handleError(error)
    },
  })

  // Computed properties
  const canPromote = computed(() => promotionStatus.value?.canPromote ?? false)
  const userPromoted = computed(() => promotionStatus.value?.userPromoted ?? false)
  const inCatalogue = computed(() => promotionStatus.value?.inCatalogue ?? false)

  return {
    // Status
    promotionStatus,
    isStatusLoading,
    refetchStatus,
    // Computed
    canPromote,
    userPromoted,
    inCatalogue,
    // Mutations
    promoteItem: promoteMutation.mutate,
    isPromoting: computed(() => promoteMutation.isPending.value),
    addToCatalogue: addToCatalogueMutation.mutate,
    isAddingToCatalogue: computed(() => addToCatalogueMutation.isPending.value),
  }
}

