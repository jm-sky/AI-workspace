import type { IGearContainer, IGearItem } from '../types/gear.types'
import type { IGearItemV2 } from '../types/gear.types.v2'

/**
 * V1 to V2 Data Migration Service
 *
 * Transparently migrates localStorage data from V1 dual-model to V2 unified model.
 *
 * Migration Strategy:
 * - V1 containers → V2 containers (itemType='container')
 * - V1 items → V2 items (itemType='item')
 * - Preserves all relationships (parent-child)
 * - Field mappings: type→containerType, parentContainerId→parentItemId, order→orderIndex
 */

const V1_CONTAINERS_KEY = 'gear-stack:containers'
const V2_ITEMS_KEY = 'gear-stack:items-v2'
const MIGRATION_FLAG_KEY = 'gear-stack:v2-migration-completed'

interface MigrationResult {
  success: boolean
  itemsMigrated: number
  containersMigrated: number
  errors: string[]
}

/**
 * Check if V1 data exists in localStorage
 */
function hasV1Data(): boolean {
  try {
    const v1Data = localStorage.getItem(V1_CONTAINERS_KEY)
    return !!v1Data && v1Data.length > 2 // More than just "[]"
  } catch {
    return false
  }
}

/**
 * Check if V2 data already exists
 */
function hasV2Data(): boolean {
  try {
    const v2Data = localStorage.getItem(V2_ITEMS_KEY)
    return !!v2Data && v2Data.length > 2
  } catch {
    return false
  }
}

/**
 * Check if migration was already completed
 */
function isMigrationCompleted(): boolean {
  try {
    return localStorage.getItem(MIGRATION_FLAG_KEY) === 'true'
  } catch {
    return false
  }
}

/**
 * Transform V1 container to V2 unified item
 */
function transformContainerToV2(
  container: IGearContainer,
  userId: string = 'local-user',
): IGearItemV2 {
  // Map V1 container to V2 format
  const v2Item: IGearItemV2 = {
    // Core identification
    id: container.id,
    userId,
    itemType: 'container',

    // Parent relationship (V1: parentContainerId → V2: parentItemId)
    parentItemId: container.parentContainerId || null,

    // Basic info
    name: container.name,
    description: container.description || null,

    // Container-specific (V1: type → V2: containerType)
    containerType: container.type || 'backpack',

    // Organization
    category: null, // Containers don't have categories in V1
    orderIndex: null, // V1 containers don't have order

    // Status & Priority
    status: 'owned', // Containers are always owned
    priority: null,

    // Physical attributes
    weight: container.weight ?? null,
    weightUnit: container.weightUnit ?? null,
    maxWeight: container.maxWeight ?? null,
    maxWeightUnit: container.maxWeightUnit ?? null,

    // Quantity
    quantity: 1, // Containers always quantity 1

    // Flags
    wearable: false,
    consumable: false,
    favorite: container.favorite ?? false,
    hideWhenNested: container.hideWhenNested ?? false,

    // Purchase info
    price: container.price ?? null,
    currency: container.currency ?? null,
    url: container.url ?? null,
    brand: container.brand ?? null,

    // Visual
    color: container.color ?? null,

    // Dates
    expirationDate: null,
    createdAt: container.createdAt || new Date().toISOString(),
    updatedAt: container.updatedAt || new Date().toISOString(),

    // Public sharing (if present)
    isPublic: container.isPublic ?? false,
    authorId: container.authorId ?? null,
    authorName: container.authorName ?? null,
    averageUserRating: container.averageUserRating ?? null,
    showItemImages: container.showItemImages ?? false,

    // Quality & Notes
    quality: null,
    notes: null, // V1 containers don't have notes
  }

  return v2Item
}

/**
 * Transform V1 item to V2 unified item
 */
function transformItemToV2(
  item: IGearItem,
  containerId: string,
  userId: string = 'local-user',
): IGearItemV2 {
  const v2Item: IGearItemV2 = {
    // Core identification
    id: item.id,
    userId,
    itemType: 'item',

    // Parent relationship (V1: in container.items → V2: parentItemId)
    parentItemId: containerId,

    // Basic info
    name: item.name,
    description: item.notes ?? null, // V2 uses description, V1 uses notes

    // Container-specific (not applicable for items)
    containerType: null,

    // Organization
    category: item.category ?? null,
    orderIndex: item.order ?? null,

    // Status & Priority
    status: item.status || 'owned',
    priority: item.priority ?? null,

    // Physical attributes
    weight: item.weight ?? null,
    weightUnit: item.weightUnit ?? null,
    maxWeight: null, // Items don't have maxWeight
    maxWeightUnit: null,

    // Quantity
    quantity: item.quantity ?? 1,

    // Flags
    wearable: item.wearable ?? false,
    consumable: item.consumable ?? false,
    favorite: false, // Items don't have favorite flag in V1
    hideWhenNested: false,

    // Purchase info
    price: item.price ?? null,
    currency: item.currency ?? null,
    url: item.url ?? null,
    brand: item.brand ?? null,

    // Visual
    color: item.color ?? null,

    // Dates
    expirationDate: item.expirationDate ?? null,
    createdAt: item.createdAt || new Date().toISOString(),
    updatedAt: item.updatedAt || new Date().toISOString(),

    // Public sharing (items inherit from container)
    isPublic: false,
    authorId: null,
    authorName: null,
    averageUserRating: null,
    showItemImages: false,

    // Quality & Notes
    quality: item.quality ?? null,
    notes: item.notes ?? null,
  }

  return v2Item
}

