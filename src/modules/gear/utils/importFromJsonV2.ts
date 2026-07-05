/**
 * Import a gear tree from the JSON produced by `exportToJsonV2`.
 *
 * Recreates containers and items via the injected `createItem` dependency, assigning fresh
 * parentItemId links (the source ids are not reused, so an import always adds a fresh copy).
 * Dependency-injected so it can be unit tested and used with either service.
 */

import type { ICreateGearItemV2Dto, IGearItemV2 } from '../types/gear.types.v2'
import type { JSONExportNodeV2 } from './exportToJsonV2'

export interface ImportJsonDeps {
  createItem: (data: ICreateGearItemV2Dto) => Promise<IGearItemV2>
}

export interface ImportJsonResult {
  containers: number
  items: number
}

/**
 * Map an export node to a create DTO (without id/timestamps), re-parenting it.
 */
function nodeToCreateDto(node: JSONExportNodeV2, parentItemId: string | null): ICreateGearItemV2Dto {
  return {
    itemType: node.itemType,
    parentItemId,
    name: node.name,
    description: node.description,
    brand: node.brand,
    price: node.price,
    currency: node.currency,
    weight: node.weight,
    weightUnit: node.weightUnit,
    url: node.url,
    color: node.color,
    notes: node.notes,
    containerType: node.containerType,
    maxWeight: node.maxWeight,
    maxWeightUnit: node.maxWeightUnit,
    hideWhenNested: node.hideWhenNested,
    isPublic: false,
    favorite: node.favorite,
    showItemImages: node.showItemImages,
    category: node.category,
    quantity: node.quantity,
    status: node.status,
    priority: node.priority,
    expirationDate: node.expirationDate,
    shelfLife: node.shelfLife,
    quality: node.quality,
    wearable: node.wearable,
    consumable: node.consumable,
    orderIndex: node.orderIndex,
    showOnContainer: node.showOnContainer,
  }
}

/**
 * Parse the JSON export document. Accepts either the documented
 * `{ version, containers: [...] }` shape or a bare array of nodes.
 */
function parseNodes(json: string): JSONExportNodeV2[] {
  const parsed: unknown = JSON.parse(json)

  if (Array.isArray(parsed)) {
    return parsed as JSONExportNodeV2[]
  }
  if (parsed && typeof parsed === 'object' && Array.isArray((parsed as { containers?: unknown }).containers)) {
    return (parsed as { containers: JSONExportNodeV2[] }).containers
  }
  throw new Error('Invalid gear JSON: expected an array or an object with a "containers" array')
}

/**
 * Import containers (and their subtrees) from a JSON string.
 */
export async function importContainersFromJSONV2(
  json: string,
  deps: ImportJsonDeps,
): Promise<ImportJsonResult> {
  const roots = parseNodes(json)
  const result: ImportJsonResult = { containers: 0, items: 0 }

  const createNode = async (node: JSONExportNodeV2, parentItemId: string | null): Promise<void> => {
    const created = await deps.createItem(nodeToCreateDto(node, parentItemId))
    if (node.itemType === 'container') {
      result.containers++
    } else {
      result.items++
    }
    for (const child of node.children ?? []) {
      await createNode(child, created.id)
    }
  }

  for (const root of roots) {
    await createNode(root, null)
  }

  return result
}
