import type { IShelfLife } from '../types/gear.types'
import type { TDateTime } from '@/shared/types/base.type'

/**
 * Calculate expiration date based on shelf life
 * @param shelfLife - Shelf life object with value and unit
 * @returns ISO date string (YYYY-MM-DD format)
 */
export function calculateExpirationDate(shelfLife: IShelfLife): TDateTime {
  const now = new Date()
  const result = new Date(now)

  switch (shelfLife.unit) {
    case 'days':
      result.setDate(result.getDate() + shelfLife.value)
      break
    case 'months':
      result.setMonth(result.getMonth() + shelfLife.value)
      break
    case 'years':
      result.setFullYear(result.getFullYear() + shelfLife.value)
      break
  }

  return result.toISOString().split('T')[0] as TDateTime
}

/**
 * Format shelf life for display
 * @param shelfLife - Shelf life object with value and unit
 * @returns Formatted string (e.g., "10 lat", "6 miesięcy", "30 dni")
 */
export function formatShelfLife(shelfLife: IShelfLife): string {
  const unitMap: Record<IShelfLife['unit'], (value: number) => string> = {
    days: (value: number) => {
      if (value === 1) return 'dzień'
      if (value < 5) return 'dni'
      return 'dni'
    },
    months: (value: number) => {
      if (value === 1) return 'miesiąc'
      if (value < 5) return 'miesiące'
      return 'miesięcy'
    },
    years: (value: number) => {
      if (value === 1) return 'rok'
      if (value < 5) return 'lata'
      return 'lat'
    },
  }

  const unitLabel = unitMap[shelfLife.unit](shelfLife.value)
  return `${shelfLife.value} ${unitLabel}`
}

