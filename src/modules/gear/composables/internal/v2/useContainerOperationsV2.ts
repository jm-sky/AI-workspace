import { useQueryClient } from '@tanstack/vue-query'
import type { ICreateGearItemV2Dto, IGearItemV2, IUpdateGearItemV2Dto } from '../../../types/gear.types.v2'
import { useGearV2 } from '../../useGearV2'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Composable for V2 container operations
 *
 * Wraps useGearV2() methods with container-specific logic.
 * Maintains facade pattern similar to V1's useContainerOperations.
 *
 * Usage:
 * ```ts
 * const { containers, rootContainers, createContainer, deleteContainer } = useContainerOperationsV2()
 * const newContainer = await createContainer({ name: 'Bug-Out Bag', containerType: 'backpack' })
 * ```
 */
export function useContainerOperationsV2() {
  const queryClient = useQueryClient()
  const {
    items: _items,
    containers,
    rootContainers,
    createItem,
    getItems,
    getItemById,
    updateItem,
    deleteItem,
    moveItem,
  } = useGearV2()

  /**
   * Invalidate gear queries to refresh data
   */
  const invalidateGearQueries = () => {
    queryClient.invalidateQueries({ queryKey: ['gear'] })
  }

  /**
   * Create a new container
   * @param data - Container creation data
   * @returns Created container
   */
  const createContainer = async (data: Omit<ICreateGearItemV2Dto, 'itemType'>): Promise<IGearItemV2> => {
    // Force itemType to 'container'
    const container = await createItem({ ...data, itemType: 'container' })
    invalidateGearQueries()
    return container
  }

  /**
   * Update a container
   * @param id - Container ID
   * @param data - Update data
   * @returns Updated container
   */
  const updateContainer = async (id: TUUID, data: IUpdateGearItemV2Dto): Promise<IGearItemV2> => {
    const container = await updateItem(id, data)
    invalidateGearQueries()
    return container
  }

  /**
   * Delete a container (and all its children via cascade)
   * @param id - Container ID
   */
  const deleteContainer = async (id: TUUID): Promise<void> => {
    await deleteItem(id)
    invalidateGearQueries()
  }

  /**
   * Delete all root containers (no parent)
   * WARNING: This will cascade delete all items!
   * @returns Number of containers deleted
   */
  const deleteAllContainers = async (): Promise<number> => {
    let deletedCount = 0
    for (const container of rootContainers.value) {
      await deleteItem(container.id)
      deletedCount++
    }
    invalidateGearQueries()
    return deletedCount
  }

  /**
   * Get a container by ID
   * @param id - Container ID
   * @returns Container or undefined
   */
  const getContainerById = async (id: TUUID): Promise<IGearItemV2 | undefined> => {
    const item = await getItemById(id)
    // Verify it's actually a container
    if (item && item.itemType !== 'container') return undefined
    return item
  }

  /**
   * Get root containers (no parent)
   * Reactive computed value
   */
  const getRootContainers = rootContainers

  /**
   * Get nested containers (containers that have a parent)
   * @param parentId - Parent container ID
   * @returns Array of nested containers
   */
  const getNestedContainers = async (parentId?: TUUID): Promise<IGearItemV2[]> => {
    const filters = {
      itemType: 'container' as const,
      parentItemId: parentId,
    }
    return await getItems(filters)
  }

  /**
   * Move a container to a different parent
   * @param containerId - Container ID to move
   * @param targetParentId - Target parent ID (null for root)
   * @returns Moved container
   */
  const moveContainer = async (containerId: TUUID, targetParentId: TUUID | null): Promise<IGearItemV2> => {
    const container = await moveItem(containerId, targetParentId)
    invalidateGearQueries()
    return container
  }

  return {
    // State (reactive)
    containers,
    rootContainers: getRootContainers,

    // Operations
    createContainer,
    updateContainer,
    deleteContainer,
    deleteAllContainers,
    getContainerById,
    getRootContainers,
    getNestedContainers,
    moveContainer,
  }
}

/**
 * Type for the return value of useContainerOperationsV2
 */
export type ContainerOperationsV2 = ReturnType<typeof useContainerOperationsV2>
