import { computed, type ComputedRef, type MaybeRefOrGetter, toValue } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IGearItem, TGearWeightUnit } from '../types/gear.types'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import { formatWeightWithPreferredUnit } from '../utils/formatWeight'
import { useGearSettings } from './useGearSettings'

type ItemWithWeight = IGearItem | IItemWithContainer | { weight: number; weightUnit?: TGearWeightUnit | null; quantity: number }

/**
 * Composable for formatting item weight with preferred unit
 * @param itemOrWeight - Item object or weight value
 * @param weightUnit - Weight unit (required if itemOrWeight is a number)
 * @param includeQuantity - Whether to multiply by quantity (default: true)
 * @param fallback - Fallback value if weight is not available (default: '-')
 */
export function useFormattedItemWeight(
  itemOrWeight: MaybeRefOrGetter<ItemWithWeight | number | null | undefined>,
  weightUnit?: MaybeRefOrGetter<TGearWeightUnit | null | undefined>,
  includeQuantity: MaybeRefOrGetter<boolean> = true,
  fallback: MaybeRefOrGetter<string> = '-',
): { formattedWeight: ComputedRef<string> } {
  const { settings: gearSettings } = useGearSettings()
  const { locale } = useI18n()
  const preferredWeightUnit = computed(() => gearSettings.value.preferredWeightUnit)

  const formattedWeight = computed<string>(() => {
    const itemOrWeightValue = toValue(itemOrWeight)
    const includeQuantityValue = toValue(includeQuantity)
    const fallbackValue = toValue(fallback)

    if (!itemOrWeightValue) {
      return fallbackValue
    }

    // If it's an item object
    if (typeof itemOrWeightValue === 'object' && 'weight' in itemOrWeightValue) {
      const item = itemOrWeightValue as ItemWithWeight
      if (!item.weight) {
        return fallbackValue
      }

      const totalWeight = includeQuantityValue ? item.weight * item.quantity : item.weight
      return formatWeightWithPreferredUnit(
        totalWeight,
        item.weightUnit ?? 'g',
        preferredWeightUnit.value,
        locale.value,
      )
    }

    // If it's a number (weight value)
    const weight = itemOrWeightValue as number
    const unit = toValue(weightUnit) ?? 'g'
    if (!unit) {
      return fallbackValue
    }

    return formatWeightWithPreferredUnit(weight, unit, preferredWeightUnit.value, locale.value)
  })

  return { formattedWeight }
}

/**
 * Helper function for formatting item weight (for use in templates)
 * @param item - Item object
 * @param includeQuantity - Whether to multiply by quantity (default: true)
 * @param preferredWeightUnit - Preferred weight unit
 * @param fallback - Fallback value if weight is not available (default: '-')
 */
export function formatItemWeight(
  item: ItemWithWeight | null | undefined,
  includeQuantity: boolean = true,
  preferredWeightUnit: TGearWeightUnit,
  fallback: string = '-',
  locale?: string,
): string {
  if (!item || !item.weight) {
    return fallback
  }

  const totalWeight = includeQuantity ? item.weight * item.quantity : item.weight
  return formatWeightWithPreferredUnit(
    totalWeight,
    item.weightUnit ?? 'g',
    preferredWeightUnit,
    locale,
  )
}

