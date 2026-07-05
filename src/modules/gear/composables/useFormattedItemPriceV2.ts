import { computed, type ComputedRef, type MaybeRefOrGetter, toValue } from 'vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { DEFAULT_ITEM_QUANTITY } from '../utils/constants'
import { formatCurrency, getCurrency } from '../utils/currencyFormatter'
import { useGearSettings } from './useGearSettings'

/**
 * Composable for formatting item price with currency (V2)
 * @param itemOrPrice - Item object or price value
 * @param currency - Currency code (required if itemOrPrice is a number)
 * @param includeQuantity - Whether to multiply by quantity (default: false)
 * @param fallback - Fallback value if price is not available (default: '-')
 */
export function useFormattedItemPriceV2(
  itemOrPrice: MaybeRefOrGetter<IGearItemV2 | number | null | undefined>,
  currency?: MaybeRefOrGetter<string | null | undefined>,
  includeQuantity: MaybeRefOrGetter<boolean> = false,
  fallback: MaybeRefOrGetter<string> = '-',
): { formattedPrice: ComputedRef<string> } {
  const { defaultCurrency } = useGearSettings()

  const formattedPrice = computed<string>(() => {
    const itemOrPriceValue = toValue(itemOrPrice)
    const includeQuantityValue = toValue(includeQuantity)
    const fallbackValue = toValue(fallback)

    if (!itemOrPriceValue) {
      return fallbackValue
    }

    // If it's an item object
    if (typeof itemOrPriceValue === 'object' && 'price' in itemOrPriceValue) {
      const item = itemOrPriceValue as IGearItemV2
      if (item.price == null) {
        return fallbackValue
      }

      const quantity = item.quantity ?? DEFAULT_ITEM_QUANTITY
      const totalPrice = includeQuantityValue ? item.price * quantity : item.price
      const itemCurrency = getCurrency(item.currency ?? null, defaultCurrency.value)
      return formatCurrency(totalPrice, itemCurrency)
    }

    // If it's a number (price value)
    const price = itemOrPriceValue as number
    const currencyCode = toValue(currency)
    if (!currencyCode) {
      return fallbackValue
    }

    const finalCurrency = getCurrency(currencyCode, defaultCurrency.value)
    return formatCurrency(price, finalCurrency)
  })

  return { formattedPrice }
}

/**
 * Helper function for formatting item price (for use in templates) (V2)
 * @param item - Item object
 * @param includeQuantity - Whether to multiply by quantity (default: false)
 * @param defaultCurrency - Default currency code
 * @param fallback - Fallback value if price is not available (default: '-')
 */
export function formatItemPriceV2(
  item: IGearItemV2 | null | undefined,
  includeQuantity: boolean = false,
  defaultCurrency: string,
  fallback: string = '-',
): string {
  if (!item || item.price == null) {
    return fallback
  }

  const quantity = item.quantity ?? DEFAULT_ITEM_QUANTITY
  const totalPrice = includeQuantity ? item.price * quantity : item.price
  const itemCurrency = getCurrency(item.currency ?? null, defaultCurrency)
  return formatCurrency(totalPrice, itemCurrency)
}