/**
 * Migrate all V1 data to V2 format
 */
export async function migrateV1ToV2(): Promise<MigrationResult> {
  const result: MigrationResult = {
    success: false,
    itemsMigrated: 0,
    containersMigrated: 0,
    errors: [],
  }

  try {
    // Check if migration is needed
    if (isMigrationCompleted()) {
      console.log('[V2 Migration] Already completed, skipping')
      result.success = true
      return result
    }

    if (!hasV1Data()) {
      console.log('[V2 Migration] No V1 data found, skipping')
      // Mark as completed so we don't check again
      localStorage.setItem(MIGRATION_FLAG_KEY, 'true')
      result.success = true
      return result
    }

    if (hasV2Data()) {
      console.log('[V2 Migration] V2 data already exists, skipping')
      // Mark as completed
      localStorage.setItem(MIGRATION_FLAG_KEY, 'true')
      result.success = true
      return result
    }

    console.log('[V2 Migration] Starting migration...')

    // Load V1 data
    const v1DataRaw = localStorage.getItem(V1_CONTAINERS_KEY)
    if (!v1DataRaw) {
      throw new Error('Failed to load V1 data')
    }

    const v1Containers: IGearContainer[] = JSON.parse(v1DataRaw)
    console.log(`[V2 Migration] Found ${v1Containers.length} V1 containers`)

    // Transform to V2 format
    const v2Items: IGearItemV2[] = []

    for (const container of v1Containers) {
      try {
        // Transform container
        const v2Container = transformContainerToV2(container)
        v2Items.push(v2Container)
        result.containersMigrated++

        // Transform all items in container
        if (container.items && Array.isArray(container.items)) {
          for (const item of container.items) {
            try {
              const v2Item = transformItemToV2(item, container.id)
              v2Items.push(v2Item)
              result.itemsMigrated++
            } catch (error) {
              const errorMsg = `Failed to migrate item ${item.id}: ${error instanceof Error ? error.message : 'Unknown error'}`
              console.error(errorMsg)
              result.errors.push(errorMsg)
            }
          }
        }
      } catch (error) {
        const errorMsg = `Failed to migrate container ${container.id}: ${error instanceof Error ? error.message : 'Unknown error'}`
        console.error(errorMsg)
        result.errors.push(errorMsg)
      }
    }

    // Save V2 data
    localStorage.setItem(V2_ITEMS_KEY, JSON.stringify(v2Items))

    // Mark migration as completed
    localStorage.setItem(MIGRATION_FLAG_KEY, 'true')

    console.log(`[V2 Migration] Complete! Migrated ${result.containersMigrated} containers and ${result.itemsMigrated} items`)

    if (result.errors.length > 0) {
      console.warn(`[V2 Migration] Completed with ${result.errors.length} errors:`, result.errors)
    }

    result.success = true
    return result
  } catch (error) {
    const errorMsg = `Migration failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    console.error(`[V2 Migration] ${errorMsg}`)
    result.errors.push(errorMsg)
    result.success = false
    return result
  }
}

/**
 * Read V1 localStorage data and return it as flat V2 items (containers + items),
 * WITHOUT touching V2 storage or the store.
 *
 * Used by the local→API upload flow (`dataMigrationService`): the V1 key
 * (`gear-stack:containers`) is a stable offline snapshot that the API-synced V2 store
 * never overwrites, so it's the safe source for uploading offline data to the backend.
 */
export function readV1LocalDataAsV2Items(): IGearItemV2[] {
  let v1Containers: IGearContainer[] = []
  try {
    const raw = localStorage.getItem(V1_CONTAINERS_KEY)
    if (!raw) return []
    v1Containers = JSON.parse(raw) as IGearContainer[]
  } catch {
    return []
  }

  const v2Items: IGearItemV2[] = []
  for (const container of v1Containers) {
    try {
      v2Items.push(transformContainerToV2(container))
      if (Array.isArray(container.items)) {
        for (const item of container.items) {
          try {
            v2Items.push(transformItemToV2(item, container.id))
          } catch {
            // Skip malformed item
          }
        }
      }
    } catch {
      // Skip malformed container
    }
  }
  return v2Items
}

/**
 * Clear the V1 localStorage snapshot (after it has been uploaded to the API).
 */
export function clearV1LocalData(): void {
  try {
    localStorage.removeItem(V1_CONTAINERS_KEY)
  } catch {
    // ignore
  }
}

/**
 * Check if migration is needed (for displaying UI notification)
 */
export function needsMigration(): boolean {
  return hasV1Data() && !hasV2Data() && !isMigrationCompleted()
}

/**
 * Reset migration flag (for testing purposes)
 */
export function resetMigrationFlag(): void {
  localStorage.removeItem(MIGRATION_FLAG_KEY)
  console.log('[V2 Migration] Migration flag reset')
}
