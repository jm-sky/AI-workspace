import { describe, expect, it } from 'vitest'
import type { ContainerFormData, ItemFormData } from './validation'
import {
  containerSchema,
  itemSchema,
  safeValidateContainer,
  safeValidateItem,
  validateContainerDto,
  validateItemDto,
} from './validation'

describe('validation', () => {
  describe('containerSchema', () => {
    it('should validate a minimal valid container', () => {
      const validContainer = {
        name: 'Test Container',
        type: 'backpack',
      }

      const result = containerSchema.safeParse(validContainer)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.name).toBe('Test Container')
        expect(result.data.type).toBe('backpack')
      }
    })

    it('should validate a complete valid container', () => {
      const validContainer: ContainerFormData = {
        name: 'Bug-Out Bag',
        type: 'backpack',
        description: 'Emergency preparedness bag',
        color: 'coyote',
        parentContainerId: '550e8400-e29b-41d4-a716-446655440000',
        hideWhenNested: true,
        isPublic: false,
        favorite: true,
        brand: 'Tactical Gear Inc',
        price: 150.99,
        currency: 'USD',
        weight: 2000,
        weightUnit: 'g',
        maxWeight: 25000,
        maxWeightUnit: 'g',
        url: 'https://example.com/product',
        showItemImages: true,
      }

      const result = containerSchema.safeParse(validContainer)
      expect(result.success).toBe(true)
    })

    it('should reject container with missing name', () => {
      const invalidContainer = {
        type: 'backpack',
      }

      const result = containerSchema.safeParse(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.path).toContain('name')
      }
    })

    it('should reject container with empty name', () => {
      const invalidContainer = {
        name: '',
        type: 'backpack',
      }

      const result = containerSchema.safeParse(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.message).toContain('wymagana')
      }
    })

    it('should reject container with missing type', () => {
      const invalidContainer = {
        name: 'Test',
      }

      const result = containerSchema.safeParse(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.path).toContain('type')
      }
    })

    it('should reject container with negative price', () => {
      const invalidContainer = {
        name: 'Test',
        type: 'backpack',
        price: -10,
      }

      const result = containerSchema.safeParse(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.message).toContain('ujemna')
      }
    })

    it('should reject container with negative weight', () => {
      const invalidContainer = {
        name: 'Test',
        type: 'backpack',
        weight: -100,
      }

      const result = containerSchema.safeParse(invalidContainer)
      expect(result.success).toBe(false)
    })

    it('should reject container with invalid URL', () => {
      const invalidContainer = {
        name: 'Test',
        type: 'backpack',
        url: 'not-a-valid-url',
      }

      const result = containerSchema.safeParse(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.message).toContain('URL')
      }
    })

    it('should accept container with empty string URL', () => {
      const validContainer = {
        name: 'Test',
        type: 'backpack',
        url: '',
      }

      const result = containerSchema.safeParse(validContainer)
      expect(result.success).toBe(true)
    })

    it('should reject container with invalid UUID for parentContainerId', () => {
      const invalidContainer = {
        name: 'Test',
        type: 'backpack',
        parentContainerId: 'not-a-uuid',
      }

      const result = containerSchema.safeParse(invalidContainer)
      expect(result.success).toBe(false)
    })

    it('should accept container with null parentContainerId', () => {
      const validContainer = {
        name: 'Test',
        type: 'backpack',
        parentContainerId: null,
      }

      const result = containerSchema.safeParse(validContainer)
      expect(result.success).toBe(true)
    })

    it('should accept container with valid color', () => {
      const validColors = ['default', 'coyote', 'khaki', 'olive', 'forestGreen', 'tan', 'brown', 'black', 'navy', 'jeans', 'gray', 'orange']

      for (const color of validColors) {
        const container = {
          name: 'Test',
          type: 'backpack',
          color,
        }

        const result = containerSchema.safeParse(container)
        expect(result.success).toBe(true)
      }
    })
  })

  describe('itemSchema', () => {
    it('should validate a minimal valid item', () => {
      const validItem = {
        name: 'Water Bottle',
        category: 'water',
        quantity: 1,
        weight: 300,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = itemSchema.safeParse(validItem)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.name).toBe('Water Bottle')
        expect(result.data.quantity).toBe(1)
      }
    })

    it('should validate a complete valid item', () => {
      const validItem: ItemFormData = {
        name: 'Tactical Knife',
        category: 'tools',
        quantity: 1,
        weight: 200,
        weightUnit: 'g',
        notes: 'Keep sharp',
        expirationDate: '2025-12-31',
        priority: 'high',
        status: 'owned',
        containerId: '550e8400-e29b-41d4-a716-446655440000',
        price: 75.50,
        currency: 'USD',
        url: 'https://example.com/knife',
        brand: 'Victorinox',
        color: 'black',
        quality: 'high',
        wearable: false,
        consumable: false,
        showOnContainer: true,
      }

      const result = itemSchema.safeParse(validItem)
      expect(result.success).toBe(true)
    })

    it('should reject item with missing name', () => {
      const invalidItem = {
        category: 'water',
        quantity: 1,
        weight: 300,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = itemSchema.safeParse(invalidItem)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.path).toContain('name')
      }
    })

    it('should reject item with missing category', () => {
      const invalidItem = {
        name: 'Test Item',
        quantity: 1,
        weight: 300,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = itemSchema.safeParse(invalidItem)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.path).toContain('category')
      }
    })

    it('should reject item with zero quantity', () => {
      const invalidItem = {
        name: 'Test Item',
        category: 'water',
        quantity: 0,
        weight: 300,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = itemSchema.safeParse(invalidItem)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0]?.message).toContain('większa od 0')
      }
    })

    it('should reject item with negative weight', () => {
      const invalidItem = {
        name: 'Test Item',
        category: 'water',
        quantity: 1,
        weight: -100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = itemSchema.safeParse(invalidItem)
      expect(result.success).toBe(false)
    })

    it('should reject item with fractional quantity', () => {
      const invalidItem = {
        name: 'Test Item',
        category: 'water',
        quantity: 1.5,
        weight: 300,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = itemSchema.safeParse(invalidItem)
      expect(result.success).toBe(false)
    })

    it('should accept all valid priority values', () => {
      const priorities = ['critical', 'high', 'medium', 'low']

      for (const priority of priorities) {
        const item = {
          name: 'Test',
          category: 'water',
          quantity: 1,
          weight: 100,
          weightUnit: 'g',
          priority,
          status: 'owned',
        }

        const result = itemSchema.safeParse(item)
        expect(result.success).toBe(true)
      }
    })

    it('should accept all valid status values', () => {
      const statuses = ['owned', 'missing', 'toBuy']

      for (const status of statuses) {
        const item = {
          name: 'Test',
          category: 'water',
          quantity: 1,
          weight: 100,
          weightUnit: 'g',
          priority: 'medium',
          status,
        }

        const result = itemSchema.safeParse(item)
        expect(result.success).toBe(true)
      }
    })

    it('should accept empty string for containerId', () => {
      const validItem = {
        name: 'Test',
        category: 'water',
        quantity: 1,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
        containerId: '',
      }

      const result = itemSchema.safeParse(validItem)
      expect(result.success).toBe(true)
    })
  })

  describe('validateContainerDto', () => {
    it('should return validated data for valid container', () => {
      const validContainer = {
        name: 'Test Container',
        type: 'backpack',
        weight: 1500,
        weightUnit: 'g',
      }

      const result = validateContainerDto(validContainer)
      expect(result.name).toBe('Test Container')
      expect(result.type).toBe('backpack')
      expect(result.weight).toBe(1500)
    })

    it('should throw ZodError for invalid container', () => {
      const invalidContainer = {
        name: '',
        type: 'backpack',
      }

      expect(() => validateContainerDto(invalidContainer)).toThrow()
    })

    it('should throw for missing required fields', () => {
      const invalidContainer = {
        name: 'Test',
      }

      expect(() => validateContainerDto(invalidContainer)).toThrow()
    })
  })

  describe('validateItemDto', () => {
    it('should return validated data for valid item', () => {
      const validItem = {
        name: 'Water Bottle',
        category: 'water',
        quantity: 2,
        weight: 300,
        weightUnit: 'g',
        priority: 'high',
        status: 'owned',
      }

      const result = validateItemDto(validItem)
      expect(result.name).toBe('Water Bottle')
      expect(result.quantity).toBe(2)
      expect(result.priority).toBe('high')
    })

    it('should throw ZodError for invalid item', () => {
      const invalidItem = {
        name: 'Test',
        category: 'water',
        quantity: 0, // Invalid: must be >= 1
        weight: 100,
        weightUnit: 'g',
        priority: 'high',
        status: 'owned',
      }

      expect(() => validateItemDto(invalidItem)).toThrow()
    })
  })

  describe('safeValidateContainer', () => {
    it('should return success result for valid container', () => {
      const validContainer = {
        name: 'Test Container',
        type: 'backpack',
      }

      const result = safeValidateContainer(validContainer)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.name).toBe('Test Container')
        expect(result.data.type).toBe('backpack')
      }
    })

    it('should return error result for invalid container', () => {
      const invalidContainer = {
        name: '',
        type: 'backpack',
      }

      const result = safeValidateContainer(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.errors).toHaveLength(1)
        expect(result.errors[0]).toContain('name')
      }
    })

    it('should return multiple errors for multiple invalid fields', () => {
      const invalidContainer = {
        name: '',
        price: -10,
        weight: -100,
      }

      const result = safeValidateContainer(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.errors.length).toBeGreaterThan(1)
      }
    })

    it('should format error messages with field paths', () => {
      const invalidContainer = {
        name: 'Test',
        type: 'backpack',
        url: 'invalid-url',
      }

      const result = safeValidateContainer(invalidContainer)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.errors[0]).toContain('url:')
      }
    })
  })

  describe('safeValidateItem', () => {
    it('should return success result for valid item', () => {
      const validItem = {
        name: 'Water Bottle',
        category: 'water',
        quantity: 1,
        weight: 300,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = safeValidateItem(validItem)
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data.name).toBe('Water Bottle')
        expect(result.data.category).toBe('water')
      }
    })

    it('should return error result for invalid item', () => {
      const invalidItem = {
        name: 'Test',
        category: '',
        quantity: 1,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = safeValidateItem(invalidItem)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.errors.length).toBeGreaterThan(0)
        expect(result.errors[0]).toContain('category')
      }
    })

    it('should return multiple errors for multiple invalid fields', () => {
      const invalidItem = {
        name: '',
        category: '',
        quantity: 0,
        weight: -100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = safeValidateItem(invalidItem)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.errors.length).toBeGreaterThan(1)
      }
    })

    it('should format error messages with field paths', () => {
      const invalidItem = {
        name: 'Test',
        category: 'water',
        quantity: 0,
        weight: 100,
        weightUnit: 'g',
        priority: 'medium',
        status: 'owned',
      }

      const result = safeValidateItem(invalidItem)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.errors[0]).toContain('quantity:')
      }
    })
  })

  describe('edge cases', () => {
    it('should handle null and undefined values appropriately', () => {
      const containerWithNulls = {
        name: 'Test',
        type: 'backpack',
        parentContainerId: null,
        description: undefined,
      }

      const result = safeValidateContainer(containerWithNulls)
      expect(result.success).toBe(true)
    })

    it('should handle unknown properties by ignoring them', () => {
      const containerWithExtra = {
        name: 'Test',
        type: 'backpack',
        unknownField: 'should be stripped',
      }

      const result = safeValidateContainer(containerWithExtra)
      expect(result.success).toBe(true)
      if (result.success) {
        expect('unknownField' in result.data).toBe(false)
      }
    })

    it('should validate weight units correctly', () => {
      const units = ['g', 'kg', 'oz', 'lb']

      for (const unit of units) {
        const item = {
          name: 'Test',
          category: 'water',
          quantity: 1,
          weight: 100,
          weightUnit: unit,
          priority: 'medium',
          status: 'owned',
        }

        const result = safeValidateItem(item)
        expect(result.success).toBe(true)
      }
    })

    it('should reject invalid weight units', () => {
      const item = {
        name: 'Test',
        category: 'water',
        quantity: 1,
        weight: 100,
        weightUnit: 'invalid',
        priority: 'medium',
        status: 'owned',
      }

      const result = safeValidateItem(item)
      expect(result.success).toBe(false)
    })
  })
})
