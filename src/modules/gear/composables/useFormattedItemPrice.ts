import { computed, type ComputedRef, type MaybeRefOrGetter, toValue } from 'vue'
import type { IGearItem } from '../types/gear.types'
import { formatCurrency, getCurrency } from '../utils/currencyFormatter'
import { useGearSettings } from './useGearSettings'

/**
 * Composable for formatting item price with currency
 * @param itemOrPrice - Item object or price value
 * @param currency - Currency code (required if itemOrPrice is a number)
 * @param includeQuantity - Whether to multiply by quantity (default: false)
 * @param fallback - Fallback value if price is not available (default: '-')
 */
export function useFormattedItemPrice(
  itemOrPrice: MaybeRefOrGetter<IGearItem | number | null | undefined>,
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
      const item = itemOrPriceValue as IGearItem
      if (item.price == null) {
        return fallbackValue
      }

      const totalPrice = includeQuantityValue ? item.price * item.quantity : item.price
      const itemCurrency = getCurrency(item.currency, defaultCurrency.value)
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
 * Helper function for formatting item price (for use in templates)
 * @param item - Item object
 * @param includeQuantity - Whether to multiply by quantity (default: false)
 * @param defaultCurrency - Default currency code
 * @param fallback - Fallback value if price is not available (default: '-')
 */
export function formatItemPrice(
  item: IGearItem | null | undefined,
  includeQuantity: boolean = false,
  defaultCurrency: string,
  fallback: string = '-',
): string {
  if (!item || item.price == null) {
    return fallback
  }

  const totalPrice = includeQuantity ? item.price * item.quantity : item.price
  const itemCurrency = getCurrency(item.currency, defaultCurrency)
  return formatCurrency(totalPrice, itemCurrency)
}

