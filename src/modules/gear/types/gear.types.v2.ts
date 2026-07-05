/**
 * Unified gear types (V2)
 *
 * This module defines types for the unified gear model where containers are items
 * with itemType='container'. This replaces the dual-model approach (IGearContainer + IGearItem).
 *
 * Key Changes:
 * - Single unified type: IGearItemV2 (replaces IGearContainer + IGearItem)
 * - Type discriminator: itemType ('container' | 'item')
 * - Unified nesting: parentItemId (replaces parentContainerId + containerId)
 * - Optional children array for tree structure
 *
 * @module gear/types/v2
 */

import type {
  TContainerColor,
  TGearContainerType,
  TGearItemCategory,
  TGearItemPriority,
  TGearItemQuality,
  TGearItemStatus,
  TGearWeightUnit,
  TRatingType,
  TRatingValue,
} from './gear.types'
import {
  GEAR_ITEM_CATEGORIES,
  GEAR_ITEM_QUALITIES,
} from './gear.types'
import type { TDateTime, TUUID } from '@/shared/types/base.type'

// Re-export common types from V1 (unchanged)
export type {
  TContainerColor,
  TGearContainerType,
  TGearItemCategory,
  TGearItemPriority,
  TGearItemQuality,
  TGearItemStatus,
  TGearWeightUnit,
  TRatingType,
  TRatingValue,
}

export {
  GEAR_ITEM_CATEGORIES,
  GEAR_ITEM_QUALITIES,
}

// Type discriminator for unified model
export type TGearItemType = 'container' | 'item'

/**
 * Shelf life configuration
 * Represents the period before item expires when purchased/created
 */
export interface IShelfLife {
  value: number
  unit: 'days' | 'months' | 'years'
}

/**
 * Unified gear item interface (V2)
 *
 * This interface represents both containers and regular items.
 * Use itemType to discriminate between types:
 * - itemType='container': Container-specific fields are populated
 * - itemType='item': Item-specific fields are populated
 *
 * Field Mapping from V1:
 * - IGearContainer.id → id (preserved)
 * - IGearContainer.parentContainerId → parentItemId
 * - IGearContainer.type → containerType
 * - IGearItem.id → id (preserved)
 * - IGearItem.containerId → parentItemId
 * - IGearItem.order → orderIndex (renamed)
 * - IGearItem.containerId (nested) → REMOVED (legacy)
 */
export interface IGearItemV2 {
  // Core identity
  id: TUUID
  userId: TUUID
  itemType: TGearItemType

  // Unified nesting (replaces parentContainerId + containerId)
  parentItemId?: TUUID | null

  // Common fields (from both old types)
  name: string
  description?: string | null
  brand?: string | null
  price?: number | null
  currency?: string | null
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  url?: string | null
  color?: TContainerColor | string | null
  notes?: string | null

  // Container-specific fields (populated when itemType='container')
  containerType?: TGearContainerType | null
  maxWeight?: number | null
  maxWeightUnit?: TGearWeightUnit | null
  hideWhenNested?: boolean | null
  isPublic?: boolean | null
  favorite?: boolean | null
  showItemImages?: boolean | null

  // Container rating fields (only for containers)
  ownerRating?: TRatingValue | null
  userRating?: TRatingValue | null
  averageUserRating?: number | null
  userRatingCount?: number

  // Container author fields (only for public containers)
  authorName?: string | null
  authorId?: TUUID | null

  // Content moderation (only for public containers)
  isHiddenByReports?: boolean | null

  // Item-specific fields (populated when itemType='item')
  category?: TGearItemCategory | null
  quantity?: number | null
  status?: TGearItemStatus | null
  priority?: TGearItemPriority | null
  expirationDate?: TDateTime | null
  shelfLife?: IShelfLife | null
  quality?: TGearItemQuality | null
  wearable?: boolean | null
  consumable?: boolean | null
  orderIndex?: number | null
  showOnContainer?: boolean | null
  promoteCount?: number | null

  // Item image fields
  primaryImageUrl?: string | null

  // Linking fields
  linkedItemId?: TUUID | null
  catalogueItemId?: TUUID | null

  // Metadata
  createdAt: TDateTime
  updatedAt: TDateTime

  // Optional: nested children (for tree structure)
  children?: IGearItemV2[]
}

/**
 * Type guard: Check if item is a container
 */
