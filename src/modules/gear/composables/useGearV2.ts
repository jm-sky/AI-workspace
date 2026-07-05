/**
 * Unified gear composable (V2)
 *
 * This composable provides a unified interface for working with gear items
 * in the V2 unified model. It handles both API calls and store synchronization.
 *
 * @module gear/composables/v2
 */

import { computed } from 'vue'
import { useBackend } from '@/shared/composables/useBackend'
import type {
  IBatchOrderUpdateItem,
  ICreateGearItemV2Dto,
  IGearItemFiltersV2,
  IGearItemV2,
  IUpdateGearItemV2Dto,
} from '../types/gear.types.v2'
import { gearItemApiServiceV2 } from '../services/gearItemApiServiceV2'
import { gearItemLocalServiceV2 } from '../services/gearItemLocalServiceV2'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import type { TUUID } from '@/shared/types/base.type'

export function useGearV2() {
  const store = useGearStoreV2()
  const { shouldUseAPI } = useBackend()

  // Get active service based on backend availability
  const service = computed(() => {
    return shouldUseAPI.value ? gearItemApiServiceV2 : gearItemLocalServiceV2
  })

  // ===== Computed from store =====

  const items = computed(() => store.getAllItems)
  const containers = computed(() => store.getAllContainers)
  const rootContainers = computed(() => store.getRootContainers)
  const favoriteContainers = computed(() => store.getFavoriteContainers)
  const publicContainers = computed(() => store.getPublicContainers)

  // ===== Create operations =====

  /**
   * Create a new gear item (container or regular item)
   */
  async function createItem(data: ICreateGearItemV2Dto): Promise<IGearItemV2> {
    const item = await service.value.createItem(data)
    store.upsertItem(item)
    return item
  }

  // ===== Read operations =====

  /**
   * Get items with optional filters
   */
  async function getItems(filters?: IGearItemFiltersV2): Promise<IGearItemV2[]> {
    const fetchedItems = await service.value.getItems(filters)
    store.upsertItems(fetchedItems)
    return fetchedItems
  }

  /**
   * Get item by ID
   */
  async function getItemById(id: TUUID): Promise<IGearItemV2 | undefined> {
    // Try store first (O(1))
    let item = store.getItemById(id)
    if (item) return item

    // Fetch from service if not in store
    item = await service.value.getItemById(id)
    if (item) {
      store.upsertItem(item)
    }
    return item
  }

  /**
   * Get children of an item
   */
  async function getChildren(parentItemId: TUUID): Promise<IGearItemV2[]> {
    const children = await service.value.getChildren(parentItemId)
    store.upsertItems(children)
    return children
  }

  /**
   * Get item from store only (no API call)
   */
  function getItemFromStore(id: TUUID): IGearItemV2 | undefined {
    return store.getItemById(id)
  }

  /**
   * Get parent of an item from store
   */
  function getParentFromStore(itemId: TUUID): IGearItemV2 | undefined {
    return store.getParentOfItem(itemId)
  }

  /**
   * Get children of an item from store
   */
  function getChildrenFromStore(parentItemId: TUUID): IGearItemV2[] {
    return store.getChildrenOfItem(parentItemId)
  }

  // ===== Update operations =====

  /**
   * Update an item
   */
  async function updateItem(id: TUUID, data: IUpdateGearItemV2Dto): Promise<IGearItemV2> {
    const updatedItem = await service.value.updateItem(id, data)
    store.upsertItem(updatedItem)
    return updatedItem
  }

  /**
   * Batch update order (for drag-and-drop reordering)
   */
  async function batchUpdateOrder(items: IBatchOrderUpdateItem[]): Promise<IGearItemV2[]> {
    const updatedItems = await service.value.batchUpdateOrder(items)
    store.upsertItems(updatedItems)
    return updatedItems
  }

  /**
   * Move item to a different parent
   */
  async function moveItem(itemId: TUUID, targetParentId: TUUID | null): Promise<IGearItemV2> {
    const updatedItem = await service.value.moveItem(itemId, targetParentId)
    store.upsertItem(updatedItem)
    return updatedItem
  }

  // ===== Delete operations =====

  /**
   * Delete an item (cascade deletes children)
   */
  async function deleteItem(id: TUUID): Promise<void> {
    await service.value.deleteItem(id)
    store.deleteItem(id)
  }

  // ===== Utility functions =====

  /**
   * Refresh all items from service
   */
  async function refreshAll(filters?: IGearItemFiltersV2): Promise<void> {
    const fetchedItems = await service.value.getItems(filters)
    store.setItems(fetchedItems)
  }

  /**
   * Clear all items from store
   */
  function clearAll(): void {
    store.clearAll()
  }

  return {
    // Computed
    items,
    containers,
    rootContainers,
    favoriteContainers,
    publicContainers,

    // Create
    createItem,

    // Read
    getItems,
    getItemById,
    getChildren,
    getItemFromStore,
    getParentFromStore,
    getChildrenFromStore,

    // Update
    updateItem,
    batchUpdateOrder,
    moveItem,

    // Delete
    deleteItem,

    // Utility
    refreshAll,
    clearAll,
  }
}
