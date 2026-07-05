/**
 * V2 composable backing the "copy from an existing item" catalog pickers.
 *
 * Loads the full gear list through the active V2 service (API or localStorage) into the
 * store and exposes the flattened catalog list, excluding the given container.
 */

import { computed, type MaybeRefOrGetter, onMounted, toValue } from 'vue'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { getAllItemsForCatalogV2 } from '../utils/getAllItemsForCatalogV2'
import { useGearV2 } from './useGearV2'
import type { TUUID } from '@/shared/types/base.type'

export function useItemCatalogV2(excludeContainerId?: MaybeRefOrGetter<TUUID | undefined>) {
  const store = useGearStoreV2()
  const { getItems } = useGearV2()

  // Ensure the full gear list is loaded (the form pages only load the current container)
  onMounted(() => {
    getItems().catch(() => {
      // Best-effort; fall back to whatever is already in the store
    })
  })

  const catalogItems = computed<IItemWithContainer[]>(() =>
    getAllItemsForCatalogV2(store.getAllItems, toValue(excludeContainerId)),
  )

  return { catalogItems }
}
