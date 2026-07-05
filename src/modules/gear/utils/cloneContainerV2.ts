/**
 * Deep-clone a gear container subtree (V2 unified model).
 *
 * Creates a copy of a container and (optionally) all of its children — regular items and,
 * if requested, nested containers — assigning fresh ids and re-parenting via `parentItemId`.
 *
 * The logic is dependency-injected (no direct store/service access) so it can be unit tested
 * and reused with either the API or the localStorage service.
 */

import type { ICreateGearItemV2Dto, IGearItemV2 } from '../types/gear.types.v2'
import type { TUUID } from '@/shared/types/base.type'

export interface CloneContainerOptions {
  newName: string
  includeNestedContainers?: boolean
  includePrices?: boolean
}

export interface CloneContainerDeps {
  getItemById: (id: TUUID) => Promise<IGearItemV2 | undefined>
  getChildren: (parentItemId: TUUID) => Promise<IGearItemV2[]>
  createItem: (data: ICreateGearItemV2Dto) => Promise<IGearItemV2>
}

/**
 * Build a create DTO from an existing item, applying clone overrides.
 */
function toCreateDto(
  item: IGearItemV2,
  overrides: { name?: string; parentItemId: TUUID | null; includePrices: boolean },
): ICreateGearItemV2Dto {
  return {
    itemType: item.itemType,
    parentItemId: overrides.parentItemId,
    name: overrides.name ?? item.name,
    description: item.description,
    brand: item.brand,
    price: overrides.includePrices ? item.price : null,
    currency: item.currency,
    weight: item.weight,
    weightUnit: item.weightUnit,
    url: item.url,
    color: item.color,
    notes: item.notes,
    // Container-specific
    containerType: item.containerType,
    maxWeight: item.maxWeight,
    maxWeightUnit: item.maxWeightUnit,
    hideWhenNested: item.hideWhenNested,
    // A clone starts private regardless of the source's visibility
    isPublic: false,
    favorite: item.favorite,
    showItemImages: item.showItemImages,
    // Item-specific
    category: item.category,
    quantity: item.quantity,
    status: item.status,
    priority: item.priority,
    expirationDate: item.expirationDate,
    shelfLife: item.shelfLife,
    quality: item.quality,
    wearable: item.wearable,
    consumable: item.consumable,
    orderIndex: item.orderIndex,
    showOnContainer: item.showOnContainer,
    catalogueItemId: item.catalogueItemId,
  }
}

/**
 * Clone a container (and optionally its subtree) and return the newly created root container.
 */
export async function cloneContainerV2(
  sourceId: TUUID,
  options: CloneContainerOptions,
  deps: CloneContainerDeps,
): Promise<IGearItemV2> {
  const { newName, includeNestedContainers = false, includePrices = true } = options

  const source = await deps.getItemById(sourceId)
  if (!source || source.itemType !== 'container') {
    throw new Error(`Container with id ${sourceId} not found`)
  }

  // Create the root clone (always at top level)
  const rootClone = await deps.createItem(
    toCreateDto(source, { name: newName, parentItemId: null, includePrices }),
  )

  const cloneChildren = async (oldParentId: TUUID, newParentId: TUUID): Promise<void> => {
    const children = await deps.getChildren(oldParentId)
    for (const child of children) {
      // Skip nested containers unless requested; regular items are always cloned
      if (child.itemType === 'container' && !includeNestedContainers) {
        continue
      }
      const clone = await deps.createItem(
        toCreateDto(child, { parentItemId: newParentId, includePrices }),
      )
      if (child.itemType === 'container') {
        await cloneChildren(child.id, clone.id)
      }
    }
  }

  await cloneChildren(sourceId, rootClone.id)

  return rootClone
}
