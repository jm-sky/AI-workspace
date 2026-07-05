/**
 * Type converters between V1 (dual model) and V2 (unified model)
 *
 * These are temporary utilities to bridge V1 and V2 types during migration.
 * Eventually all code should use V2 types exclusively.
 */

import type { IGearContainer, IGearItem, TGearItemCategory, TGearItemPriority } from '../types/gear.types'
import type { IGearItemV2, TContainerColor } from '../types/gear.types.v2'

/**
 * Convert V2 container (IGearItemV2 with itemType='container') to V1 IGearContainer
 *
 * Note: This is a lossy conversion - V2 containers don't have a nested items array,
 * so the returned container will have an empty items array. Use getChildrenOfItem()
 * to get actual children.
 */
export function convertV2ContainerToV1(v2Item: IGearItemV2): IGearContainer {
  if (v2Item.itemType !== 'container') {
    throw new Error('Cannot convert non-container V2 item to V1 container')
  }

  const v1Container: IGearContainer = {
    id: v2Item.id,
    name: v2Item.name,
    description: v2Item.description,
    type: v2Item.containerType || 'backpack',
    items: [], // V1 containers have nested items, but V2 uses flat structure
    parentContainerId: v2Item.parentItemId || undefined,
    favorite: v2Item.favorite ?? false,
    color: (v2Item.color as TContainerColor) || undefined,
    weight: v2Item.weight ?? undefined,
    weightUnit: v2Item.weightUnit ?? undefined,
    maxWeight: v2Item.maxWeight ?? undefined,
    maxWeightUnit: v2Item.maxWeightUnit ?? undefined,
    price: v2Item.price ?? undefined,
    currency: v2Item.currency ?? undefined,
    url: v2Item.url ?? undefined,
    brand: v2Item.brand ?? undefined,
    createdAt: v2Item.createdAt,
    updatedAt: v2Item.updatedAt,
    isPublic: v2Item.isPublic ?? false,
    authorId: v2Item.authorId || undefined,
    authorName: v2Item.authorName || undefined,
    averageUserRating: v2Item.averageUserRating ?? undefined,
    showItemImages: v2Item.showItemImages ?? undefined,
  }

  return v1Container
}

/**
 * Convert V2 item (IGearItemV2 with itemType='item') to V1 IGearItem
 */
export function convertV2ItemToV1(v2Item: IGearItemV2): IGearItem {
  if (v2Item.itemType !== 'item') {
    throw new Error('Cannot convert non-item V2 item to V1 item')
  }

  const v1Item: IGearItem = {
    id: v2Item.id,
    name: v2Item.name,
    category: (v2Item.category as TGearItemCategory) ?? 'other',
    quantity: v2Item.quantity ?? 1,
    weight: v2Item.weight ?? 0,
    weightUnit: v2Item.weightUnit ?? 'g',
    status: v2Item.status ?? 'owned',
    priority: (v2Item.priority as TGearItemPriority) ?? 'medium',
    wearable: v2Item.wearable ?? undefined,
    consumable: v2Item.consumable ?? undefined,
    expirationDate: v2Item.expirationDate || undefined,
    price: v2Item.price ?? undefined,
    currency: v2Item.currency ?? undefined,
    url: v2Item.url ?? undefined,
    brand: v2Item.brand ?? undefined,
    color: v2Item.color ?? undefined,
    quality: v2Item.quality ?? undefined,
    notes: v2Item.notes || undefined,
    order: v2Item.orderIndex ?? undefined,
    createdAt: v2Item.createdAt,
    updatedAt: v2Item.updatedAt,
  }

  return v1Item
}

/**
 * Convert V1 container to V2 unified item
 *
 * Note: This flattens the nested structure - V1 container.items are NOT included.
 * They should be converted separately and added with correct parentItemId.
 */
