import { describe, expect, it, vi } from 'vitest'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { exportContainersToJSONV2 } from './exportToJsonV2'
import { importContainersFromJSONV2, type ImportJsonDeps } from './importFromJsonV2'

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

function makeCreateDep() {
  const created: Array<{ id: string; name: string; itemType: string; parentItemId: string | null }> = []
  let counter = 0
  const deps: ImportJsonDeps = {
    createItem: vi.fn(async (dto) => {
      const id = `new-${++counter}`
      created.push({ id, name: dto.name, itemType: dto.itemType, parentItemId: dto.parentItemId ?? null })
      return makeItem({ id, itemType: dto.itemType, name: dto.name, parentItemId: dto.parentItemId ?? null })
    }),
  }
  return { deps, created }
}

describe('importContainersFromJSONV2', () => {
  it('rejects malformed JSON shape', async () => {
    const { deps } = makeCreateDep()
    await expect(importContainersFromJSONV2(JSON.stringify({ foo: 1 }), deps)).rejects.toThrow(/Invalid gear JSON/)
  })

  it('round-trips an exported tree, re-parenting children', async () => {
    // Build a small tree and export it via the V2 exporter
    const container = makeItem({ id: 'c1', itemType: 'container', name: 'Bag' })
    const item = makeItem({ id: 'i1', itemType: 'item', name: 'Knife', parentItemId: 'c1' })
    const nested = makeItem({ id: 'c2', itemType: 'container', name: 'Pouch', parentItemId: 'c1' })
    const nestedItem = makeItem({ id: 'i2', itemType: 'item', name: 'Match', parentItemId: 'c2' })

    const childrenMap: Record<string, IGearItemV2[]> = {
      c1: [item, nested],
      c2: [nestedItem],
    }
    const json = exportContainersToJSONV2([container], {
      getChildrenOfItem: id => childrenMap[id] ?? [],
      includeNestedContainers: true,
    })

    const { deps, created } = makeCreateDep()
    const result = await importContainersFromJSONV2(json, deps)

    expect(result).toEqual({ containers: 2, items: 2 })
    expect(created).toHaveLength(4)

    // Root container created at top level
    const root = created.find(c => c.name === 'Bag')!
    expect(root.parentItemId).toBeNull()

    // Knife and Pouch parented under the new root
    expect(created.find(c => c.name === 'Knife')!.parentItemId).toBe(root.id)
    const pouch = created.find(c => c.name === 'Pouch')!
    expect(pouch.parentItemId).toBe(root.id)

    // Match parented under the new Pouch
    expect(created.find(c => c.name === 'Match')!.parentItemId).toBe(pouch.id)
  })

  it('accepts a bare array of nodes', async () => {
    const node = { ...makeItem({ id: 'c1', itemType: 'container', name: 'Solo' }), children: [] }
    const { deps, created } = makeCreateDep()
    const result = await importContainersFromJSONV2(JSON.stringify([node]), deps)
    expect(result.containers).toBe(1)
    expect(created[0]!.name).toBe('Solo')
  })
})
