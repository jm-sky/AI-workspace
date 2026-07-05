/**
 * Constants for gear module
 */

import type { TContainerColor, TGearItemCategory, TGearItemPriority, TGearItemStatus } from '../types/gear.types'

// Pagination
export const DEFAULT_PAGINATION_LIMIT = 100
export const DEFAULT_PAGINATION_SKIP = 0

// Weight conversion
export const GRAMS_PER_KILOGRAM = 1000
export const GRAMS_PER_OUNCE = 28.3495
export const GRAMS_PER_POUND = 453.592
export const WEIGHT_DECIMAL_PLACES = 2
export const DEFAULT_ITEM_WEIGHT_GRAMS = 100

// Percentage calculations
export const PERCENTAGE_MULTIPLIER = 100

// Readiness thresholds (percentages)
export const READINESS_EXCELLENT_THRESHOLD = 81
export const READINESS_GOOD_THRESHOLD = 51

// Expiration warnings (days)
export const EXPIRATION_WARNING_DAYS = 7
export const EXPIRATION_SOON_DAYS = 30

// Time conversion
export const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24

export const DEFAULT_ITEM_CATEGORY: TGearItemCategory = 'other'
export const DEFAULT_ITEM_COLOR: TContainerColor = 'default'
export const DEFAULT_ITEM_STATUS: TGearItemStatus = 'owned'
export const DEFAULT_ITEM_PRIORITY: TGearItemPriority = 'medium'
export const DEFAULT_ITEM_QUANTITY = 1
export const DEFAULT_ITEM_WEIGHT = 0
