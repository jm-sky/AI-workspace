import type { TDateTime, TUUID } from '@/shared/types/base.type'

// Typ kontenera - może być domyślny lub własny (custom)
export type TGearContainerType =
  | 'backpack'
  | 'bag'
  | 'pouch'
  | 'box'
  | 'cabinet'
  | 'vehicle'
  | 'shelf'
  | 'drawer'
  | 'case'
  | 'trunk'
  | 'ubranie'
  | 'naczynie'
  | 'other'
  | string // Allow custom container types

// Status przedmiotu
export type TGearItemStatus = 'owned' | 'missing' | 'toBuy'

// Priorytet przedmiotu
export type TGearItemPriority = 'critical' | 'high' | 'medium' | 'low'

// Półka cenowa / jakość
export type TGearItemQuality = 'low' | 'medium' | 'high'

export type TGearWeightAutoMode = 'auto-g-kg' | 'auto-oz-lb'

// Jednostka wagi
export type TGearWeightUnit = 'g' | 'kg' | 'oz' | 'lb' | TGearWeightAutoMode

// Rating type (1-5)
export type TRatingValue = 1 | 2 | 3 | 4 | 5

// Rating type enum
export type TRatingType = 'owner' | 'user'

// Container color options
export type TContainerColor =
  | 'default'  // No color (gray/neutral)
  | 'coyote'
  | 'khaki'
  | 'olive'
  | 'forestGreen'
  | 'tan'
  | 'brown'
  | 'black'
  | 'navy'
  | 'jeans'
  | 'gray'
  | 'orange'

// Kategoria przedmiotu - może być domyślna lub własna (custom)
export type TGearItemCategory =
  | 'water'
  | 'food'
  | 'shelter'
  | 'fire'
  | 'firstAid'
  | 'blades'
  | 'tools'
  | 'light'
  | 'navigation'
  | 'communication'
  | 'clothing'
  | 'hygiene'
  | 'other'
  | string // Allow custom categories

// Constants for item categories (default categories only)
export const GEAR_ITEM_CATEGORIES: TGearItemCategory[] = [
  'water',
  'food',
  'shelter',
  'fire',
  'firstAid',
  'blades',
  'tools',
  'light',
  'navigation',
  'communication',
  'clothing',
  'hygiene',
  'other',
]

// Constants for item qualities
export const GEAR_ITEM_QUALITIES: TGearItemQuality[] = ['low', 'medium', 'high']

// Shelf life unit type
export type TShelfLifeUnit = 'days' | 'months' | 'years'

// Shelf life interface
export interface IShelfLife {
  value: number
  unit: TShelfLifeUnit
}

// Container information included in item responses
export interface IContainerInfo {
  id: TUUID
  name: string
  type: TGearContainerType
  color?: TContainerColor | null
}

// Pojedynczy przedmiot
export interface IGearItem {
  id: TUUID
  linkedItemId?: TUUID | null // Reference to original item when linked (future-ready for backend)
  catalogueItemId?: TUUID | null // Reference to global catalogue item (if item was added from catalogue)
  name: string
  category: TGearItemCategory
  quantity: number
  weight: number // wartość wagi
  weightUnit: TGearWeightUnit // jednostka wagi (g lub kg)
  notes?: string | null
  expirationDate?: TDateTime | null // ISO date string
  shelfLife?: IShelfLife | null // Shelf life period (e.g., { value: 10, unit: 'years' })
  priority: TGearItemPriority
  status: TGearItemStatus
  containerId?: TUUID | null // Reference to a nested container (if this item is a container)
  container?: IContainerInfo | null // Information about parent container where item is located (from API)
  // Extended fields
  price?: number | null // Price in currency (optional)
  currency?: string | null // Currency code (PLN, USD, EUR, GBP, etc.)
  url?: string | null // Link to product, review, etc.
  brand?: string | null // Manufacturer/brand
  color?: string | null // Item color
  quality?: TGearItemQuality | null // Price tier / quality
  wearable?: boolean | null // Item is worn/carried on person (e.g., clothing, watch)
  consumable?: boolean | null // Item is consumed/used up (e.g., food, medicine, fuel)
  order?: number | null // Manual order for items within container (lower numbers appear first)
  showOnContainer?: boolean | null // Show item image in container view gallery (Implementation postponed - use container.showItemImages instead)
  primaryImageUrl?: string | null // URL of the primary image for the item
  promoteCount?: number // Number of promotions for this item (for promotion to catalogue)
  createdAt: TDateTime
  updatedAt: TDateTime
}

