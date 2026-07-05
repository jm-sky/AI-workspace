/**
 * Suggested brands/manufacturers for gear items and containers
 * These are pre-populated options that users can select from,
 * but they can also add their own custom values.
 */

// Suggested brands/manufacturers for gear items and containers
export const SUGGESTED_BRANDS = [
  '5.11 Tactical',
  'Adventure Medical Kits',
  'Anker',
  'Arc\'teryx',
  'Badger',
  'Bahco',
  'BIC',
  'Black Diamond',
  'Blackhawk',
  'CamelBak',
  'Coghlan\'s',
  'Columbia',
  'Condor',
  'Deuter',
  'Eagle Industries',
  'EDCX',
  'Esbit',
  'Fenix',
  'Field Notes',
  'Fisher',
  'Fiskars',
  'Gregory',
  'Helicon',
  'Helikon',
  'Leatherman',
  'LifeStraw',
  'Light My Fire',
  'M-TAC',
  'Magpul',
  'Maxpedition',
  'Merrell',
  'MFH',
  'Mil-Tec',
  'Morakniv',
  'Mystery Ranch',
  'NEO Tools',
  'Olight',
  'Osprey',
  'Patagonia',
  'Salomon',
  'SOL (Survive Outdoors Longer)',
  'SolarForce',
  'Tactical Tailor',
  'The North Face',
  'UCO',
  'Victorinox',
  'YOUKUKE',
  'Zippo',
] as const

/**
 * Convert suggested brands to ComboBox options
 * Includes both default SUGGESTED_BRANDS and custom user brands
 */
export function getBrandOptions(customBrands?: Array<{ value: string }>): Array<{ value: string; label: string }> {
  const defaultBrands = SUGGESTED_BRANDS.map(brand => ({
    value: brand,
    label: brand,
  }))

  if (!customBrands || customBrands.length === 0) {
    return defaultBrands
  }

  const customBrandOptions = customBrands.map(brand => ({
    value: brand.value,
    label: brand.value,
  }))

  // Combine default and custom brands, removing duplicates
  const allBrands = [...defaultBrands, ...customBrandOptions]
  const uniqueBrands = Array.from(
    new Map(allBrands.map(brand => [brand.value, brand])).values()
  )

  return uniqueBrands
}

