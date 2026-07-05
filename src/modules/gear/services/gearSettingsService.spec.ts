import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { IGearSettings, IUserBrand, IUserCategory, IUserContainerType } from '../types/gearSettings.types'
import { GearSettingsService } from './gearSettingsService'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    clear: () => {
      store = {}
    },
    getItem: (key: string) => store[key] ?? null,
    removeItem: (key: string) => {
      delete store[key]
    },
    setItem: (key: string, value: string) => {
      store[key] = value
    },
  }
})()

Object.defineProperty(globalThis, 'localStorage', {
  configurable: true,
  value: localStorageMock,
})

describe('gearSettingsService - HIGH PRIORITY Refactoring', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  const createDefaultSettings = (): IGearSettings => ({
    customBrands: [],
    customCategories: [],
    customContainerTypes: [],
  })

  const createMockCategory = (id = 'cat-1'): IUserCategory => ({
    createdAt: '2024-01-01T00:00:00Z',
    id,
    updatedAt: '2024-01-01T00:00:00Z',
    value: 'test-category',
  })

  const createMockContainerType = (id = 'type-1'): IUserContainerType => ({
    createdAt: '2024-01-01T00:00:00Z',
    id,
    updatedAt: '2024-01-01T00:00:00Z',
    value: 'test-type',
  })

  const createMockBrand = (id = 'brand-1'): IUserBrand => ({
    createdAt: '2024-01-01T00:00:00Z',
    id,
    updatedAt: '2024-01-01T00:00:00Z',
    value: 'Test Brand',
  })

  describe('H2: Generic Array Helpers (DRY Fix)', () => {
    describe('addCategory / addContainerType / addBrand', () => {
      it('should add a custom category using generic addToArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const settings = createDefaultSettings()
        const category = createMockCategory()

        // Act
        const updated = await service.addCategory(settings, category)

        // Assert
        expect(updated.customCategories).toHaveLength(1)
        expect(updated.customCategories[0]).toEqual(category)
      })

      it('should add a custom container type using generic addToArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const settings = createDefaultSettings()
        const containerType = createMockContainerType()

        // Act
        const updated = await service.addContainerType(settings, containerType)

        // Assert
        expect(updated.customContainerTypes).toHaveLength(1)
        expect(updated.customContainerTypes[0]).toEqual(containerType)
      })

      it('should add a custom brand using generic addToArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const settings = createDefaultSettings()
        const brand = createMockBrand()

        // Act
        const updated = await service.addBrand(settings, brand)

        // Assert
        expect(updated.customBrands).toHaveLength(1)
        expect(updated.customBrands[0]).toEqual(brand)
      })

      it('should persist to localStorage when adding items', async () => {
        // Arrange
        const service = new GearSettingsService()
        const settings = createDefaultSettings()
        const category = createMockCategory()

        // Act
        await service.addCategory(settings, category)

        // Assert
        const stored = localStorage.getItem('gear-stack:gear-settings')
        expect(stored).toBeTruthy()
        const parsed = JSON.parse(stored!)
        expect(parsed.customCategories).toHaveLength(1)
      })
    })

    describe('updateCategory / updateContainerType / updateBrand', () => {
      it('should update a custom category using generic updateInArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const category = createMockCategory()
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customCategories: [category],
        }
        const updatedCategory = { ...category, value: 'updated-category' }

        // Act
        const updated = await service.updateCategory(settings, updatedCategory)

        // Assert
        expect(updated.customCategories).toHaveLength(1)
        expect(updated.customCategories[0]!.value).toBe('updated-category')
      })

      it('should update a custom container type using generic updateInArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const containerType = createMockContainerType()
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customContainerTypes: [containerType],
        }
        const updatedType = { ...containerType, value: 'updated-type' }

        // Act
        const updated = await service.updateContainerType(settings, updatedType)

        // Assert
        expect(updated.customContainerTypes).toHaveLength(1)
        expect(updated.customContainerTypes[0]!.value).toBe('updated-type')
      })

      it('should update a custom brand using generic updateInArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const brand = createMockBrand()
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customBrands: [brand],
        }
        const updatedBrand = { ...brand, value: 'Updated Brand' }

        // Act
        const updated = await service.updateBrand(settings, updatedBrand)

        // Assert
        expect(updated.customBrands).toHaveLength(1)
        expect(updated.customBrands[0]!.value).toBe('Updated Brand')
      })

      it('should not modify other items when updating', async () => {
        // Arrange
        const service = new GearSettingsService()
        const category1 = createMockCategory('cat-1')
        const category2 = createMockCategory('cat-2')
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customCategories: [category1, category2],
        }
        const updatedCategory = { ...category1, value: 'updated' }

        // Act
        const updated = await service.updateCategory(settings, updatedCategory)

        // Assert
        expect(updated.customCategories).toHaveLength(2)
        expect(updated.customCategories[0]!.value).toBe('updated')
        expect(updated.customCategories[1]!.value).toBe(category2.value)
      })
    })

    describe('removeCategory / removeContainerType / removeBrand', () => {
      it('should remove a custom category using generic removeFromArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const category = createMockCategory()
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customCategories: [category],
        }

        // Act
        const updated = await service.removeCategory(settings, category.id)

        // Assert
        expect(updated.customCategories).toHaveLength(0)
      })

      it('should remove a custom container type using generic removeFromArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const containerType = createMockContainerType()
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customContainerTypes: [containerType],
        }

        // Act
        const updated = await service.removeContainerType(settings, containerType.id)

        // Assert
        expect(updated.customContainerTypes).toHaveLength(0)
      })

      it('should remove a custom brand using generic removeFromArray helper', async () => {
        // Arrange
        const service = new GearSettingsService()
        const brand = createMockBrand()
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customBrands: [brand],
        }

        // Act
        const updated = await service.removeBrand(settings, brand.id)

        // Assert
        expect(updated.customBrands).toHaveLength(0)
      })

      it('should only remove the specified item', async () => {
        // Arrange
        const service = new GearSettingsService()
        const category1 = createMockCategory('cat-1')
        const category2 = createMockCategory('cat-2')
        const settings: IGearSettings = {
          ...createDefaultSettings(),
          customCategories: [category1, category2],
        }

        // Act
        const updated = await service.removeCategory(settings, category1.id)

        // Assert
        expect(updated.customCategories).toHaveLength(1)
        expect(updated.customCategories[0]!.id).toBe(category2.id)
      })
    })
  })

  describe('H1: Static Delegate Wrapper (Reduce Duplication)', () => {
    it('should delegate static loadFromStorage to instance method', async () => {
      // Arrange
      const settings = createDefaultSettings()
      localStorage.setItem('gear-stack:gear-settings', JSON.stringify(settings))

      // Act
      const loaded = await GearSettingsService.loadFromStorage()

      // Assert
      expect(loaded).toEqual(settings)
    })

    it('should delegate static saveToStorage to instance method', async () => {
      // Arrange
      const settings = createDefaultSettings()

      // Act
      await GearSettingsService.saveToStorage(settings)

      // Assert
      const stored = localStorage.getItem('gear-stack:gear-settings')
      expect(stored).toBeTruthy()
      expect(JSON.parse(stored!)).toEqual(settings)
    })

    it('should delegate static addCategory to instance method', async () => {
      // Arrange
      const settings = createDefaultSettings()
      const category = createMockCategory()

      // Act
      const updated = await GearSettingsService.addCategory(settings, category)

      // Assert
      expect(updated.customCategories).toHaveLength(1)
      expect(updated.customCategories[0]).toEqual(category)
    })

    it('should delegate static updateCategory to instance method', async () => {
      // Arrange
      const category = createMockCategory()
      const settings: IGearSettings = {
        ...createDefaultSettings(),
        customCategories: [category],
      }
      const updatedCategory = { ...category, value: 'updated' }

      // Act
      const updated = await GearSettingsService.updateCategory(settings, updatedCategory)

      // Assert
      expect(updated.customCategories[0]!.value).toBe('updated')
    })

    it('should delegate static removeCategory to instance method', async () => {
      // Arrange
      const category = createMockCategory()
      const settings: IGearSettings = {
        ...createDefaultSettings(),
        customCategories: [category],
      }

      // Act
      const updated = await GearSettingsService.removeCategory(settings, category.id)

      // Assert
      expect(updated.customCategories).toHaveLength(0)
    })

    it('should delegate all static methods for containerTypes', async () => {
      // Arrange
      const containerType = createMockContainerType()
      const settings = createDefaultSettings()

      // Act & Assert - Add
      let updated = await GearSettingsService.addContainerType(settings, containerType)
      expect(updated.customContainerTypes).toHaveLength(1)

      // Act & Assert - Update
      const updatedType = { ...containerType, value: 'updated' }
      updated = await GearSettingsService.updateContainerType(updated, updatedType)
      expect(updated.customContainerTypes[0]!.value).toBe('updated')

      // Act & Assert - Remove
      updated = await GearSettingsService.removeContainerType(updated, containerType.id)
      expect(updated.customContainerTypes).toHaveLength(0)
    })

    it('should delegate all static methods for brands', async () => {
      // Arrange
      const brand = createMockBrand()
      const settings = createDefaultSettings()

      // Act & Assert - Add
      let updated = await GearSettingsService.addBrand(settings, brand)
      expect(updated.customBrands).toHaveLength(1)

      // Act & Assert - Update
      const updatedBrand = { ...brand, value: 'Updated' }
      updated = await GearSettingsService.updateBrand(updated, updatedBrand)
      expect(updated.customBrands[0]!.value).toBe('Updated')

      // Act & Assert - Remove
      updated = await GearSettingsService.removeBrand(updated, brand.id)
      expect(updated.customBrands).toHaveLength(0)
    })
  })

  describe('Integration: All Operations Work Together', () => {
    it('should support multiple categories, types, and brands simultaneously', async () => {
      // Arrange
      const service = new GearSettingsService()
      let settings = createDefaultSettings()

      const category1 = createMockCategory('cat-1')
      const category2 = createMockCategory('cat-2')
      const containerType = createMockContainerType()
      const brand = createMockBrand()

      // Act - Add multiple items
      settings = await service.addCategory(settings, category1)
      settings = await service.addCategory(settings, category2)
      settings = await service.addContainerType(settings, containerType)
      settings = await service.addBrand(settings, brand)

      // Assert - All items added
      expect(settings.customCategories).toHaveLength(2)
      expect(settings.customContainerTypes).toHaveLength(1)
      expect(settings.customBrands).toHaveLength(1)

      // Act - Update category
      const updatedCategory = { ...category1, value: 'updated' }
      settings = await service.updateCategory(settings, updatedCategory)

      // Assert - Only target category updated
      expect(settings.customCategories[0]!.value).toBe('updated')
      expect(settings.customCategories[1]!.value).toBe(category2.value)

      // Act - Remove one category
      settings = await service.removeCategory(settings, category1.id)

      // Assert - Only one category removed, others intact
      expect(settings.customCategories).toHaveLength(1)
      expect(settings.customContainerTypes).toHaveLength(1)
      expect(settings.customBrands).toHaveLength(1)
    })
  })
})
