import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '../types/gear.types.v2'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import {
  calculateReadinessPercentageSyncV2,
  calculateTotalWeightSyncV2,
} from '../utils/containerCalculationsV2'
import { useGearV2 } from './useGearV2'
import type { TUUID } from '@/shared/types/base.type'

/**
 * V2 Composable for working with a single container
 *
 * Provides reactive access to container data and calculations.
 * Automatically retrieves container ID from route params if not provided.
 *
 * Usage:
 * ```ts
 * const { container, totalWeight, readinessPercentage, update, remove } = useContainerV2()
 * ```
 */
export function useContainerV2(containerId?: TUUID) {
  const route = useRoute()
  const store = useGearStoreV2()
  const { updateItem, deleteItem } = useGearV2()

  // Get ID from route if not provided
  const id = computed<TUUID>(() => containerId ?? (route.params.id as string))

  // Container data - use store directly for synchronous access in computed
  const container = computed<IGearItemV2 | undefined>(() => {
    const item = store.getItemById(id.value)
    // Verify it's actually a container
    if (item && item.itemType !== 'container') return undefined
    return item
  })

  // Computed properties - use sync helpers for computed
  const totalWeight = computed<number>(() => {
    if (!container.value) return 0
    return calculateTotalWeightSyncV2(container.value.id, store.getItemById, store.getChildrenOfItem)
  })

  const readinessPercentage = computed<number>(() => {
    if (!container.value) return 0
    return calculateReadinessPercentageSyncV2(container.value.id, store.getItemById, store.getChildrenOfItem)
  })

  const itemsCount = computed<number>(() => {
    if (!container.value) return 0
    const children = store.getChildrenOfItem(container.value.id)
    return children.filter(child => child.itemType === 'item').length
  })

  // Actions
  const update = async (data: IUpdateGearItemV2Dto): Promise<IGearItemV2 | undefined> => {
    if (!container.value) return undefined
    return await updateItem(container.value.id, data)
  }

  const remove = async (): Promise<void> => {
    if (!container.value) return
    await deleteItem(container.value.id)
  }

  return {
    container,
    totalWeight,
    readinessPercentage,
    itemsCount,
    update,
    remove,
  }
}
