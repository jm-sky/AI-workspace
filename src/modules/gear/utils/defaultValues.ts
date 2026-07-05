import type { ICreateItemDto } from '../types/gear.types'

/**
 * Default values for creating new items
 * These values are pre-filled in the form to speed up item creation
 */
export const DEFAULT_ITEM_VALUES: ICreateItemDto = {
  name: '',
  quantity: 1,
  weight: 0.1, // 0.1 kg (100g) - reasonable default
  weightUnit: 'kg',
  status: 'owned',
  priority: 'medium',
  category: 'other',
}

/**
 * Get default values for a new item
 * @returns Default values object that can be spread into form initial values
 */
export function getDefaultItemValues(): ICreateItemDto {
  return { ...DEFAULT_ITEM_VALUES }
}

