import { EXPIRATION_WARNING_DAYS } from './constants'
import type { TDateTime } from '@/shared/types/base.type'

interface IExpirable {
  expirationDate?: TDateTime | null // ISO date string
}

export function isExpiringSoon(item: IExpirable | null | undefined, days: number = EXPIRATION_WARNING_DAYS): boolean {
  if (!item) return false
  if (!item?.expirationDate) return false
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24
  const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
  return daysUntilExpiration > 0 && daysUntilExpiration <= days
}
