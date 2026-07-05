import { describe, expect, it } from 'vitest'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { getAllItemsForCatalogV2 } from './getAllItemsForCatalogV2'

function makeItem(partial: Partial<IGearItemV2> & { id: string; itemType: 'container' | 'item' }): IGearItemV2 {
  return {
    userId: 'u1',
    parentItemId: null,
    name: partial.name ?? partial.id,
    description: null,
    containerType: partial.itemType === 'container' ? 'backpack' : null,
    category: null,
    orderIndex: null,
    status: 'owned',
    priority: null,
    weight: null,
    weightUnit: null,
    maxWeight: null,
    maxWeightUnit: null,
    quantity: 1,
    wearable: false,
    consumable: false,
    favorite: false,
    hideWhenNested: false,
    price: null,
    currency: null,
    url: null,
    brand: null,
    color: null,
    expirationDate: null,
    quality: null,
    notes: null,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    isPublic: false,
    showItemImages: false,
    ...partial,
  } as IGearItemV2
}

describe('getAllItemsForCatalogV2', () => {
  const container = makeItem({ id: 'c1', itemType: 'container', name: 'Bag', color: 'olive' })
  const other = makeItem({ id: 'c2', itemType: 'container', name: 'EDC' })
  const item1 = makeItem({ id: 'i1', itemType: 'item', name: 'Zebra', parentItemId: 'c1', category: 'tools' })
  const item2 = makeItem({ id: 'i2', itemType: 'item', name: 'Alpha', parentItemId: 'c2', category: 'food' })

  it('excludes the given container and its items, lists only regular items sorted by name', () => {
    const result = getAllItemsForCatalogV2([container, other, item1, item2], 'c1')

    // c1 items excluded; containers omitted when excluding; only i2 remains
    expect(result.map(r => r.id)).toEqual(['i2'])
    expect(result[0]).toMatchObject({
      id: 'i2',
      name: 'Alpha',
      containerId: 'c2',
      containerName: 'EDC',
      category: 'food',
      isContainer: false,
    })
  })

  it('includes containers as items and sorts alphabetically when no exclusion', () => {
    const result = getAllItemsForCatalogV2([container, other, item1, item2])

    // Containers + items, sorted by name: Alpha, Bag, EDC, Zebra
    expect(result.map(r => r.name)).toEqual(['Alpha', 'Bag', 'EDC', 'Zebra'])
    const bag = result.find(r => r.id === 'c1')!
    expect(bag.isContainer).toBe(true)
    expect(bag.containerType).toBe('backpack')
  })

  it('resolves container info for items from the parent container', () => {
    const result = getAllItemsForCatalogV2([container, item1], 'somethingElse')
    const zebra = result.find(r => r.id === 'i1')!
    expect(zebra.containerName).toBe('Bag')
    expect(zebra.containerColor).toBe('olive')
  })
})
