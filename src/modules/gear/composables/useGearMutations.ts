/**
 * Gear mutations (V2) with automatic TanStack Query cache invalidation.
 *
 * The `/gear` pages render from TanStack Query (see `useGearQueries`). `useGearV2()`
 * mutations only touch the Pinia store, so the query cache goes stale after a mutation.
 * This composable wraps the V2 mutations and invalidates `gearQueryKeys` afterwards, so
 * any component performing a single mutation gets a consistent, up-to-date UI for free.
 *
 * For bulk operations (e.g. markdown import doing hundreds of writes) keep using
 * `useGearV2()` directly and invalidate once at the end, to avoid a refetch per write.
 *
 * Usage:
 * ```ts
 * const { updateItem, deleteItem } = useGearMutations()
 * await updateItem(id, { name: 'New name' }) // store + cache stay in sync
 * ```
 */

import { useQueryClient } from '@tanstack/vue-query'
import type {
  IBatchOrderUpdateItem,
  ICreateGearItemV2Dto,
  IGearItemV2,
  IUpdateGearItemV2Dto,
} from '../types/gear.types.v2'
import { gearQueryKeys } from '../utils/queryKeys'
import { useGearV2 } from './useGearV2'
import type { TUUID } from '@/shared/types/base.type'

export function useGearMutations() {
  const queryClient = useQueryClient()
  const gear = useGearV2()

  const invalidate = () => queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })

  const createItem = async (data: ICreateGearItemV2Dto): Promise<IGearItemV2> => {
    const item = await gear.createItem(data)
    await invalidate()
    return item
  }

  const updateItem = async (id: TUUID, data: IUpdateGearItemV2Dto): Promise<IGearItemV2> => {
    const item = await gear.updateItem(id, data)
    await invalidate()
    return item
  }

  const deleteItem = async (id: TUUID): Promise<void> => {
    await gear.deleteItem(id)
    await invalidate()
  }

  const moveItem = async (itemId: TUUID, targetParentId: TUUID | null): Promise<IGearItemV2> => {
    const item = await gear.moveItem(itemId, targetParentId)
    await invalidate()
    return item
  }

  const batchUpdateOrder = async (items: IBatchOrderUpdateItem[]): Promise<IGearItemV2[]> => {
    const updated = await gear.batchUpdateOrder(items)
    await invalidate()
    return updated
  }

  return {
    ...gear,
    // Mutations overridden with cache invalidation
    createItem,
    updateItem,
    deleteItem,
    moveItem,
    batchUpdateOrder,
  }
}

/**
 * Type for the return value of useGearMutations
 */
export type GearMutations = ReturnType<typeof useGearMutations>
