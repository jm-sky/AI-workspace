import { describe, expect, it } from 'vitest'
import { recognizeParameters, recognizeParametersForItems } from './parameterRecognition'

describe('parameterRecognition', () => {
  describe('recognizeParameters', () => {
    it('should return empty object for empty string', () => {
      expect(recognizeParameters('')).toEqual({})
      expect(recognizeParameters('   ')).toEqual({})
    })

    it('should recognize brand from suggested brands', () => {
      const result = recognizeParameters('Victorinox Knife')
      expect(result.brand).toBe('Victorinox')
    })

    it('should recognize brand case-insensitively', () => {
      const result = recognizeParameters('victorinox knife')
      expect(result.brand).toBe('Victorinox')
    })

    it('should recognize brand from custom brands', () => {
      const customBrands = [{ value: 'CustomBrand' }]
      const result = recognizeParameters('CustomBrand Item', customBrands)
      expect(result.brand).toBe('CustomBrand')
    })

    it('should recognize color from suggested colors', () => {
      const result = recognizeParameters('Black Knife')
      expect(result.color).toBe('Black')
    })

    it('should recognize color case-insensitively', () => {
      const result = recognizeParameters('black knife')
      expect(result.color).toBe('Black')
    })

    it('should recognize both brand and color', () => {
      const result = recognizeParameters('Victorinox Black Knife')
      expect(result.brand).toBe('Victorinox')
      expect(result.color).toBe('Black')
    })

    it('should match longer brand names first', () => {
      // "The North Face" should match before "North"
      const result = recognizeParameters('The North Face Backpack')
      expect(result.brand).toBe('The North Face')
    })

    it('should recognize hyphenated brand patterns', () => {
      const result = recognizeParameters('Materac M-TAC')
      expect(result.brand).toBe('M-TAC')
    })

    it('should recognize brand from first word if uppercase', () => {
      const result = recognizeParameters('Helikon Backpack')
      expect(result.brand).toBe('Helikon')
    })

    it('should not recognize common words as brands', () => {
      const result = recognizeParameters('the backpack')
      expect(result.brand).toBeUndefined()
    })

    it('should handle brand at the beginning of name', () => {
      const result = recognizeParameters('Osprey Backpack')
      expect(result.brand).toBe('Osprey')
    })

    it('should handle brand in the middle of name', () => {
      const result = recognizeParameters('Tactical Victorinox Knife')
      expect(result.brand).toBe('Victorinox')
    })

    it('should match longer color names first', () => {
      const result = recognizeParameters('OD Green Backpack')
      expect(result.color).toBe('OD Green')
    })

    it('should return empty object when no matches found', () => {
      // Use lowercase to avoid brand pattern matching
      const result = recognizeParameters('random item name')
      expect(result).toEqual({})
    })

    it('should handle special characters in brand names', () => {
      const result = recognizeParameters("Arc'teryx Jacket")
      expect(result.brand).toBe("Arc'teryx")
    })

    it('should handle multiple word brand names', () => {
      const result = recognizeParameters('5.11 Tactical Pants')
      expect(result.brand).toBe('5.11 Tactical')
    })
  })

  describe('recognizeParametersForItems', () => {
    it('should return empty map for empty array', () => {
      const result = recognizeParametersForItems([])
      expect(result.size).toBe(0)
    })

    it('should recognize parameters for multiple items', () => {
      const items = [
        { id: '1', name: 'Victorinox Knife' },
        { id: '2', name: 'Black Backpack' },
        { id: '3', name: 'random item' }, // lowercase to avoid brand pattern matching
      ]

      const result = recognizeParametersForItems(items)

      expect(result.size).toBe(2)
      expect(result.get('1')?.brand).toBe('Victorinox')
      expect(result.get('2')?.color).toBe('Black')
      expect(result.get('3')).toBeUndefined()
    })

    it('should only include items with recognized parameters', () => {
      const items = [
        { id: '1', name: 'random item' }, // lowercase to avoid brand pattern matching
        { id: '2', name: 'another random item' }, // lowercase to avoid brand pattern matching
      ]

      const result = recognizeParametersForItems(items)

      expect(result.size).toBe(0)
    })

    it('should handle items with both brand and color', () => {
      const items = [
        { id: '1', name: 'Victorinox Black Knife' },
      ]

      const result = recognizeParametersForItems(items)

      expect(result.size).toBe(1)
      const params = result.get('1')
      expect(params?.brand).toBe('Victorinox')
      expect(params?.color).toBe('Black')
    })
  })
})

