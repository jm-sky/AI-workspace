import { describe, expect, it } from 'vitest'
import { isSet } from './helpers'

describe('helpers', () => {
  describe('isSet', () => {
    it('should return true for defined non-null values', () => {
      expect(isSet('string')).toBe(true)
      expect(isSet(0)).toBe(true)
      expect(isSet(false)).toBe(true)
      expect(isSet('')).toBe(true)
      expect(isSet([])).toBe(true)
      expect(isSet({})).toBe(true)
    })

    it('should return false for undefined', () => {
      expect(isSet(undefined)).toBe(false)
    })

    it('should return false for null', () => {
      expect(isSet(null)).toBe(false)
    })

    it('should narrow type correctly', () => {
      const value: string | undefined | null = 'test'
      
      if (isSet(value)) {
        // TypeScript should know value is string here
        expect(typeof value).toBe('string')
        expect(value.toUpperCase()).toBe('TEST')
      }
    })

    it('should handle numbers including zero', () => {
      expect(isSet(0)).toBe(true)
      expect(isSet(-1)).toBe(true)
      expect(isSet(1)).toBe(true)
      expect(isSet(3.14)).toBe(true)
    })

    it('should handle boolean values', () => {
      expect(isSet(true)).toBe(true)
      expect(isSet(false)).toBe(true)
    })

    it('should handle empty strings and arrays', () => {
      expect(isSet('')).toBe(true)
      expect(isSet([])).toBe(true)
      expect(isSet({})).toBe(true)
    })
  })
})

