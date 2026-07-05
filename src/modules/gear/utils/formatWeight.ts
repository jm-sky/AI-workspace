import type { TGearWeightAutoMode, TGearWeightUnit } from '../types/gear.types'
import { GRAMS_PER_KILOGRAM, GRAMS_PER_OUNCE, GRAMS_PER_POUND, WEIGHT_DECIMAL_PLACES } from './constants'
import { isAutoWeightUnit } from './weightUnits'

const DEFAULT_LOCALE_ID = 'en-US' // Use en-US for consistent formatting (tests and international use)

/**
 * Converts weight to grams for internal calculations
 * @param weight - Weight value
 * @param unit - Weight unit (g, kg, oz, or lb)
 * @returns Weight in grams
 */
export function convertToGrams(weight: number, unit: TGearWeightUnit): number {
  switch (unit) {
    case 'kg':
      return weight * GRAMS_PER_KILOGRAM
    case 'lb':
      return weight * GRAMS_PER_POUND
    case 'oz':
      return weight * GRAMS_PER_OUNCE
    case 'g':
    default:
      return weight
  }
}

/**
 * Converts weight from grams to specified unit
 * @param weightInGrams - Weight in grams
 * @param targetUnit - Target unit (g, kg, oz, or lb)
 * @returns Weight in target unit
 */
export function convertFromGrams(weightInGrams: number, targetUnit: TGearWeightUnit): number {
  switch (targetUnit) {
    case 'kg':
      return weightInGrams / GRAMS_PER_KILOGRAM
    case 'lb':
      return weightInGrams / GRAMS_PER_POUND
    case 'oz':
      return weightInGrams / GRAMS_PER_OUNCE
    case 'g':
    default:
      return weightInGrams
  }
}

/**
 * Resolves auto weight unit to actual unit based on weight value
 * @param weightInGrams - Weight in grams
 * @param autoMode - Auto mode ('auto-g-kg' or 'auto-oz-lb')
 * @returns Resolved weight unit (g, kg, oz, or lb)
 */
export function resolveAutoWeightUnit(weightInGrams: number, autoMode: TGearWeightAutoMode): TGearWeightUnit {
  const THRESHOLD_KG = GRAMS_PER_KILOGRAM // 1 kg = 1000g

  if (autoMode === 'auto-g-kg') {
    return weightInGrams < THRESHOLD_KG ? 'g' : 'kg'
  } else { // auto-oz-lb
    return weightInGrams < THRESHOLD_KG ? 'oz' : 'lb'
  }
}

/**
 * Formats a number with thousand separator based on locale
 * @param value - Number to format
 * @param locale - Locale string (defaults to 'en-US')
 * @param unit - Weight unit to determine decimal places (g uses 0, others use WEIGHT_DECIMAL_PLACES)
 * @returns Formatted number string with thousand separator
 */
function formatNumberWithSeparator(value: number, locale: string = DEFAULT_LOCALE_ID, unit?: TGearWeightUnit): string {
  // For kg, lb, oz: always show 2 decimal places. For g: show exact value with decimals if needed
  if (unit === 'g') {
    // For grams, don't use thousand separator
    // Show exact value - if it's a whole number, show without decimals, otherwise show decimals
    if (value % 1 === 0) {
      return value.toFixed(0)
    } else {
      // Show with decimals but remove trailing zeros
      return value.toString()
    }
  }

  const minFractionDigits = WEIGHT_DECIMAL_PLACES
  const maxFractionDigits = WEIGHT_DECIMAL_PLACES

  const formatter = new Intl.NumberFormat(locale, {
    minimumFractionDigits: minFractionDigits,
    maximumFractionDigits: maxFractionDigits,
  })
  return formatter.format(value)
}

/**
 * Formats weight value with unit to a display string
 * @param weight - Weight value
 * @param unit - Weight unit (g, kg, oz, or lb)
 * @param locale - Optional locale for formatting (defaults to 'en-US')
 * @returns Formatted weight string (e.g., "1.50 kg", "1 500 g", "16 oz", "2.5 lb")
 */