// Kontener (plecak/zestaw)
export interface IGearContainer {
  id: TUUID
  name: string
  description?: string | null
  type: TGearContainerType
  color?: TContainerColor | null  // Optional, defaults to 'default'
  parentContainerId?: TUUID | null // Parent container ID (if this container is nested)
  hideWhenNested?: boolean | null // Hide from main list when nested in another container
  isPublic: boolean // Whether container is publicly visible
  isHiddenByReports?: boolean | null // Whether container is hidden from public views due to reports
  favorite: boolean // Whether container is marked as favorite
  authorName?: string | null // Author name (only for public containers)
  authorId?: TUUID | null // Author user ID (only for public containers)
  // Extended fields
  brand?: string | null // Manufacturer/brand
  price?: number | null // Price in currency (optional)
  currency?: string | null // Currency code (PLN, USD, EUR, GBP, etc.)
  weight?: number | null // Container weight value
  weightUnit?: TGearWeightUnit | null // Container weight unit (g or kg)
  maxWeight?: number | null // Maximum weight limit value
  maxWeightUnit?: TGearWeightUnit | null // Maximum weight unit (g or kg)
  url?: string | null // Link to product, review, etc.
  showItemImages?: boolean | null // Show item images in container view (only items with primary image)
  // Rating fields
  ownerRating?: TRatingValue | null // Owner's rating (1-5)
  userRating?: TRatingValue | null // Current user's rating (if logged in)
  averageUserRating?: number | null // Average of all user ratings
  userRatingCount?: number // Number of user ratings
  items: IGearItem[]
  createdAt: TDateTime
  updatedAt: TDateTime
}

// DTO dla tworzenia kontenera
export interface ICreateContainerDto {
  id?: TUUID | null // Optional UUID for import/update workflow (when UUID is provided in markdown export)
  name: string
  description?: string | null
  type: TGearContainerType
  color?: TContainerColor | null
  parentContainerId?: TUUID | null
  hideWhenNested?: boolean | null
  isPublic?: boolean | null
  favorite?: boolean | null
  brand?: string | null
  price?: number | null
  currency?: string | null // Currency code (PLN, USD, EUR, GBP, etc.)
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  maxWeight?: number | null
  maxWeightUnit?: TGearWeightUnit | null
  url?: string | null
  showItemImages?: boolean | null
}

// DTO dla aktualizacji kontenera
export interface IUpdateContainerDto {
  name?: string | null
  description?: string | null
  type?: TGearContainerType | null
  color?: TContainerColor | null
  parentContainerId?: TUUID | null
  hideWhenNested?: boolean | null
  isPublic?: boolean | null
  favorite?: boolean | null
  brand?: string | null
  price?: number | null
  currency?: string | null
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  maxWeight?: number | null
  maxWeightUnit?: TGearWeightUnit | null
  url?: string | null
  showItemImages?: boolean | null
}

// DTO dla tworzenia przedmiotu
export interface ICreateItemDto {
  id?: TUUID | null // Optional UUID for import/update workflow (when UUID is provided in markdown export)
  linkedItemId?: TUUID | null // Reference to original item when linking
  catalogueItemId?: TUUID | null // Reference to global catalogue item (if item was added from catalogue)
  name: string
  category: TGearItemCategory
  quantity: number
  weight: number
  weightUnit: TGearWeightUnit
  notes?: string | null
  expirationDate?: TDateTime | null
  shelfLife?: IShelfLife | null // Shelf life period (e.g., { value: 10, unit: 'years' })
  priority: TGearItemPriority
  status: TGearItemStatus
  containerId?: TUUID | null // Reference to a nested container (if this item is a container)
  price?: number | null
  currency?: string | null // Currency code (PLN, USD, EUR, GBP, etc.)
  url?: string | null
  brand?: string | null
  color?: string | null
  quality?: TGearItemQuality | null
  wearable?: boolean | null
  consumable?: boolean | null
  order?: number | null
  showOnContainer?: boolean | null
}

