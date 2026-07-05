import type { TGearItemPriority, TGearItemStatus } from '../types/gear.types'
import type { BadgeVariants } from '@/components/ui/badge'

/**
 * Get badge variant for priority
 */
export function getPriorityVariant(priority: TGearItemPriority): BadgeVariants['variant'] {
  if (priority === 'critical') return 'destructive'
  if (priority === 'high') return 'default'
  return 'outline'
}

/**
 * Get badge variant for status
 */
export function getStatusVariant(status: TGearItemStatus): BadgeVariants['variant'] {
  if (status === 'owned') return 'default'
  if (status === 'missing') return 'destructive'
  return 'destructive-outline'
}

