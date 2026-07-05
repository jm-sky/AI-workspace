import type { IGearItemV2, TGearItemPriority } from '../types/gear.types.v2'
import { getCurrency } from './currencyFormatter'
import { convertToGrams } from './formatWeight'
import { isSet } from './helpers'
import type { TUUID } from '@/shared/types/base.type'

/**
 * V2 calculation utilities for unified model
 *
 * Key differences from V1:
 * - Accept store getters as function parameters (dependency injection)
 * - Use O(1) Map lookups instead of array scans
 * - Recursive traversal via getChildrenOfItem() instead of allContainers.find()
 * - Handle both containers and items uniformly (check itemType)
 */

/**
 * Calculate total weight of an item (container or regular item) synchronously
 * For containers: includes own weight + all children recursively
 * For items: includes own weight * quantity
 *
 * @param itemId - ID of item/container to calculate weight for
 * @param getItemById - Store getter to fetch item by ID (O(1))
 * @param getChildrenOfItem - Store getter to fetch children of an item (O(1))
 * @returns Total weight in grams
 */
export function calculateTotalWeightSyncV2(
  itemId: TUUID,
  getItemById: (id: TUUID) => IGearItemV2 | undefined,
  getChildrenOfItem: (id: TUUID) => IGearItemV2[],
): number {
  const item = getItemById(itemId)
  if (!item) return 0

  // Start with item's own weight (if set)
  let totalWeight = 0
  if (isSet(item.weight) && isSet(item.weightUnit)) {
    totalWeight = convertToGrams(item.weight!, item.weightUnit!)
  }

  // For containers: add weight of all children recursively
  if (item.itemType === 'container') {
    const children = getChildrenOfItem(itemId)
    for (const child of children) {
      const childWeight = calculateTotalWeightSyncV2(child.id, getItemById, getChildrenOfItem)
      const quantity = child.quantity || 1
      totalWeight += childWeight * quantity
    }
  }

  return totalWeight
}

/**
 * Calculate readiness percentage synchronously (for use in computed)
 * Only applies to containers - counts owned items as a percentage of total
 *
 * @param itemId - Container ID
 * @param getItemById - Store getter
 * @param getChildrenOfItem - Store getter
 * @returns Readiness percentage (0-100)
 */
export function calculateReadinessPercentageSyncV2(
  itemId: TUUID,
  getItemById: (id: TUUID) => IGearItemV2 | undefined,
  getChildrenOfItem: (id: TUUID) => IGearItemV2[],
): number {
  const item = getItemById(itemId)
  if (!item || item.itemType !== 'container') {
    return 0
  }

  const children = getChildrenOfItem(itemId)
  // Only count regular items (not nested containers)
  const items = children.filter(child => child.itemType === 'item')

  if (items.length === 0) {
    return 0
  }

  const ownedItems = items.filter(item => item.status === 'owned').length
  return Math.round((ownedItems / items.length) * 100)
}

/**
 * Calculate weight limit percentage synchronously (for use in computed)
 * Only applies to containers with maxWeight set
 *
 * @param itemId - Container ID
 * @param getItemById - Store getter
 * @param getChildrenOfItem - Store getter
 * @returns Weight limit percentage (0-100+) or null if no limit
 */
export function calculateWeightLimitPercentageSyncV2(
  itemId: TUUID,
  getItemById: (id: TUUID) => IGearItemV2 | undefined,
  getChildrenOfItem: (id: TUUID) => IGearItemV2[],
): number | null {
  const item = getItemById(itemId)
  if (!item || item.itemType !== 'container' || !isSet(item.maxWeight)) {
    return null
  }

  const totalWeight = calculateTotalWeightSyncV2(itemId, getItemById, getChildrenOfItem)
  const maxWeightInGrams = convertToGrams(item.maxWeight!, item.maxWeightUnit || 'g')

  if (maxWeightInGrams === 0) {
    return 0
  }

  return Math.round((totalWeight / maxWeightInGrams) * 100)
}

/**
 * Calculate total price of an item/container synchronously
 * Groups prices by currency and returns totals per currency
 *
 * @param itemId - Item/container ID
 * @param getItemById - Store getter
 * @param getChildrenOfItem - Store getter
 * @param defaultCurrency - Default currency to use when item has no currency
 * @returns Object with currency totals: { [currency: string]: number }
 */
export function calculateTotalPriceSyncV2(
  itemId: TUUID,
  getItemById: (id: TUUID) => IGearItemV2 | undefined,
  getChildrenOfItem: (id: TUUID) => IGearItemV2[],
  defaultCurrency: string,
): Record<string, number> {
  const item = getItemById(itemId)
  if (!item) return {}

  const totals: Record<string, number> = {}

  // Helper to add price to totals
  const addPrice = (price: number | null | undefined, currency: string | null | undefined, quantity: number = 1) => {
    if (price == null || price <= 0) return
    const curr = getCurrency(currency, defaultCurrency)
    totals[curr] = (totals[curr] || 0) + price * quantity
  }

  // Add item's own price (containers can have prices too)
  addPrice(item.price, item.currency)

  // For containers: add prices of all children recursively
  if (item.itemType === 'container') {
    const children = getChildrenOfItem(itemId)
    for (const child of children) {
      const childTotals = calculateTotalPriceSyncV2(child.id, getItemById, getChildrenOfItem, defaultCurrency)
      const childQuantity = child.quantity || 1

      // Multiply child totals by quantity and add to totals
      for (const [currency, amount] of Object.entries(childTotals)) {
        totals[currency] = (totals[currency] || 0) + amount * childQuantity
      }
    }
  }

  return totals
}

