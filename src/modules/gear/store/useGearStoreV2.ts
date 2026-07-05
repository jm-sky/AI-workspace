/**
 * Unified gear store (V2) with O(1) lookups
 *
 * This store uses a flat Map structure for optimal performance:
 * - O(1) item lookup by ID (vs O(n*m) in V1)
 * - O(1) parent lookup (vs O(n*m) in V1)
 * - O(1) children lookup via index
 *
 * Key improvements:
 * - No more nested iterations through containers and items
 * - Efficient updates without full array scans
 * - Better memory usage with Map vs nested arrays
 *
 * @module gear/store/v2
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { migrateV1ToV2 } from '../services/v1ToV2Migration'
import { isContainer } from '../types/gear.types.v2'
import type { TUUID } from '@/shared/types/base.type'

const STORAGE_KEY = 'gear-stack:items-v2'

export const useGearStoreV2 = defineStore('gearV2', () => {
  // ===== State =====

  /**
   * Flat map of all items (containers + regular items)
   * Key: item ID
   * Value: item data
   *
   * This replaces the nested containers[].items[] structure
   * for O(1) lookups instead of O(n*m).
   */
  const itemsById = ref<Map<TUUID, IGearItemV2>>(new Map())

  /**
   * Index of items by parent ID
   * Key: parent item ID (or null for root items)
   * Value: array of child item IDs
   *
   * This enables O(1) children lookups without scanning all items.
   */
  const itemsByParentId = ref<Map<TUUID | null, TUUID[]>>(new Map())

  // ===== Computed Getters (O(1)!) =====

  /**
   * Get item by ID (O(1))
   */
  const getItemById = computed(() => (id: TUUID) => {
    return itemsById.value.get(id)
  })

  /**
   * Get parent of an item (O(1))
   */
  const getParentOfItem = computed(() => (itemId: TUUID) => {
    const item = itemsById.value.get(itemId)
    if (!item || !item.parentItemId) return undefined
    return itemsById.value.get(item.parentItemId)
  })

  /**
   * Get children of an item (O(1))
   */
  const getChildrenOfItem = computed(() => (itemId: TUUID) => {
    const childIds = itemsByParentId.value.get(itemId) || []
    return childIds.map(id => itemsById.value.get(id)!).filter(Boolean)
  })

  /**
   * Get all root containers (items with no parent and itemType='container')
   */
  const getRootContainers = computed<IGearItemV2[]>(() => {
    const rootIds = itemsByParentId.value.get(null) || []
    return rootIds
      .map(id => itemsById.value.get(id)!)
      .filter(item => item && isContainer(item))
  })

  /**
   * Get all containers (regardless of parent)
   */
  const getAllContainers = computed<IGearItemV2[]>(() => {
    return Array.from(itemsById.value.values()).filter(item => isContainer(item))
  })

  /**
   * Get all items (regardless of parent)
   */
  const getAllItems = computed<IGearItemV2[]>(() => {
    return Array.from(itemsById.value.values())
  })

  /**
   * Get favorite containers
   */
  const getFavoriteContainers = computed<IGearItemV2[]>(() => {
    return Array.from(itemsById.value.values())
      .filter(item => isContainer(item) && item.favorite === true)
  })

  /**
   * Get public containers
   */
  const getPublicContainers = computed<IGearItemV2[]>(() => {
    return Array.from(itemsById.value.values())
      .filter(item => isContainer(item) && item.isPublic === true)
  })

  // ===== Actions =====

  /**
   * Update indexes after items change
   * Must be called after any mutation to itemsById
   */
  function updateIndexes(): void {
    itemsByParentId.value.clear()

    for (const item of itemsById.value.values()) {
      const parentId = item.parentItemId ?? null
      if (!itemsByParentId.value.has(parentId)) {
        itemsByParentId.value.set(parentId, [])
      }
      itemsByParentId.value.get(parentId)!.push(item.id)
    }
  }

  /**
   * Upsert (insert or update) an item
   */
  function upsertItem(item: IGearItemV2): void {
    itemsById.value.set(item.id, item)
    updateIndexes()
    saveToStorage()
  }

  /**
   * Upsert multiple items (batch operation)
   */
  function upsertItems(items: IGearItemV2[]): void {
    for (const item of items) {
      itemsById.value.set(item.id, item)
    }
    updateIndexes()
    saveToStorage()
  }

  /**
   * Delete an item
   * Also deletes all children due to cascade
   */
  function deleteItem(itemId: TUUID): void {
    // Get all children recursively
    const childrenToDelete = getDescendants(itemId)

    // Delete item and all children
    itemsById.value.delete(itemId)
    for (const childId of childrenToDelete) {
      itemsById.value.delete(childId)
    }

    updateIndexes()
    saveToStorage()
  }

  /**
   * Get all descendants of an item (recursive)
   */
  function getDescendants(itemId: TUUID): TUUID[] {
    const descendants: TUUID[] = []
    const childIds = itemsByParentId.value.get(itemId) || []

    for (const childId of childIds) {
      descendants.push(childId)
      // Recursively get descendants of this child
      descendants.push(...getDescendants(childId))
    }

    return descendants
  }

  /**
   * Clear all items
   */
  function clearAll(): void {
    itemsById.value.clear()
    itemsByParentId.value.clear()
    saveToStorage()
  }

  /**
   * Set all items (replaces entire store)
   */
  function setItems(items: IGearItemV2[]): void {
    itemsById.value.clear()
    for (const item of items) {
      itemsById.value.set(item.id, item)
    }
    updateIndexes()
    saveToStorage()
  }

  // ===== Persistence =====

  /**
   * Save to localStorage
   */
  function saveToStorage(): void {
    try {
      const items = Array.from(itemsById.value.values())
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
    }
  }

  /**
   * Load from localStorage
   */
  function loadFromStorage(): void {
    try {
      const data = localStorage.getItem(STORAGE_KEY)
      if (!data) return

      const items: IGearItemV2[] = JSON.parse(data)
      setItems(items)
    } catch (error) {
      console.error('Failed to load from localStorage:', error)
    }
  }

  // ===== Initialization =====

  // Run V1→V2 migration before loading (transparent, runs once)
  migrateV1ToV2().then(result => {
    if (result.success && (result.containersMigrated > 0 || result.itemsMigrated > 0)) {
      console.log(`[Gear Store V2] Migration successful: ${result.containersMigrated} containers, ${result.itemsMigrated} items`)
    }
    // Load V2 data after migration
    loadFromStorage()
  }).catch(error => {
    console.error('[Gear Store V2] Migration failed:', error)
    // Still attempt to load V2 data even if migration fails
    loadFromStorage()
  })

  // ===== Return =====

  return {
    // State
    itemsById,
    itemsByParentId,

    // Computed
    getItemById,
    getParentOfItem,
    getChildrenOfItem,
    getRootContainers,
    getAllContainers,
    getAllItems,
    getFavoriteContainers,
    getPublicContainers,

    // Actions
    upsertItem,
    upsertItems,
    deleteItem,
    clearAll,
    setItems,
    loadFromStorage,
    saveToStorage,
  }
})
