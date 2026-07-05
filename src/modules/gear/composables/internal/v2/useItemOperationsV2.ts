import type { ICreateGearItemV2Dto, IGearItemV2, IUpdateGearItemV2Dto } from '../../../types/gear.types.v2'
import { useGearV2 } from '../../useGearV2'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Composable for V2 item operations
 *
 * Thin wrapper around useGearV2() for item-specific operations.
 * Works on both regular items and nested containers uniformly.
 *
 * Usage:
 * ```ts
 * const { createItem, updateItem, deleteItem } = useItemOperationsV2()
 * const newItem = await createItem({ name: 'Water Bottle', category: 'water', itemType: 'item' })
 * ```
 */
export function useItemOperationsV2() {
  const {
    createItem,
    getItemById,
    updateItem,
    deleteItem,
    moveItem,
    batchUpdateOrder,
  } = useGearV2()

  /**
   * Create a new item (can be regular item or nested container)
   * @param data - Item creation data
   * @returns Created item
   */
  const createItemV2 = async (data: ICreateGearItemV2Dto): Promise<IGearItemV2> => {
    return await createItem(data)
  }

  /**
   * Update an item
   * @param id - Item ID
   * @param data - Update data
   * @returns Updated item
   */
  const updateItemV2 = async (id: TUUID, data: IUpdateGearItemV2Dto): Promise<IGearItemV2> => {
    return await updateItem(id, data)
  }

  /**
   * Delete an item
   * @param id - Item ID
   */
  const deleteItemV2 = async (id: TUUID): Promise<void> => {
    await deleteItem(id)
  }

  /**
   * Get an item by ID
   * @param id - Item ID
   * @returns Item or undefined
   */
  const getItemByIdV2 = async (id: TUUID): Promise<IGearItemV2 | undefined> => {
    return await getItemById(id)
  }

  /**
   * Move an item to a different parent container
   * @param itemId - Item ID to move
   * @param targetParentId - Target parent container ID (null for root)
   * @returns Moved item
   */
  const moveItemV2 = async (itemId: TUUID, targetParentId: TUUID | null): Promise<IGearItemV2> => {
    return await moveItem(itemId, targetParentId)
  }

  /**
   * Batch update order/sorting for multiple items
   * @param updates - Array of {id, orderIndex} objects
   * @returns Updated items
   */
  const batchUpdateOrderV2 = async (updates: Array<{ id: TUUID; orderIndex: number }>): Promise<IGearItemV2[]> => {
    return await batchUpdateOrder(updates)
  }

  return {
    createItem: createItemV2,
    updateItem: updateItemV2,
    deleteItem: deleteItemV2,
    getItemById: getItemByIdV2,
    moveItem: moveItemV2,
    batchUpdateOrder: batchUpdateOrderV2,
  }
}

/**
 * Type for the return value of useItemOperationsV2
 */
export type ItemOperationsV2 = ReturnType<typeof useItemOperationsV2>