// DTO dla aktualizacji przedmiotu
export interface IUpdateItemDto {
  name?: string | null
  category?: TGearItemCategory | null
  quantity?: number | null
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  notes?: string | null
  expirationDate?: TDateTime | null
  shelfLife?: IShelfLife | null // Shelf life period (e.g., { value: 10, unit: 'years' })
  priority?: TGearItemPriority | null
  status?: TGearItemStatus | null
  containerId?: TUUID | null // Reference to a nested container (if this item is a container)
  price?: number | null
  currency?: string | null
  url?: string | null
  brand?: string | null
  color?: string | null
  quality?: TGearItemQuality | null
  wearable?: boolean | null
  consumable?: boolean | null
  order?: number | null
  showOnContainer?: boolean | null
  primaryImageUrl?: string | null // URL of the primary image for the item
}

// Service interface for gear operations
// This interface defines the common contract for both localStorage and API implementations
export interface IGearService {
  // Container operations (CRUD)
  createContainer(data: ICreateContainerDto): Promise<IGearContainer>
  getContainers(skip?: number, limit?: number): Promise<IGearContainer[]>
  getContainer(id: TUUID): Promise<IGearContainer>
  updateContainer(id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer>
  deleteContainer(id: TUUID): Promise<void>

  // Item operations (CRUD)
  createItem(containerId: TUUID, data: ICreateItemDto): Promise<IGearItem>
  getItems(containerId: TUUID, skip?: number, limit?: number): Promise<IGearItem[]>
  getItem(itemId: TUUID): Promise<IGearItem>
  updateItem(itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem>
  deleteItem(itemId: TUUID): Promise<void>

  // Statistics operations (from API or calculated locally)
  getContainerWeight(containerId: TUUID): Promise<{ grams: number; kilograms: number }>
  getContainerReadiness(containerId: TUUID): Promise<{
    totalItems: number
    ownedItems: number
    missingItems: number
    toBuyItems: number
    readinessPercentage: number
  }>
}

// Extended interface for localStorage-specific operations
// These methods are only available in localStorage implementation
// API implementation may throw "Not implemented" or provide fallback behavior
export interface IGearServiceExtended extends IGearService {
  // Additional container operations (localStorage-specific)
  getAllContainers(): Promise<IGearContainer[]>
  getRootContainers(): Promise<IGearContainer[]>
  getNestedContainers(containerId: TUUID): Promise<IGearContainer[]>
  deleteAllContainers(): Promise<void>

  // Additional item operations (localStorage-specific)
  getItemById(containerId: TUUID, itemId: TUUID): Promise<IGearItem | undefined>

  // Business logic operations (calculated locally)
  calculateTotalWeight(containerId: TUUID): Promise<number>
  calculateReadinessPercentage(containerId: TUUID): Promise<number>
  calculateWeightLimitPercentage(containerId: TUUID): Promise<number | null>
  isWeightLimitExceeded(containerId: TUUID): Promise<boolean>
  getItemsByStatus(containerId: TUUID, status: TGearItemStatus): Promise<IGearItem[]>
  getExpiredItems(containerId: TUUID): Promise<IGearItem[]>
  getExpiringSoonItems(containerId: TUUID, days?: number): Promise<IGearItem[]>
  moveItem(containerId: TUUID, itemId: TUUID, newContainerId: TUUID): Promise<void>
  cloneContainer(
    containerId: TUUID,
    options: {
      newName: string
      includeNestedContainers?: boolean
      includePrices?: boolean
    },
  ): Promise<IGearContainer>
  // Import/Export operations (localStorage-specific)
  exportData(): Promise<string>
  importData(json: string): Promise<void>
}

export interface IGearItemService {
  createItem(containerId: TUUID, data: ICreateItemDto): Promise<IGearItem>
  getItems(containerId: TUUID, skip?: number, limit?: number): Promise<IGearItem[]>
  getItem(itemId: TUUID): Promise<IGearItem>
  getItemFromContainer(containerId: TUUID, itemId: TUUID): Promise<IGearItem | undefined>
  updateItem(itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem>
  moveItem(itemId: TUUID, targetContainerId: TUUID): Promise<IGearItem>
  deleteItem(itemId: TUUID): Promise<void>
  batchUpdateOrder(items: IGearItem[]): Promise<IGearItem[]>
}