export function isContainer(item: IGearItemV2): boolean {
  return item.itemType === 'container'
}

/**
 * Type guard: Check if item is a regular item
 */
export function isRegularItem(item: IGearItemV2): boolean {
  return item.itemType === 'item'
}

/**
 * Type guard: Check if item is a root item (no parent)
 */
export function isRootItem(item: IGearItemV2): boolean {
  return !item.parentItemId
}

/**
 * DTO for creating a gear item (V2)
 */
export interface ICreateGearItemV2Dto {
  id?: TUUID | null
  itemType: TGearItemType
  parentItemId?: TUUID | null

  // Common fields
  name: string
  description?: string | null
  brand?: string | null
  price?: number | null
  currency?: string | null
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  url?: string | null
  color?: TContainerColor | string | null
  notes?: string | null

  // Container-specific (required if itemType='container')
  containerType?: TGearContainerType | null
  maxWeight?: number | null
  maxWeightUnit?: TGearWeightUnit | null
  hideWhenNested?: boolean | null
  isPublic?: boolean | null
  isHiddenByReports?: boolean | null
  favorite?: boolean | null
  showItemImages?: boolean | null

  // Item-specific (required if itemType='item')
  category?: TGearItemCategory | null
  quantity?: number | null
  status?: TGearItemStatus | null
  priority?: TGearItemPriority | null
  expirationDate?: TDateTime | null
  shelfLife?: IShelfLife | null
  quality?: TGearItemQuality | null
  wearable?: boolean | null
  consumable?: boolean | null
  orderIndex?: number | null
  showOnContainer?: boolean | null
  promoteCount?: number | null

  // Linking fields
  linkedItemId?: TUUID | null
  catalogueItemId?: TUUID | null
}

/**
 * DTO for updating a gear item (V2)
 */
export interface IUpdateGearItemV2Dto {
  // Core fields (itemType cannot be changed after creation)
  parentItemId?: TUUID | null

  // Common fields
  name?: string | null
  description?: string | null
  brand?: string | null
  price?: number | null
  currency?: string | null
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  url?: string | null
  color?: TContainerColor | string | null
  notes?: string | null

  // Container-specific
  containerType?: TGearContainerType | null
  maxWeight?: number | null
  maxWeightUnit?: TGearWeightUnit | null
  hideWhenNested?: boolean | null
  isPublic?: boolean | null
  isHiddenByReports?: boolean | null
  favorite?: boolean | null
  showItemImages?: boolean | null

  // Item-specific
  category?: TGearItemCategory | null
  quantity?: number | null
  status?: TGearItemStatus | null
  priority?: TGearItemPriority | null
  expirationDate?: TDateTime | null
  shelfLife?: IShelfLife | null
  quality?: TGearItemQuality | null
  wearable?: boolean | null
  consumable?: boolean | null
  orderIndex?: number | null
  showOnContainer?: boolean | null
  promoteCount?: number | null

  // Linking fields
  linkedItemId?: TUUID | null
  catalogueItemId?: TUUID | null
}

/**
 * Query filters for fetching gear items (V2)
 */
export interface IGearItemFiltersV2 {
  itemType?: 'container' | 'item' | 'all'
  parentItemId?: TUUID | null
  isPublic?: boolean | null
  favorite?: boolean | null
  status?: TGearItemStatus | null
  priority?: TGearItemPriority | null
  category?: TGearItemCategory | null
}

/**
 * Batch order update item
 */
export interface IBatchOrderUpdateItem {
  id: TUUID
  orderIndex: number
}

/**
 * Service interface for gear items (V2)
 */
export interface IGearItemServiceV2 {
  // Create
  createItem(data: ICreateGearItemV2Dto): Promise<IGearItemV2>

  // Read
  getItems(filters?: IGearItemFiltersV2): Promise<IGearItemV2[]>
  getItemById(id: TUUID): Promise<IGearItemV2 | undefined>
  getChildren(parentItemId: TUUID): Promise<IGearItemV2[]>

  // Update
  updateItem(id: TUUID, data: IUpdateGearItemV2Dto): Promise<IGearItemV2>
  batchUpdateOrder(items: IBatchOrderUpdateItem[]): Promise<IGearItemV2[]>
  moveItem(itemId: TUUID, targetParentId: TUUID | null): Promise<IGearItemV2>

  // Delete
  deleteItem(id: TUUID): Promise<void>
}
