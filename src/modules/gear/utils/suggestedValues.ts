/**
 * Suggested values for gear items and containers
 *
 * This file re-exports all suggested values for backward compatibility.
 * For better organization, you can import directly from:
 * - suggestedColors.ts for color-related exports
 * - suggestedBrands.ts for brand-related exports
 */

// Re-export brands
export {
  getBrandOptions,
  SUGGESTED_BRANDS,
} from './suggestedBrands'

// Re-export colors
export {
  DEFAULT_COLOR,
  getColorHex,
  getColorOptions,
  SUGGESTED_COLORS,
  type TColor,
} from './suggestedColors'

