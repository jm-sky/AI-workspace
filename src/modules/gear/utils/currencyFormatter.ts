/**
 * Currency formatter utility
 * Provides currency formatting and supported currencies list
 */

const DEFAULT_LOCALE_ID = 'pl-PL'

export const SUPPORTED_CURRENCIES = [
  { value: 'PLN', label: 'PLN (zł)', symbol: 'zł' },
  { value: 'EUR', label: 'EUR (€)', symbol: '€' },
  { value: 'USD', label: 'USD ($)', symbol: '$' },
  { value: 'GBP', label: 'GBP (£)', symbol: '£' },
  { value: 'JPY', label: 'JPY (¥)', symbol: '¥' },
  { value: 'CHF', label: 'CHF (Fr)', symbol: 'Fr' },
  { value: 'CAD', label: 'CAD ($)', symbol: '$' },
  { value: 'AUD', label: 'AUD ($)', symbol: '$' },
] as const

export type SupportedCurrency = typeof SUPPORTED_CURRENCIES[number]['value']

/**
 * Detect default currency based on browser locale
 * @param locale - Browser locale string (e.g., 'pl-PL', 'en-US', 'en-GB')
 * @returns Currency code (PLN, USD, GBP, JPY, CHF, CAD, AUD, or EUR as default)
 */
export function detectDefaultCurrency(locale: string): SupportedCurrency {
  // Polish
  if (locale.startsWith('pl')) return 'PLN'
  // US English
  if (locale.startsWith('en-US')) return 'USD'
  // UK English
  if (locale.startsWith('en-GB')) return 'GBP'
  // Canadian English
  if (locale.startsWith('en-CA')) return 'CAD'
  // Australian English
  if (locale.startsWith('en-AU')) return 'AUD'
  // Japanese
  if (locale.startsWith('ja')) return 'JPY'
  // Swiss locales (German, French, Italian)
  if (locale.startsWith('de-CH') || locale.startsWith('fr-CH') || locale.startsWith('it-CH')) return 'CHF'
  // Default to EUR for other locales
  return 'EUR'
}

/**
 * Format currency amount using Intl.NumberFormat
 * @param amount - Amount to format
 * @param currency - Currency code (ISO 4217)
 * @param locale - Optional locale for formatting (defaults to 'pl-PL')
 * @returns Formatted currency string
 */
export function formatCurrency(
  amount: number,
  currency: string,
  locale?: string
): string {
  const formatter = new Intl.NumberFormat(locale ?? DEFAULT_LOCALE_ID, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return formatter.format(amount)
}

/**
 * Get currency label from currency code
 * @param currencyCode - Currency code (e.g., 'PLN', 'USD')
 * @returns Currency label (e.g., 'PLN (zł)')
 */
export function getCurrencyLabel(currencyCode: string): string {
  const currency = SUPPORTED_CURRENCIES.find(c => c.value === currencyCode)
  return currency?.label ?? currencyCode
}

/**
 * Get currency code for item/container, falling back to default currency
 * @param currency - Currency code from item/container (can be null/undefined)
 * @param defaultCurrency - Default currency to use if currency is not set
 * @returns Currency code to use
 */
export function getCurrency(
  currency: string | null | undefined,
  defaultCurrency: string
): string {
  return currency ?? defaultCurrency
}

