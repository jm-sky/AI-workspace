import { SUGGESTED_BRANDS, SUGGESTED_COLORS } from './suggestedValues'

/**
 * Result of parameter recognition
 */
export interface IRecognizedParameters {
  brand?: string
  color?: string
}

/**
 * Recognize parameters (brand, color) from item name
 * Uses fuzzy matching against SUGGESTED_BRANDS (and custom brands) and SUGGESTED_COLORS
 *
 * @param name - Item name to analyze
 * @param customBrands - Optional array of custom user brands to include in matching
 * @returns Recognized parameters (brand and/or color)
 */
export function recognizeParameters(
  name: string,
  customBrands?: Array<{ value: string }>
): IRecognizedParameters {
  if (!name || name.trim().length === 0) {
    return {}
  }

  const normalizedName = name.toLowerCase().trim()
  const result: IRecognizedParameters = {}

  // Combine default and custom brands
  const allBrands = [
    ...SUGGESTED_BRANDS,
    ...(customBrands?.map(b => b.value) ?? []),
  ]

  // Match brand - check for brand names in the item name
  // Sort brands by length (longest first) to match longer names first
  const brandsByLength = [...allBrands].sort((a, b) => b.length - a.length)

  for (const brand of brandsByLength) {
    const normalizedBrand = brand.toLowerCase().trim()

    // Exact match (case-insensitive)
    if (normalizedName === normalizedBrand) {
      result.brand = brand
      break
    }

    // Contains match (fuzzy)
    // Check if brand name is contained in item name or vice versa
    const firstWord = normalizedName.split(' ')[0]
    if (
      normalizedName.includes(normalizedBrand) ||
      (firstWord && normalizedBrand.includes(firstWord)) // First word matches
    ) {
      // Avoid false positives - brand should be significant part
      if (normalizedBrand.length >= 3 && normalizedName.includes(normalizedBrand)) {
        result.brand = brand
        break
      }
    }
  }

  // If no brand found in suggested list, try to extract brand-like patterns from name
  // Look for uppercase/mixed-case words or hyphenated patterns early in the name
  if (!result.brand) {
    const words = name.trim().split(/\s+/)
    if (words.length > 1) {
      // First, check for hyphenated brand patterns (e.g., "M-TAC" in "Materac M-TAC")
      // These are most likely to be brands/model numbers
      for (const word of words.slice(0, 3)) { // Check first 3 words
        if (word.includes('-') && word.match(/^[A-Z][A-Za-z0-9-]+$/)) {
          // Hyphenated word with uppercase start - likely a brand/model
          result.brand = word
          break
        }
      }
      
      // If no hyphenated pattern found, check first word(s) for brand-like patterns
      if (!result.brand) {
        const firstWord = words[0] ?? ''
        const secondWord = words[1] ?? ''
        
        // Exclude common words that aren't brands
        const commonWords = ['the', 'a', 'an', 'my', 'our', 'your', 'this', 'that', 'these', 'those', 'materac', 'plecak', 'torba', 'saszetka']
        
        // Check if first word looks like a brand (has uppercase letters, may have hyphens)
        if (firstWord.match(/^[A-Z][A-Za-z0-9-]+$/) && !commonWords.includes(firstWord.toLowerCase())) {
          result.brand = firstWord
        }
        
        // Also check second word if first word is a common article/preposition or common noun
        if (!result.brand && secondWord) {
          if (firstWord.toLowerCase().match(/^(the|a|an|my|our|your)$/) || commonWords.includes(firstWord.toLowerCase())) {
            if (secondWord.match(/^[A-Z][A-Za-z0-9-]+$/)) {
              result.brand = secondWord
            }
          }
        }
      }
    }
  }

  // Match color - check for color names in the item name
  // Sort colors by length (longest first) to match longer names first
  const colorsByLength = [...SUGGESTED_COLORS].sort((a, b) => b.length - a.length)

  for (const color of colorsByLength) {
    const normalizedColor = color.toLowerCase().trim()

    // Exact match (case-insensitive)
    if (normalizedName === normalizedColor) {
      result.color = color
      break
    }

    // Contains match (fuzzy)
    // Check if color name is contained in item name
    if (normalizedName.includes(normalizedColor)) {
      // Avoid false positives - color should be significant part
      if (normalizedColor.length >= 3) {
        result.color = color
        break
      }
    }
  }

  return result
}

/**
 * Recognize parameters for multiple items
 *
 * @param items - Array of items with names
 * @returns Map of item IDs to recognized parameters
 */
export function recognizeParametersForItems(
  items: Array<{ id: string; name: string }>
): Map<string, IRecognizedParameters> {
  const result = new Map<string, IRecognizedParameters>()

  for (const item of items) {
    const params = recognizeParameters(item.name)
    if (params.brand || params.color) {
      result.set(item.id, params)
    }
  }

  return result
}
