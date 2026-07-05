import type { IGearItemV2 } from '../../../types/gear.types.v2'
import { useGearStoreV2 } from '../../../store/useGearStoreV2'
import {
  calculateItemsByPriorityV2,
  calculatePriceByCategoryV2,
  calculateReadinessPercentageSyncV2,
  calculateTotalPriceSyncV2,
  calculateTotalWeightSyncV2,
  calculateWeightBreakdownV2,
  calculateWeightLimitPercentageSyncV2,
  type WeightBreakdown,
} from '../../../utils/containerCalculationsV2'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Composable for V2 container calculations
 *
 * Bridges V2 calculation utilities and Vue components.
 * All calculations use the flat Map store for O(1) lookups.
 *
 * Usage:
 * ```ts
 * const { calculateTotalWeight, calculateReadinessPercentage } = useContainerCalculationsV2()
 * const totalWeight = calculateTotalWeight(containerId)
 * const readiness = calculateReadinessPercentage(containerId)
 * ```
 */
export function useContainerCalculationsV2() {
  const store = useGearStoreV2()

  /**
   * Calculate total weight of an item/container
   * @param itemId - Item/container ID
   * @returns Total weight in grams
   */
  const calculateTotalWeight = (itemId: TUUID): number => {
    return calculateTotalWeightSyncV2(itemId, store.getItemById, store.getChildrenOfItem)
  }

  /**
   * Calculate readiness percentage for a container
   * @param itemId - Container ID
   * @returns Readiness percentage (0-100)
   */
  const calculateReadinessPercentage = (itemId: TUUID): number => {
    return calculateReadinessPercentageSyncV2(itemId, store.getItemById, store.getChildrenOfItem)
  }

  /**
   * Calculate weight limit percentage for a container
   * @param itemId - Container ID
   * @returns Weight limit percentage (0-100+) or null if no limit
   */
  const calculateWeightLimitPercentage = (itemId: TUUID): number | null => {
    return calculateWeightLimitPercentageSyncV2(itemId, store.getItemById, store.getChildrenOfItem)
  }

  /**
   * Check if weight limit is exceeded
   * @param itemId - Container ID
   * @returns True if weight limit is exceeded (>100%)
   */
  const isWeightLimitExceeded = (itemId: TUUID): boolean => {
    const percentage = calculateWeightLimitPercentage(itemId)
    return percentage !== null && percentage > 100
  }

  /**
   * Calculate total price of an item/container by currency
   * @param itemId - Item/container ID
   * @param defaultCurrency - Default currency
   * @returns Object with currency totals
   */
  const calculateTotalPrice = (itemId: TUUID, defaultCurrency: string = 'USD'): Record<string, number> => {
    return calculateTotalPriceSyncV2(itemId, store.getItemById, store.getChildrenOfItem, defaultCurrency)
  }

  /**
   * Calculate price distribution by category
   * @param itemId - Container ID
   * @returns Array of category price data
   */
  const calculatePriceByCategory = (itemId: TUUID) => {
    return calculatePriceByCategoryV2(itemId, store.getItemById, store.getChildrenOfItem)
  }

  /**
   * Calculate item distribution by priority
   * @param itemId - Container ID
   * @returns Array of priority data
   */
  const calculateItemsByPriority = (itemId: TUUID) => {
    return calculateItemsByPriorityV2(itemId, store.getItemById, store.getChildrenOfItem)
  }

  /**
   * Calculate weight breakdown (base, worn, consumable)
   * @param itemId - Container ID
   * @returns Weight breakdown object
   */
  const calculateWeightBreakdown = (itemId: TUUID): WeightBreakdown => {
    return calculateWeightBreakdownV2(itemId, store.getItemById, store.getChildrenOfItem)
  }

  /**
   * Get items by status (filtered from container's children recursively)
   * @param itemId - Container ID
   * @param status - Status to filter by
   * @returns Array of matching items
   */
  const getItemsByStatus = (itemId: TUUID, status: string): IGearItemV2[] => {
    const results: IGearItemV2[] = []

    const collectItems = (currentId: TUUID): void => {
      const current = store.getItemById(currentId)
      if (!current) return

      if (current.itemType === 'item' && current.status === status) {
        results.push(current)
      } else if (current.itemType === 'container') {
        const children = store.getChildrenOfItem(currentId)
        for (const child of children) {
          collectItems(child.id)
        }
      }
    }

    collectItems(itemId)
    return results
  }

  /**
   * Get expired items from a container
   * @param itemId - Container ID
   * @returns Array of expired items
   */
  const getExpiredItems = (itemId: TUUID): IGearItemV2[] => {
    const now = new Date()
    const results: IGearItemV2[] = []

    const collectItems = (currentId: TUUID): void => {
      const current = store.getItemById(currentId)
      if (!current) return

      if (current.itemType === 'item' && current.expirationDate) {
        const expirationDate = new Date(current.expirationDate)
        if (expirationDate < now) {
          results.push(current)
        }
      } else if (current.itemType === 'container') {
        const children = store.getChildrenOfItem(currentId)
        for (const child of children) {
          collectItems(child.id)
        }
      }
    }

    collectItems(itemId)
    return results
  }

  /**
   * Get items expiring soon (within 30 days)
   * @param itemId - Container ID
   * @param daysThreshold - Number of days to consider "soon" (default: 30)
   * @returns Array of items expiring soon
   */
  const getExpiringSoonItems = (itemId: TUUID, daysThreshold: number = 30): IGearItemV2[] => {
    const now = new Date()
    const threshold = new Date(now.getTime() + daysThreshold * 24 * 60 * 60 * 1000)
    const results: IGearItemV2[] = []

    const collectItems = (currentId: TUUID): void => {
      const current = store.getItemById(currentId)
      if (!current) return

      if (current.itemType === 'item' && current.expirationDate) {
        const expirationDate = new Date(current.expirationDate)
        if (expirationDate >= now && expirationDate <= threshold) {
          results.push(current)
        }
      } else if (current.itemType === 'container') {
        const children = store.getChildrenOfItem(currentId)
        for (const child of children) {
          collectItems(child.id)
        }
      }
    }

    collectItems(itemId)
    return results
  }

  return {
    // Weight calculations
    calculateTotalWeight,
    calculateWeightLimitPercentage,
    isWeightLimitExceeded,
    calculateWeightBreakdown,

    // Readiness
    calculateReadinessPercentage,

    // Price calculations
    calculateTotalPrice,
    calculatePriceByCategory,

    // Item statistics
    calculateItemsByPriority,
    getItemsByStatus,
    getExpiredItems,
    getExpiringSoonItems,
  }
}

/**
 * Type for the return value of useContainerCalculationsV2
 * Useful for creating refs or type hints
 */
export type ContainerCalculationsV2 = ReturnType<typeof useContainerCalculationsV2>
