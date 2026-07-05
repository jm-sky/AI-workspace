/**
 * Weight units utilities
 * Single source of truth for weight units enum and validation
 */
import { z } from 'zod'
import type { TGearWeightUnit } from '../types/gear.types'

/**
 * Supported weight units as array for iteration
 * Used in forms (items/containers) - does NOT include auto options
 */
export const WEIGHT_UNITS = ['g', 'kg', 'oz', 'lb'] as const

/**
 * Preferred weight units including auto options
 * Used in user preferences settings
 */
export const PREFERRED_WEIGHT_UNITS = ['g', 'kg', 'oz', 'lb', 'auto-g-kg', 'auto-oz-lb'] as const

/**
 * Zod enum for weight unit validation
 * Use this for form validation schemas (items/containers)
 */
export const weightUnitEnum = z.enum(WEIGHT_UNITS)

/**
 * Zod enum for preferred weight unit validation
 * Use this for user preferences settings (includes auto options)
 */
export const preferredWeightUnitEnum = z.enum(PREFERRED_WEIGHT_UNITS)

/**
 * Type guard to check if a string is a valid basic weight unit (for forms)
 * Returns true only for basic units (g, kg, oz, lb), not auto options
 */
export function isWeightUnit(value: string): value is 'g' | 'kg' | 'oz' | 'lb' {
  return WEIGHT_UNITS.includes(value as 'g' | 'kg' | 'oz' | 'lb')
}

/**
 * Type guard to check if a string is a valid preferred weight unit (including auto options)
 */
export function isPreferredWeightUnit(value: string): value is TGearWeightUnit {
  return PREFERRED_WEIGHT_UNITS.includes(value as TGearWeightUnit)
}

/**
 * Check if a weight unit is an auto option
 */
export function isAutoWeightUnit(unit: TGearWeightUnit): unit is 'auto-g-kg' | 'auto-oz-lb' {
  return unit === 'auto-g-kg' || unit === 'auto-oz-lb'
}

/**
 * Convert TGearWeightUnit to basic weight unit (for forms)
 * Auto options are converted to their default unit (auto-g-kg -> g, auto-oz-lb -> oz)
 * @param unit - Weight unit (may include auto options)
 * @returns Basic weight unit (g, kg, oz, or lb)
 */
export function toBasicWeightUnit(unit: TGearWeightUnit | null | undefined): 'g' | 'kg' | 'oz' | 'lb' {
  if (!unit) return 'g'
  if (unit === 'auto-g-kg') return 'g'
  if (unit === 'auto-oz-lb') return 'oz'
  return unit
}

