import { describe, expect, it } from 'vitest'
import { getBrandOptions, getColorHex, getColorOptions } from './suggestedValues'

describe('suggestedValues', () => {
  describe('getColorHex', () => {
    it('should return hex for known color names', () => {
      expect(getColorHex('Black')).toBe('#000000')
      expect(getColorHex('Olive')).toBe('#808000')
      expect(getColorHex('Coyote')).toBe('#8A6642')
    })

    it('should be case-insensitive', () => {
      expect(getColorHex('black')).toBe('#000000')
      expect(getColorHex('BLACK')).toBe('#000000')
      expect(getColorHex('Black')).toBe('#000000')
    })

    it('should handle spaces and hyphens', () => {
      expect(getColorHex('OD Green')).toBe('#006B3C')
      expect(getColorHex('od-green')).toBe('#006B3C')
      expect(getColorHex('Ranger Green')).toBe('#007236')
      expect(getColorHex('ranger-green')).toBe('#007236')
    })

    it('should return null for unknown colors', () => {
      expect(getColorHex('UnknownColor')).toBeNull()
      expect(getColorHex('PurpleRain')).toBeNull()
    })

    it('should return null for null or undefined', () => {
      expect(getColorHex(null)).toBeNull()
      expect(getColorHex(undefined)).toBeNull()
    })

    it('should trim whitespace', () => {
      expect(getColorHex('  Black  ')).toBe('#000000')
      expect(getColorHex('\tOlive\n')).toBe('#808000')
    })

    it('should handle grey as gray', () => {
      expect(getColorHex('Grey')).toBe('#808080')
      expect(getColorHex('grey')).toBe('#808080')
    })
  })

  describe('getColorOptions', () => {
    it('should return array of color options', () => {
      const options = getColorOptions()
      expect(Array.isArray(options)).toBe(true)
      expect(options.length).toBeGreaterThan(0)
    })

    it('should include value, label, and data for each color', () => {
      const options = getColorOptions()
      const firstOption = options[0]
      
      expect(firstOption).toHaveProperty('value')
      expect(firstOption).toHaveProperty('label')
      expect(firstOption).toHaveProperty('data')
    })

    it('should have matching value and label', () => {
      const options = getColorOptions()
      options.forEach(option => {
        expect(option.value).toBe(option.label)
      })
    })

    it('should include hex color in data when available', () => {
      const options = getColorOptions()
      const blackOption = options.find(opt => opt.value === 'Black')
      
      expect(blackOption?.data).toBe('#000000')
    })

    it('should fallback to color name in data when hex not available', () => {
      // This test assumes there might be colors without hex mappings
      // Adjust based on actual implementation
      const options = getColorOptions()
      options.forEach(option => {
        expect(typeof option.data).toBe('string')
        expect(option.data.length).toBeGreaterThan(0)
      })
    })
  })

  describe('getBrandOptions', () => {
    it('should return array of brand options', () => {
      const options = getBrandOptions()
      expect(Array.isArray(options)).toBe(true)
      expect(options.length).toBeGreaterThan(0)
    })

    it('should include value and label for each brand', () => {
      const options = getBrandOptions()
      const firstOption = options[0]
      
      expect(firstOption).toHaveProperty('value')
      expect(firstOption).toHaveProperty('label')
    })

    it('should have matching value and label', () => {
      const options = getBrandOptions()
      options.forEach(option => {
        expect(option.value).toBe(option.label)
      })
    })

    it('should include default brands', () => {
      const options = getBrandOptions()
      const brandValues = options.map(opt => opt.value)
      
      expect(brandValues).toContain('Victorinox')
      expect(brandValues).toContain('Helikon')
      expect(brandValues).toContain('Osprey')
    })

    it('should include custom brands when provided', () => {
      const customBrands = [
        { value: 'CustomBrand1' },
        { value: 'CustomBrand2' },
      ]
      
      const options = getBrandOptions(customBrands)
      const brandValues = options.map(opt => opt.value)
      
      expect(brandValues).toContain('CustomBrand1')
      expect(brandValues).toContain('CustomBrand2')
    })

    it('should combine default and custom brands', () => {
      const customBrands = [{ value: 'CustomBrand' }]
      const options = getBrandOptions(customBrands)
      
      const brandValues = options.map(opt => opt.value)
      expect(brandValues).toContain('Victorinox') // Default
      expect(brandValues).toContain('CustomBrand') // Custom
    })

    it('should remove duplicate brands', () => {
      const customBrands = [
        { value: 'Victorinox' }, // Duplicate of default
        { value: 'CustomBrand' },
      ]
      
      const options = getBrandOptions(customBrands)
      const brandValues = options.map(opt => opt.value)
      const victorinoxCount = brandValues.filter(v => v === 'Victorinox').length
      
      expect(victorinoxCount).toBe(1) // Should only appear once
    })

    it('should handle empty custom brands array', () => {
      const optionsWithEmpty = getBrandOptions([])
      const optionsWithUndefined = getBrandOptions()
      
      expect(optionsWithEmpty.length).toBe(optionsWithUndefined.length)
    })

    it('should handle undefined custom brands', () => {
      const options = getBrandOptions(undefined)
      expect(Array.isArray(options)).toBe(true)
      expect(options.length).toBeGreaterThan(0)
    })
  })
})

