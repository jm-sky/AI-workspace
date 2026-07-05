import type { TContainerColor, TGearItemCategory, TGearItemQuality, TGearWeightUnit } from './gear.types'
import type { TDateTime, TUUID } from '@/shared/types/base.type'

// Price tier for catalogue items
export type TCataloguePriceTier = 'low' | 'medium' | 'high'

// Shop link for catalogue items
export interface ICatalogueShop {
  url: string
  name?: string
  variant?: string
  price?: number
  currency?: string
  updatedAt?: TDateTime
}

// Global catalogue item (template for creating gear items)
export interface IGlobalCatalogueItem {
  id: TUUID
  version: number // Version number for tracking updates
  name: string
  category: TGearItemCategory
  weight: number
  weightUnit: TGearWeightUnit
  description?: string | null
  brand?: string | null
  model?: string | null
  priceTier?: TCataloguePriceTier | null
  price?: number | null
  currency?: string | null
  quality?: TGearItemQuality | null
  url?: string | null
  color?: TContainerColor | null
  shops?: ICatalogueShop[]
  isActive: boolean
  createdBy?: TUUID | null
  creatorName?: string | null
  createdAt: TDateTime
  updatedAt: TDateTime
  primaryImageUrl?: string | null
}

// Search parameters for catalogue items
export interface ICatalogueSearchParams {
  query?: string | null
  category?: TGearItemCategory | null
  brand?: string | null
  priceTier?: TCataloguePriceTier | null
  quality?: TGearItemQuality | null
  isActive?: boolean | null
  skip?: number
  limit?: number
}

// Catalogue item creation data
export interface ICatalogueItemCreate {
  name: string
  category: TGearItemCategory
  weight: number
  weightUnit: TGearWeightUnit
  description?: string | null
  brand?: string | null
  model?: string | null
  priceTier?: TCataloguePriceTier | null
  price?: number | null
  currency?: string | null
  quality?: TGearItemQuality | null
  url?: string | null
  color?: string | null
  shops?: ICatalogueShop[]
}

// Catalogue item update data
export interface ICatalogueItemUpdate {
  name?: string | null
  category?: TGearItemCategory | null
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  description?: string | null
  brand?: string | null
  model?: string | null
  priceTier?: TCataloguePriceTier | null
  price?: number | null
  currency?: string | null
  quality?: TGearItemQuality | null
  url?: string | null
  color?: string | null
  shops?: ICatalogueShop[]
  isActive?: boolean | null
}

// Type aliases for consistency with API
export type IGlobalCatalogueItemCreate = ICatalogueItemCreate
export type IGlobalCatalogueItemUpdate = ICatalogueItemUpdate
