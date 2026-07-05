/**
 * Flatten all gear items (V2) into the catalog DTO used by the "copy from existing item"
 * pickers. Mirrors the V1 `getAllItems`, but operates on the flat V2 item list.
 */

import { config } from '@/shared/config/config'
import type { IGearItemV2, TContainerColor, TGearWeightUnit } from '../types/gear.types.v2'
import type { IItemWithContainer } from './allItemsColumns'
import { DEFAULT_ITEM_CATEGORY, DEFAULT_ITEM_COLOR, DEFAULT_ITEM_PRIORITY, DEFAULT_ITEM_STATUS } from './constants'
import { calculateTotalWeightSyncV2 } from './containerCalculationsV2'
import { convertFromGrams } from './formatWeight'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Build the catalog list from a flat array of V2 items.
 *
 * @param allItems - All gear items (containers and items) from the store
 * @param excludeContainerId - When set, the catalog omits this container and its direct items,
 *   and (matching V1) does not list containers themselves — only regular items.
 */
export function getAllItemsForCatalogV2(
  allItems: IGearItemV2[],
  excludeContainerId?: TUUID,
): IItemWithContainer[] {
  const byId = new Map<string, IGearItemV2>(allItems.map(item => [item.id, item]))
  const getItemById = (id: TUUID) => byId.get(id)
  const getChildrenOfItem = (id: TUUID) => allItems.filter(i => i.parentItemId === id)

  const result: IItemWithContainer[] = []

  for (const item of allItems) {
    if (item.itemType === 'container') {
      // When excluding (the picker's case) we only surface regular items
      if (excludeContainerId) continue

      const totalWeightGrams = calculateTotalWeightSyncV2(item.id, getItemById, getChildrenOfItem)
      const displayWeightUnit = (item.weightUnit ?? config.defaults.preferredWeightUnit) as TGearWeightUnit
      result.push({
        id: item.id,
        name: item.name,
        category: DEFAULT_ITEM_CATEGORY,
        containerId: item.id,
        containerName: item.name,
        containerColor: (item.color ?? DEFAULT_ITEM_COLOR) as TContainerColor,
        quantity: 1,
        weight: convertFromGrams(totalWeightGrams, displayWeightUnit),
        weightUnit: displayWeightUnit,
        status: DEFAULT_ITEM_STATUS,
        priority: DEFAULT_ITEM_PRIORITY,
        brand: item.brand ?? undefined,
        color: undefined,
        expirationDate: undefined,
        wearable: false,
        consumable: false,
        isContainer: true,
        containerType: item.containerType ?? undefined,
      })
      continue
    }

    // Regular item
    if (excludeContainerId && item.parentItemId === excludeContainerId) continue

    const parent = item.parentItemId ? byId.get(item.parentItemId) : undefined
    result.push({
      id: item.id,
      name: item.name,
      category: item.category ?? DEFAULT_ITEM_CATEGORY,
      containerId: parent?.id ?? item.parentItemId ?? '',
      containerName: parent?.name ?? '',
      containerColor: (parent?.color ?? DEFAULT_ITEM_COLOR) as TContainerColor,
      containerType: parent?.containerType ?? undefined,
      quantity: item.quantity ?? 1,
      weight: item.weight ?? 0,
      weightUnit: (item.weightUnit ?? config.defaults.preferredWeightUnit) as TGearWeightUnit,
      status: item.status ?? DEFAULT_ITEM_STATUS,
      priority: item.priority ?? DEFAULT_ITEM_PRIORITY,
      brand: item.brand ?? undefined,
      color: item.color ?? undefined,
      expirationDate: item.expirationDate ?? undefined,
      wearable: item.wearable ?? undefined,
      consumable: item.consumable ?? undefined,
      isContainer: false,
      primaryImageUrl: item.primaryImageUrl ?? undefined,
    })
  }

  return result.sort((a, b) => a.name.localeCompare(b.name))
}
