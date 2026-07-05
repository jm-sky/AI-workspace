import type { TContainerColor, TGearWeightUnit } from '../types/gear.types'
import type { ColumnDef } from '@tanstack/vue-table'

export interface IItemWithContainer {
  id: string
  name: string
  category: string
  containerId: string
  containerName: string
  containerColor: TContainerColor
  quantity: number
  weight: number
  weightUnit: TGearWeightUnit
  status: 'owned' | 'missing' | 'toBuy'
  priority: 'low' | 'medium' | 'high' | 'critical'
  brand?: string
  color?: string
  expirationDate?: string
  wearable?: boolean
  consumable?: boolean
  isContainer?: boolean // True if this is a container (not a regular item)
  containerType?: string // Container type (if isContainer is true)
  primaryImageUrl?: string | null // URL of the primary image for the item
}

export function createAllItemsColumns(
  t: (key: string, ...args: unknown[]) => string,
): ColumnDef<IItemWithContainer>[] {
  return [
    {
      id: 'image',
      accessorKey: 'id',
      header: () => t('gear.item.image'),
      enableSorting: false,
      enableHiding: true,
    },
    {
      id: 'category',
      accessorKey: 'category',
      header: () => t('gear.item.category'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'name',
      accessorKey: 'name',
      header: () => t('gear.item.name'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'container',
      accessorKey: 'containerName',
      header: () => t('gear.allItems.container'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'quantity',
      accessorKey: 'quantity',
      header: () => t('gear.item.quantity'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'weight',
      accessorKey: 'weight',
      header: () => t('gear.item.weight'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'status',
      accessorKey: 'status',
      header: () => t('gear.item.status'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'priority',
      accessorKey: 'priority',
      header: () => t('gear.item.priority'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'brand',
      accessorKey: 'brand',
      header: () => t('gear.item.brand'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'color',
      accessorKey: 'color',
      header: () => t('gear.item.color'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'wearable',
      accessorKey: 'wearable',
      header: () => t('gear.item.wearable'),
      enableSorting: true,
      enableHiding: true,
    },
    {
      id: 'consumable',
      accessorKey: 'consumable',
      header: () => t('gear.item.consumable'),
      enableSorting: true,
      enableHiding: true,
    },
  ]
}