export function formatWeight(weight: number, unit: TGearWeightUnit, locale?: string): string {
  const effectiveLocale = locale ?? DEFAULT_LOCALE_ID
  const formattedValue = formatNumberWithSeparator(weight, effectiveLocale, unit)

  switch (unit) {
    case 'kg':
      return `${formattedValue} kg`
    case 'lb':
      return `${formattedValue} lb`
    case 'oz':
      return `${formattedValue} oz`
    case 'g':
    default:
      return `${formattedValue} g`
  }
}

/**
 * Formats weight in grams to a formatted string (for backward compatibility)
 * Automatically chooses best unit (kg if >= 1000g, otherwise g)
 * @param weightInGrams - Weight in grams
 * @param locale - Optional locale for formatting (defaults to 'en-US')
 * @returns Formatted weight string (e.g., "1.50 kg" or "500 g")
 */
export function formatWeightFromGrams(weightInGrams: number, locale?: string): string {
  const effectiveLocale = locale ?? DEFAULT_LOCALE_ID
  if (weightInGrams >= GRAMS_PER_KILOGRAM) {
    const weightInKg = weightInGrams / GRAMS_PER_KILOGRAM
    const formattedValue = formatNumberWithSeparator(weightInKg, effectiveLocale, 'kg')
    return `${formattedValue} kg`
  }
  const formattedValue = formatNumberWithSeparator(weightInGrams, effectiveLocale, 'g')
  return `${formattedValue} g`
}

/**
 * Formats weight in grams to a formatted string using preferred unit
 * Supports auto modes (auto-g-kg, auto-oz-lb) which automatically choose unit based on weight
 * @param weightInGrams - Weight in grams
 * @param preferredUnit - Preferred weight unit (g, kg, oz, lb, auto-g-kg, or auto-oz-lb)
 * @param locale - Optional locale for formatting (defaults to 'en-US')
 * @returns Formatted weight string (e.g., "1.50 kg", "1 500 g", "16 oz", "2.5 lb")
 */
export function formatWeightToPreferredUnit(weightInGrams: number, preferredUnit: TGearWeightUnit, locale?: string): string {
  // Handle auto modes
  if (isAutoWeightUnit(preferredUnit)) {
    const resolvedUnit = resolveAutoWeightUnit(weightInGrams, preferredUnit)
    return formatWeightToPreferredUnit(weightInGrams, resolvedUnit, locale)
  }

  const effectiveLocale = locale ?? DEFAULT_LOCALE_ID

  // Handle regular units
  switch (preferredUnit) {
    case 'kg': {
      const weightInKg = weightInGrams / GRAMS_PER_KILOGRAM
      const formattedValue = formatNumberWithSeparator(weightInKg, effectiveLocale, 'kg')
      return `${formattedValue} kg`
    }
    case 'lb': {
      const weightInLb = weightInGrams / GRAMS_PER_POUND
      const formattedValue = formatNumberWithSeparator(weightInLb, effectiveLocale, 'lb')
      return `${formattedValue} lb`
    }
    case 'oz': {
      const weightInOz = weightInGrams / GRAMS_PER_OUNCE
      const formattedValue = formatNumberWithSeparator(weightInOz, effectiveLocale, 'oz')
      return `${formattedValue} oz`
    }
    case 'g':
    default: {
      const formattedValue = formatNumberWithSeparator(weightInGrams, effectiveLocale, 'g')
      return `${formattedValue} g`
    }
  }
}

/**
 * Formats weight value with original unit, converting to preferred unit for display
 * @param weight - Weight value
 * @param originalUnit - Original weight unit (g, kg, oz, or lb)
 * @param preferredUnit - Preferred weight unit (g, kg, oz, lb, auto-g-kg, or auto-oz-lb)
 * @param locale - Optional locale for formatting (defaults to 'pl-PL')
 * @returns Formatted weight string in preferred unit
 */
export function formatWeightWithPreferredUnit(weight: number, originalUnit: TGearWeightUnit, preferredUnit: TGearWeightUnit, locale?: string): string {
  // Convert to grams first
  const weightInGrams = convertToGrams(weight, originalUnit)
  // Then format to preferred unit
  return formatWeightToPreferredUnit(weightInGrams, preferredUnit, locale)
}