/**
 * Calculate price distribution by category
 * Recursively collects all items from container and categorizes prices
 *
 * @param itemId - Container ID
 * @param getItemById - Store getter
 * @param getChildrenOfItem - Store getter
 * @returns Array of category price data with totals and percentages
 */
export function calculatePriceByCategoryV2(
  itemId: TUUID,
  getItemById: (id: TUUID) => IGearItemV2 | undefined,
  getChildrenOfItem: (id: TUUID) => IGearItemV2[],
): Array<{ category: string; totalPrice: number; percentage: number }> {
  const categoryMap = new Map<string, number>()
  let totalPrice = 0

  // Recursively collect all items
  const collectItems = (currentId: TUUID): void => {
    const current = getItemById(currentId)
    if (!current) return

    if (current.itemType === 'item') {
      // Process item price
      if (current.price != null && current.price > 0 && (current.quantity || 1) > 0) {
        const itemTotal = current.price * (current.quantity || 1)
        const category = current.category || 'other'
        const categoryTotal = categoryMap.get(category) || 0
        categoryMap.set(category, categoryTotal + itemTotal)
        totalPrice += itemTotal
      }
    } else if (current.itemType === 'container') {
      // Recurse into container children
      const children = getChildrenOfItem(currentId)
      for (const child of children) {
        collectItems(child.id)
      }
    }
  }

  collectItems(itemId)

  return Array.from(categoryMap.entries())
    .map(([category, price]) => ({
      category,
      totalPrice: price,
      percentage: totalPrice > 0 ? (price / totalPrice) * 100 : 0,
    }))
    .sort((a, b) => b.totalPrice - a.totalPrice)
}

/**
 * Calculate item distribution by priority
 * Recursively collects all items from container
 *
 * @param itemId - Container ID
 * @param getItemById - Store getter
 * @param getChildrenOfItem - Store getter
 * @returns Array of priority data with counts and percentages
 */
export function calculateItemsByPriorityV2(
  itemId: TUUID,
  getItemById: (id: TUUID) => IGearItemV2 | undefined,
  getChildrenOfItem: (id: TUUID) => IGearItemV2[],
): Array<{ priority: TGearItemPriority; count: number; percentage: number }> {
  const priorityMap = new Map<TGearItemPriority, number>()

  // Recursively collect all items
  const collectItems = (currentId: TUUID): void => {
    const current = getItemById(currentId)
    if (!current) return

    if (current.itemType === 'item') {
      const priority = current.priority || 'medium'
      const currentCount = priorityMap.get(priority) || 0
      priorityMap.set(priority, currentCount + (current.quantity || 1))
    } else if (current.itemType === 'container') {
      const children = getChildrenOfItem(currentId)
      for (const child of children) {
        collectItems(child.id)
      }
    }
  }

  collectItems(itemId)

  const totalQuantity = Array.from(priorityMap.values()).reduce((a, b) => a + b, 0)

  const result = Array.from(priorityMap.entries())
    .map(([priority, count]) => ({
      priority,
      count,
      percentage: totalQuantity > 0 ? (count / totalQuantity) * 100 : 0,
    }))
    .sort((a, b) => {
      // Sort by priority order: critical, high, medium, low
      const order: Record<TGearItemPriority, number> = {
        critical: 0,
        high: 1,
        medium: 2,
        low: 3,
      }
      return order[a.priority] - order[b.priority]
    })

  return result
}

/**
 * Weight breakdown interface
 */
export interface WeightBreakdown {
  base: number      // Other items weight in grams (not worn or consumable)
  worn: number      // Worn weight in grams
  consumable: number // Consumable weight in grams
  total: number     // Total weight in grams
}

/**
 * Calculate weight breakdown for a container
 * Categorizes items by wearable/consumable flags
 * Priority: consumable > worn > base (if item has both flags, treat as consumable)
 *
 * @param itemId - Container ID
 * @param getItemById - Store getter
 * @param getChildrenOfItem - Store getter
 * @returns Weight breakdown with base, worn, consumable weights
 */
export function calculateWeightBreakdownV2(
  itemId: TUUID,
  getItemById: (id: TUUID) => IGearItemV2 | undefined,
  getChildrenOfItem: (id: TUUID) => IGearItemV2[],
): WeightBreakdown {
  const item = getItemById(itemId)
  if (!item) {
    return { base: 0, worn: 0, consumable: 0, total: 0 }
  }

  let baseWeight = 0
  let wornWeight = 0
  let consumableWeight = 0

  // Add container's own weight to base category (if set)
  if (item.itemType === 'container' && isSet(item.weight) && isSet(item.weightUnit)) {
    const containerWeight = convertToGrams(item.weight!, item.weightUnit!)
    baseWeight += containerWeight
  }

  // Process direct children only (not recursive for now, matching V1 behavior)
  const children = getChildrenOfItem(itemId)
  for (const child of children) {
    // Only process regular items, skip nested containers
    if (child.itemType !== 'item') continue

    const childWeight = convertToGrams(child.weight || 0, child.weightUnit || 'g') * (child.quantity || 1)

    // Categorize by wearable/consumable flags
    // Priority: consumable > worn > base
    if (child.consumable) {
      consumableWeight += childWeight
    } else if (child.wearable) {
      wornWeight += childWeight
    } else {
      baseWeight += childWeight
    }
  }

  const total = baseWeight + wornWeight + consumableWeight

  return {
    base: baseWeight,
    worn: wornWeight,
    consumable: consumableWeight,
    total,
  }
}
