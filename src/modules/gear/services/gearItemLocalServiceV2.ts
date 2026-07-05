/**
 * Local storage service for unified gear items (V2)
 *
 * This service provides localStorage-based operations for the unified model.
 * Used when backend is not available (offline mode).
 *
 * @module gear/services/v2/local
 */

import type {
  IBatchOrderUpdateItem,
  ICreateGearItemV2Dto,
  IGearItemFiltersV2,
  IGearItemServiceV2,
  IGearItemV2,
  IUpdateGearItemV2Dto,
} from '../types/gear.types.v2'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Local storage service implementation for unified gear items (V2)
 */
export const gearItemLocalServiceV2: IGearItemServiceV2 = {
  // ===== Create =====

  async createItem(data: ICreateGearItemV2Dto): Promise<IGearItemV2> {
    const store = useGearStoreV2()

    const item: IGearItemV2 = {
      id: data.id ?? crypto.randomUUID(),
      userId: 'local-user', // localStorage doesn't have real user IDs
      itemType: data.itemType,
      parentItemId: data.parentItemId,

      // Common fields
      name: data.name,
      description: data.description,
      brand: data.brand,
      price: data.price,
      currency: data.currency,
      weight: data.weight,
      weightUnit: data.weightUnit,
      url: data.url,
      color: data.color,
      notes: data.notes,

      // Container-specific
      containerType: data.containerType,
      maxWeight: data.maxWeight,
      maxWeightUnit: data.maxWeightUnit,
      hideWhenNested: data.hideWhenNested,
      isPublic: data.isPublic,
      favorite: data.favorite,
      showItemImages: data.showItemImages,

      // Item-specific
      category: data.category,
      quantity: data.quantity,
      status: data.status,
      priority: data.priority,
      expirationDate: data.expirationDate,
      quality: data.quality,
      wearable: data.wearable,
      consumable: data.consumable,
      orderIndex: data.orderIndex,
      showOnContainer: data.showOnContainer,

      // Linking
      linkedItemId: data.linkedItemId,
      catalogueItemId: data.catalogueItemId,

      // Metadata
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    store.upsertItem(item)
    return item
  },

  // ===== Read =====

  async getItems(filters?: IGearItemFiltersV2): Promise<IGearItemV2[]> {
    const store = useGearStoreV2()
    let items = store.getAllItems

    // Apply filters
    if (filters) {
      if (filters.itemType && filters.itemType !== 'all') {
        items = items.filter(item => item.itemType === filters.itemType)
      }

      if (filters.parentItemId !== undefined) {
        items = items.filter(item => item.parentItemId === filters.parentItemId)
      }

      if (filters.isPublic !== undefined) {
        items = items.filter(item => item.isPublic === filters.isPublic)
      }

      if (filters.favorite !== undefined) {
        items = items.filter(item => item.favorite === filters.favorite)
      }

      if (filters.status) {
        items = items.filter(item => item.status === filters.status)
      }

      if (filters.priority) {
        items = items.filter(item => item.priority === filters.priority)
      }

      if (filters.category) {
        items = items.filter(item => item.category === filters.category)
      }
    }

    return items
  },

  async getItemById(id: TUUID): Promise<IGearItemV2 | undefined> {
    const store = useGearStoreV2()
    return store.getItemById(id)
  },

  async getChildren(parentItemId: TUUID): Promise<IGearItemV2[]> {
    const store = useGearStoreV2()
    return store.getChildrenOfItem(parentItemId)
  },

  // ===== Update =====

  async updateItem(id: TUUID, data: IUpdateGearItemV2Dto): Promise<IGearItemV2> {
    const store = useGearStoreV2()
    const existingItem = store.getItemById(id)

    if (!existingItem) {
      throw new Error(`Item not found: ${id}`)
    }

    // Filter out undefined and null values from update data
    const updates = Object.fromEntries(
      Object.entries(data).filter(([_, value]) => value !== undefined && value !== null),
    )

    const updatedItem: IGearItemV2 = {
      ...existingItem,
      ...updates,
      updatedAt: new Date().toISOString(),
    }

    store.upsertItem(updatedItem)
    return updatedItem
  },

  async batchUpdateOrder(items: IBatchOrderUpdateItem[]): Promise<IGearItemV2[]> {
    const store = useGearStoreV2()
    const updatedItems: IGearItemV2[] = []

    for (const itemUpdate of items) {
      const existingItem = store.getItemById(itemUpdate.id)
      if (existingItem) {
        const updatedItem: IGearItemV2 = {
          ...existingItem,
          orderIndex: itemUpdate.orderIndex,
          updatedAt: new Date().toISOString(),
        }
        updatedItems.push(updatedItem)
      }
    }

    store.upsertItems(updatedItems)
    return updatedItems
  },

  async moveItem(itemId: TUUID, targetParentId: TUUID | null): Promise<IGearItemV2> {
    const store = useGearStoreV2()
    const item = store.getItemById(itemId)

    if (!item) {
      throw new Error(`Item not found: ${itemId}`)
    }

    // Validate target parent if provided
    if (targetParentId) {
      const targetParent = store.getItemById(targetParentId)
      if (!targetParent) {
        throw new Error(`Target parent not found: ${targetParentId}`)
      }
      if (targetParent.itemType !== 'container') {
        throw new Error('Target must be a container')
      }
    }

    const updatedItem: IGearItemV2 = {
      ...item,
      parentItemId: targetParentId,
      updatedAt: new Date().toISOString(),
    }

    store.upsertItem(updatedItem)
    return updatedItem
  },

  // ===== Delete =====

  async deleteItem(id: TUUID): Promise<void> {
    const store = useGearStoreV2()
    store.deleteItem(id)
  },
}
