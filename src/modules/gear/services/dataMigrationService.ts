import { logger } from '@/shared/utils/logger'
import type { ICreateGearItemV2Dto, IGearItemV2 } from '../types/gear.types.v2'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { gearItemApiServiceV2 } from './gearItemApiServiceV2'
import { clearV1LocalData, readV1LocalDataAsV2Items } from './v1ToV2Migration'

const V1_CONTAINERS_KEY = 'gear-stack:containers'

/**
 * Check if there is offline gear data in localStorage (the legacy V1 key, which is the
 * stable offline snapshot used as the upload source).
 */
export function hasLocalData(): boolean {
  const stored = localStorage.getItem(V1_CONTAINERS_KEY)
  if (!stored) return false

  try {
    const containers = JSON.parse(stored) as unknown[]
    return Array.isArray(containers) && containers.length > 0
  } catch {
    return false
  }
}

/**
 * Build a create DTO from a V2 item, preserving its id and parent so the hierarchy is
 * reconstructed on the backend without an id-mapping step (the V2 API honors provided ids).
 */
function toCreateDto(item: IGearItemV2): ICreateGearItemV2Dto {
  return {
    id: item.id,
    itemType: item.itemType,
    parentItemId: item.parentItemId,
    name: item.name,
    description: item.description,
    brand: item.brand,
    price: item.price,
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
    isPublic: item.isPublic,
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
  }
}

/**
 * Order containers so a parent always precedes its children (so parentItemId references
 * are valid at creation time).
 */
function sortContainersParentFirst(containers: IGearItemV2[]): IGearItemV2[] {
  const byId = new Map(containers.map(c => [c.id, c]))
  const emitted = new Set<string>()
  const visiting = new Set<string>() // cycle guard
  const result: IGearItemV2[] = []

  const visit = (container: IGearItemV2): void => {
    if (emitted.has(container.id) || visiting.has(container.id)) return
    visiting.add(container.id)
    const parent = container.parentItemId ? byId.get(container.parentItemId) : undefined
    if (parent) visit(parent)
    visiting.delete(container.id)
    emitted.add(container.id)
    result.push(container)
  }

  containers.forEach(visit)
  return result
}

/**
 * Migrate offline gear data (V1 localStorage snapshot) to the API.
 * Called after successful login when local data exists.
 *
 * Strategy:
 * 1. Read offline data from the V1 localStorage key as flat V2 items
 * 2. Create containers first (parent before child), then items, via the V2 API,
 *    preserving ids so the hierarchy is reconstructed without id mapping
 * 3. Refresh the V2 store from the API and clear the V1 snapshot
 */
export async function migrateLocalDataToAPI(): Promise<void> {
  const items = readV1LocalDataAsV2Items()

  if (items.length === 0) {
    logger.info('No local data to migrate')
    return
  }

  const containers = sortContainersParentFirst(items.filter(i => i.itemType === 'container'))
  const regularItems = items.filter(i => i.itemType === 'item')

  logger.info(`Migrating ${containers.length} containers and ${regularItems.length} items to API...`)

  let failures = 0

  // Phase 1: containers (parent before child)
  for (const container of containers) {
    try {
      await gearItemApiServiceV2.createItem(toCreateDto(container))
    } catch (error) {
      failures++
      logger.warn(`Failed to migrate container ${container.name}:`, error)
    }
  }

  // Phase 2: items (their parent containers now exist)
  for (const item of regularItems) {
    try {
      await gearItemApiServiceV2.createItem(toCreateDto(item))
    } catch (error) {
      failures++
      logger.warn(`Failed to migrate item ${item.name}:`, error)
    }
  }

  // Refresh the store from the API so it reflects the uploaded data
  try {
    const fresh = await gearItemApiServiceV2.getItems()
    useGearStoreV2().setItems(fresh)
  } catch (error) {
    logger.warn('Failed to refresh store after migration:', error)
  }

  // Only drop the offline snapshot when everything uploaded cleanly, to avoid losing
  // data that didn't make it to the backend.
  if (failures === 0) {
    clearV1LocalData()
    logger.info('Migration complete; offline snapshot cleared')
  } else {
    logger.warn(`Migration finished with ${failures} failures; keeping offline snapshot`)
  }
}

/**
 * Check if data should be migrated and prompt user
 * This is a helper that can be used in UI to show migration prompt
 */
export function shouldPromptForMigration(): boolean {
  return hasLocalData()
}
