import type { TDateTime } from '@/shared/types/base.type'

interface IExpirable {
  expirationDate?: TDateTime | null // ISO date string
}

export function isExpired(item: IExpirable | null | undefined): boolean {
  if (!item) return false
  if (!item?.expirationDate) return false
  return new Date(item.expirationDate) < new Date()
}
