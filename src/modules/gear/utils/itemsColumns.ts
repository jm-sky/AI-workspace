import type { IGearItemV2 } from '../types/gear.types.v2'
import type { ColumnDef } from '@tanstack/vue-table'

export function createItemsColumns(
  t: (key: string, ...args: unknown[]) => string,
): ColumnDef<IGearItemV2>[] {
  return [
    {
      id: 'image',
      accessorKey: 'id',
      header: () => t('gear.item.image', 'Image'),
      enableSorting: false,
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
      id: 'category',
      accessorKey: 'category',
      header: () => t('gear.item.category'),
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
      id: 'priority',
      accessorKey: 'priority',
      header: () => t('gear.item.priority'),
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
      id: 'price',
      accessorKey: 'price',
      header: () => t('gear.item.price'),
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
    {
      id: 'order',
      accessorKey: 'order',
      header: () => t('gear.item.order', 'Order'),
      enableSorting: true,
      enableHiding: true,
      // Hidden by default (used for manual ordering)
    },
    {
      id: 'actions',
      header: () => t('gear.item.actions'),
      enableSorting: false,
      enableHiding: false,
      meta: {
        pinned: 'right',
      },
    },
  ]
}
