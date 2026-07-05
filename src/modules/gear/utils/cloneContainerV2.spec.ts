import { describe, expect, it, vi } from 'vitest'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { type CloneContainerDeps, cloneContainerV2 } from './cloneContainerV2'

/**
 * Build a minimal IGearItemV2 for tests.
 */
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

/**
 * Build a fake dependency set backed by an in-memory tree.
 * `tree` maps a parent id to its children.
 */
function makeDeps(items: IGearItemV2[], tree: Record<string, IGearItemV2[]>): {
  deps: CloneContainerDeps
  created: Array<{ id: string; name: string; itemType: string; parentItemId: string | null; price: number | null }>
} {
  const created: Array<{ id: string; name: string; itemType: string; parentItemId: string | null; price: number | null }> = []
  let counter = 0
  const deps: CloneContainerDeps = {
    getItemById: vi.fn(async (id) => items.find(i => i.id === id)),
    getChildren: vi.fn(async (parentId) => tree[parentId] ?? []),
    createItem: vi.fn(async (dto) => {
      const id = `new-${++counter}`
      created.push({
        id,
        name: dto.name,
        itemType: dto.itemType,
        parentItemId: dto.parentItemId ?? null,
        price: dto.price ?? null,
      })
      return makeItem({ id, itemType: dto.itemType, name: dto.name, parentItemId: dto.parentItemId ?? null })
    }),
  }
  return { deps, created }
}

describe('cloneContainerV2', () => {
  it('throws when the source is not a container', async () => {
    const item = makeItem({ id: 'i1', itemType: 'item' })
    const { deps } = makeDeps([item], {})
    await expect(cloneContainerV2('i1', { newName: 'X' }, deps)).rejects.toThrow(/not found/)
  })

  it('clones a container with its items and re-parents them under the new root', async () => {
    const container = makeItem({ id: 'c1', itemType: 'container', name: 'Bag' })
    const item1 = makeItem({ id: 'i1', itemType: 'item', name: 'Knife', parentItemId: 'c1', price: 10 })
    const item2 = makeItem({ id: 'i2', itemType: 'item', name: 'Rope', parentItemId: 'c1', price: 5 })
    const { deps, created } = makeDeps([container], { c1: [item1, item2] })

    const root = await cloneContainerV2('c1', { newName: 'Bag copy' }, deps)

    expect(root.name).toBe('Bag copy')
    expect(created).toHaveLength(3) // root + 2 items
    const rootCreated = created[0]!
    expect(rootCreated).toMatchObject({ name: 'Bag copy', itemType: 'container', parentItemId: null })
    // Items are parented under the newly created root
    expect(created[1]).toMatchObject({ name: 'Knife', parentItemId: rootCreated.id, price: 10 })
    expect(created[2]).toMatchObject({ name: 'Rope', parentItemId: rootCreated.id, price: 5 })
  })

  it('omits prices when includePrices is false', async () => {
    const container = makeItem({ id: 'c1', itemType: 'container' })
    const item1 = makeItem({ id: 'i1', itemType: 'item', price: 99 })
    const { deps, created } = makeDeps([container], { c1: [item1] })

    await cloneContainerV2('c1', { newName: 'X', includePrices: false }, deps)

    expect(created[1]!.price).toBeNull()
  })

  it('skips nested containers unless includeNestedContainers is set', async () => {
    const root = makeItem({ id: 'c1', itemType: 'container' })
    const nested = makeItem({ id: 'c2', itemType: 'container', parentItemId: 'c1' })
    const item = makeItem({ id: 'i1', itemType: 'item', parentItemId: 'c1' })
    const nestedItem = makeItem({ id: 'i2', itemType: 'item', parentItemId: 'c2' })
    const tree = { c1: [item, nested], c2: [nestedItem] }

    const { deps, created } = makeDeps([root], tree)
    await cloneContainerV2('c1', { newName: 'X' }, deps)
    // root + only the direct item (nested container skipped)
    expect(created).toHaveLength(2)
    expect(created.some(c => c.itemType === 'container' && c.parentItemId !== null)).toBe(false)
  })

  it('clones nested containers recursively when includeNestedContainers is set', async () => {
    const root = makeItem({ id: 'c1', itemType: 'container' })
    const nested = makeItem({ id: 'c2', itemType: 'container', parentItemId: 'c1' })
    const item = makeItem({ id: 'i1', itemType: 'item', parentItemId: 'c1' })
    const nestedItem = makeItem({ id: 'i2', itemType: 'item', parentItemId: 'c2' })
    const tree = { c1: [item, nested], c2: [nestedItem] }

    const { deps, created } = makeDeps([root], tree)
    await cloneContainerV2('c1', { newName: 'X', includeNestedContainers: true }, deps)
    // root + item + nested container + nested item
    expect(created).toHaveLength(4)
    const clonedNested = created.find(c => c.itemType === 'container' && c.parentItemId !== null)
    expect(clonedNested).toBeDefined()
    // the nested item is parented under the cloned nested container
    expect(created.some(c => c.parentItemId === clonedNested!.id)).toBe(true)
  })
})
