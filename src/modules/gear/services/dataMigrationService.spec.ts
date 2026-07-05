import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { IGearContainer } from '../types/gear.types'
import { hasLocalData, migrateLocalDataToAPI } from './dataMigrationService'
import { gearItemApiServiceV2 } from './gearItemApiServiceV2'

const V1_KEY = 'gear-stack:containers'

// The migration uploads through the V2 API (preserving ids) and refreshes the store.
vi.mock('./gearItemApiServiceV2')

function makeContainer(partial: Partial<IGearContainer> & { id: string; name: string }): IGearContainer {
  return {
    parentContainerId: null,
    items: [],
    type: 'backpack',
    isPublic: false,
    favorite: false,
    userRatingCount: 0,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
    ...partial,
  } as IGearContainer
}

function setV1Data(containers: IGearContainer[]): void {
  localStorage.setItem(V1_KEY, JSON.stringify(containers))
}

describe('dataMigrationService (V2 upload)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
    // getItems is called to refresh the store after upload
    vi.spyOn(gearItemApiServiceV2, 'getItems').mockResolvedValue([])
  })

  describe('ordering', () => {
    it('creates parent containers before their children', async () => {
      setV1Data([
        makeContainer({ id: 'child-1', name: 'Child', parentContainerId: 'parent-1', type: 'pouch' }),
        makeContainer({ id: 'parent-1', name: 'Parent' }),
      ])

      const createCalls: Array<{ id?: string | null; name: string; parentItemId?: string | null }> = []
      vi.spyOn(gearItemApiServiceV2, 'createItem').mockImplementation(async (dto) => {
        createCalls.push({ id: dto.id, name: dto.name, parentItemId: dto.parentItemId })
        return { id: dto.id } as never
      })

      await migrateLocalDataToAPI()

      expect(createCalls.map(c => c.name)).toEqual(['Parent', 'Child'])
      // ids are preserved (no id mapping needed in V2)
      expect(createCalls.find(c => c.name === 'Child')).toMatchObject({ id: 'child-1', parentItemId: 'parent-1' })
    })

    it('handles deeply nested containers (3+ levels) in dependency order', async () => {
      setV1Data([
        makeContainer({ id: 'gc', name: 'Grandchild', parentContainerId: 'c', type: 'pouch' }),
        makeContainer({ id: 'p', name: 'Parent' }),
        makeContainer({ id: 'c', name: 'Child', parentContainerId: 'p', type: 'bag' }),
      ])

      const order: string[] = []
      vi.spyOn(gearItemApiServiceV2, 'createItem').mockImplementation(async (dto) => {
        order.push(dto.name)
        return { id: dto.id } as never
      })

      await migrateLocalDataToAPI()

      expect(order).toEqual(['Parent', 'Child', 'Grandchild'])
    })

    it('creates items after their parent containers', async () => {
      setV1Data([
        makeContainer({
          id: 'c1',
          name: 'Bag',
          items: [
            { id: 'i1', name: 'Knife', category: 'tools', quantity: 1, weight: 10, weightUnit: 'g', status: 'owned', priority: 'medium' },
          ] as IGearContainer['items'],
        }),
      ])

      const calls: Array<{ itemType: string; name: string; parentItemId?: string | null }> = []
      vi.spyOn(gearItemApiServiceV2, 'createItem').mockImplementation(async (dto) => {
        calls.push({ itemType: dto.itemType, name: dto.name, parentItemId: dto.parentItemId })
        return { id: dto.id } as never
      })

      await migrateLocalDataToAPI()

      expect(calls).toEqual([
        { itemType: 'container', name: 'Bag', parentItemId: null },
        { itemType: 'item', name: 'Knife', parentItemId: 'c1' },
      ])
    })
  })

  describe('snapshot cleanup', () => {
    it('clears the V1 snapshot after a clean upload', async () => {
      setV1Data([makeContainer({ id: 'c1', name: 'Bag' })])
      vi.spyOn(gearItemApiServiceV2, 'createItem').mockResolvedValue({ id: 'c1' } as never)

      await migrateLocalDataToAPI()

      expect(localStorage.getItem(V1_KEY)).toBeNull()
    })

    it('keeps the V1 snapshot if any upload fails', async () => {
      setV1Data([
        makeContainer({ id: 'c1', name: 'Bag 1' }),
        makeContainer({ id: 'c2', name: 'Bag 2' }),
      ])
      vi.spyOn(gearItemApiServiceV2, 'createItem').mockImplementation(async (dto) => {
        if (dto.name === 'Bag 1') throw new Error('API error')
        return { id: dto.id } as never
      })

      await migrateLocalDataToAPI()

      // Both attempted, snapshot kept because of the failure
      expect(localStorage.getItem(V1_KEY)).not.toBeNull()
    })
  })

  describe('edge cases', () => {
    it('does nothing when there is no local data', async () => {
      const createSpy = vi.spyOn(gearItemApiServiceV2, 'createItem')
      await migrateLocalDataToAPI()
      expect(createSpy).not.toHaveBeenCalled()
    })
  })

  describe('hasLocalData', () => {
    it('returns true when localStorage has containers', () => {
      setV1Data([makeContainer({ id: '1', name: 'Test' })])
      expect(hasLocalData()).toBe(true)
    })

    it('returns false when localStorage is empty', () => {
      expect(hasLocalData()).toBe(false)
    })

    it('returns false for invalid JSON', () => {
      localStorage.setItem(V1_KEY, 'invalid json')
      expect(hasLocalData()).toBe(false)
    })
  })
})