export function convertV1ContainerToV2(
  v1Container: IGearContainer,
  userId: string = 'local-user',
): IGearItemV2 {
  const v2Item: IGearItemV2 = {
    id: v1Container.id,
    userId,
    itemType: 'container',
    parentItemId: v1Container.parentContainerId || null,
    name: v1Container.name,
    description: v1Container.description || null,
    containerType: v1Container.type || 'backpack',
    category: null,
    orderIndex: null, // V1 containers don't have order
    status: 'owned',
    priority: null,
    weight: v1Container.weight ?? null,
    weightUnit: v1Container.weightUnit ?? null,
    maxWeight: v1Container.maxWeight ?? null,
    maxWeightUnit: v1Container.maxWeightUnit ?? null,
    quantity: 1,
    wearable: false,
    consumable: false,
    favorite: v1Container.favorite ?? false,
    hideWhenNested: v1Container.hideWhenNested ?? false,
    price: v1Container.price ?? null,
    currency: v1Container.currency ?? null,
    url: v1Container.url ?? null,
    brand: v1Container.brand ?? null,
    color: v1Container.color ?? null,
    expirationDate: null,
    createdAt: v1Container.createdAt || new Date().toISOString(),
    updatedAt: v1Container.updatedAt || new Date().toISOString(),
    isPublic: v1Container.isPublic ?? false,
    authorId: v1Container.authorId ?? null,
    authorName: v1Container.authorName ?? null,
    averageUserRating: v1Container.averageUserRating ?? null,
    showItemImages: v1Container.showItemImages ?? false,
    quality: null,
    notes: null, // V1 containers don't have notes
  }

  return v2Item
}

/**
 * Convert V1 item to V2 unified item
 */
export function convertV1ItemToV2(
  v1Item: IGearItem,
  containerId: string,
  userId: string = 'local-user',
): IGearItemV2 {
  const v2Item: IGearItemV2 = {
    id: v1Item.id,
    userId,
    itemType: 'item',
    parentItemId: containerId,
    name: v1Item.name,
    description: v1Item.notes ?? null, // V2 uses description, V1 uses notes
    containerType: null,
    category: v1Item.category ?? null,
    orderIndex: v1Item.order ?? null,
    status: v1Item.status || 'owned',
    priority: v1Item.priority ?? null,
    weight: v1Item.weight ?? null,
    weightUnit: v1Item.weightUnit ?? null,
    maxWeight: null,
    maxWeightUnit: null,
    quantity: v1Item.quantity ?? 1,
    wearable: v1Item.wearable ?? false,
    consumable: v1Item.consumable ?? false,
    favorite: false,
    hideWhenNested: false,
    price: v1Item.price ?? null,
    currency: v1Item.currency ?? null,
    url: v1Item.url ?? null,
    brand: v1Item.brand ?? null,
    color: v1Item.color ?? null,
    expirationDate: v1Item.expirationDate ?? null,
    createdAt: v1Item.createdAt || new Date().toISOString(),
    updatedAt: v1Item.updatedAt || new Date().toISOString(),
    isPublic: false,
    authorId: null,
    authorName: null,
    averageUserRating: null,
    showItemImages: false,
    quality: v1Item.quality ?? null,
    notes: v1Item.notes ?? null,
  }

  return v2Item
}

/**
 * Convert array of V2 items to V1 items
 * Only converts items with itemType='item', filters out containers
 */
export function convertV2ItemsArrayToV1(v2Items: IGearItemV2[]): IGearItem[] {
  return v2Items
    .filter(item => item.itemType === 'item')
    .map(item => convertV2ItemToV1(item))
}

/**
 * Convert array of V2 items to V1 containers
 * Only converts items with itemType='container', filters out items
 */
export function convertV2ContainersArrayToV1(v2Items: IGearItemV2[]): IGearContainer[] {
  return v2Items
    .filter(item => item.itemType === 'container')
    .map(item => convertV2ContainerToV1(item))
}
