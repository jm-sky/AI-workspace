/**
 * Suggested colors for gear items
 * These are pre-populated options that users can select from,
 * but they can also add their own custom values.
 */

export const DEFAULT_COLOR = '#808080'

// Suggested colors for gear items
export const SUGGESTED_COLORS = [
  'Olive',
  'Coyote',
  'Black',
  'Tan',
  'Gray',
  'Green',
  'Brown',
  'Navy',
  'OD Green',
  'Ranger Green',
  'Multicam',
  'Black Multicam',
  'Desert',
  'Woodland',
] as const

export type TColor = typeof SUGGESTED_COLORS[number]

// Map common color names to hex values (case-insensitive)
const colorNameToHex: Record<string, string> = {
  'olive': '#808000',
  'coyote': '#8A6642',
  'black': '#000000',
  'tan': '#D2B48C',
  'gray': '#808080',
  'grey': '#808080',
  'green': '#008000',
  'brown': '#A52A2A',
  'od green': '#006B3C',
  'od-green': '#006B3C',
  'ranger green': '#007236',
  'ranger-green': '#007236',
  'multicam': '#C6C6C6',
  'black multicam': '#000000',
  'black-multicam': '#000000',
  'desert': '#C0C0C0',
  'woodland': '#8A8A8A',
  'navy': '#000080',
  'blue': '#0000FF',
  'red': '#FF0000',
  'white': '#FFFFFF',
  'orange': '#FFA500',
  'yellow': '#FFFF00',
  'purple': '#800080',
  'pink': '#FFC0CB',
}

/**
 * Get hex color for a color name (case-insensitive)
 * Returns hex if found, or null if not found
 */
export function getColorHex(colorName: string | null | undefined): string | null {
  if (!colorName) return null

  const normalized = colorName.toLowerCase().trim()
  return colorNameToHex[normalized] ?? null
}

/**
 * Convert suggested values to ComboBox options
 */
export function getColorOptions(): Array<{ value: string; label: string; data: string }> {
  return SUGGESTED_COLORS.map(color => ({
    value: color,
    label: color,
    data: getColorHex(color) ?? color,
  }))
}
