/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it } from 'vitest'
import { GRAMS_PER_KILOGRAM, GRAMS_PER_OUNCE, GRAMS_PER_POUND } from './constants'
import {
  convertFromGrams,
  convertToGrams,
  formatWeight,
  formatWeightFromGrams,
  formatWeightToPreferredUnit,
  formatWeightWithPreferredUnit,
} from './formatWeight'

describe('formatWeight', () => {
  describe('convertToGrams', () => {
    it('should convert grams to grams (no conversion)', () => {
      expect(convertToGrams(500, 'g')).toBe(500)
    })

    it('should convert kilograms to grams', () => {
      expect(convertToGrams(1, 'kg')).toBe(GRAMS_PER_KILOGRAM)
      expect(convertToGrams(2.5, 'kg')).toBe(2.5 * GRAMS_PER_KILOGRAM)
    })

    it('should convert pounds to grams', () => {
      expect(convertToGrams(1, 'lb')).toBe(GRAMS_PER_POUND)
      expect(convertToGrams(2, 'lb')).toBe(2 * GRAMS_PER_POUND)
    })

    it('should convert ounces to grams', () => {
      expect(convertToGrams(1, 'oz')).toBe(GRAMS_PER_OUNCE)
      expect(convertToGrams(16, 'oz')).toBe(16 * GRAMS_PER_OUNCE)
    })

    it('should default to grams for unknown unit', () => {
      expect(convertToGrams(100, 'g' as any)).toBe(100)
    })
  })

  describe('convertFromGrams', () => {
    it('should convert grams to grams (no conversion)', () => {
      expect(convertFromGrams(500, 'g')).toBe(500)
    })

    it('should convert grams to kilograms', () => {
      expect(convertFromGrams(GRAMS_PER_KILOGRAM, 'kg')).toBe(1)
      expect(convertFromGrams(2500, 'kg')).toBe(2.5)
    })

    it('should convert grams to pounds', () => {
      expect(convertFromGrams(GRAMS_PER_POUND, 'lb')).toBe(1)
      expect(convertFromGrams(GRAMS_PER_POUND * 2, 'lb')).toBe(2)
    })

    it('should convert grams to ounces', () => {
      expect(convertFromGrams(GRAMS_PER_OUNCE, 'oz')).toBe(1)
      expect(convertFromGrams(GRAMS_PER_OUNCE * 16, 'oz')).toBe(16)
    })

    it('should default to grams for unknown unit', () => {
      expect(convertFromGrams(100, 'g' as any)).toBe(100)
    })
  })

  describe('formatWeight', () => {
    it('should format grams without decimals', () => {
      expect(formatWeight(500, 'g')).toBe('500 g')
      expect(formatWeight(100, 'g')).toBe('100 g')
    })

    it('should format kilograms with decimals', () => {
      expect(formatWeight(1.5, 'kg')).toBe('1.50 kg')
      expect(formatWeight(2, 'kg')).toBe('2.00 kg')
    })

    it('should format pounds with decimals', () => {
      expect(formatWeight(2.5, 'lb')).toBe('2.50 lb')
      expect(formatWeight(1, 'lb')).toBe('1.00 lb')
    })

    it('should format ounces with decimals', () => {
      expect(formatWeight(16, 'oz')).toBe('16.00 oz')
      expect(formatWeight(8.5, 'oz')).toBe('8.50 oz')
    })

    describe('locale support', () => {
      it('should format with en-US locale (dot as decimal separator)', () => {
        expect(formatWeight(1.5, 'kg', 'en-US')).toBe('1.50 kg')
        expect(formatWeight(2.5, 'lb', 'en-US')).toBe('2.50 lb')
        expect(formatWeight(1000, 'g', 'en-US')).toBe('1000 g')
      })

      it('should format with pl-PL locale (comma as decimal separator)', () => {
        expect(formatWeight(1.5, 'kg', 'pl-PL')).toBe('1,50 kg')
        expect(formatWeight(2.5, 'lb', 'pl-PL')).toBe('2,50 lb')
        expect(formatWeight(1000, 'g', 'pl-PL')).toBe('1000 g')
      })

      it('should format large values with thousand separators (en-US)', () => {
        // en-US uses comma as thousand separator and dot as decimal separator
        expect(formatWeight(10000, 'kg', 'en-US')).toBe('10,000.00 kg')
        expect(formatWeight(100000, 'kg', 'en-US')).toBe('100,000.00 kg')
        expect(formatWeight(10000, 'lb', 'en-US')).toBe('10,000.00 lb')
      })

      it('should format large values with thousand separators (pl-PL)', () => {
        // pl-PL uses non-breaking space (U+00A0) as thousand separator and comma as decimal separator
        const nbsp = '\u00A0'
        expect(formatWeight(10000, 'kg', 'pl-PL')).toBe(`10${nbsp}000,00 kg`)
        expect(formatWeight(100000, 'kg', 'pl-PL')).toBe(`100${nbsp}000,00 kg`)
        expect(formatWeight(10000, 'lb', 'pl-PL')).toBe(`10${nbsp}000,00 lb`)
      })
    })
  })

  describe('formatWeightFromGrams', () => {
    it('should format as kg when weight >= 1000g', () => {
      expect(formatWeightFromGrams(1000)).toBe('1.00 kg')
      expect(formatWeightFromGrams(2500)).toBe('2.50 kg')
    })

    it('should format as g when weight < 1000g', () => {
      expect(formatWeightFromGrams(500)).toBe('500 g')
      expect(formatWeightFromGrams(999)).toBe('999 g')
    })

    it('should handle zero weight', () => {
      expect(formatWeightFromGrams(0)).toBe('0 g')
    })

    describe('locale support', () => {
      it('should format with en-US locale', () => {
        expect(formatWeightFromGrams(1000, 'en-US')).toBe('1.00 kg')
        expect(formatWeightFromGrams(2500, 'en-US')).toBe('2.50 kg')
        expect(formatWeightFromGrams(500, 'en-US')).toBe('500 g')
      })

      it('should format with pl-PL locale', () => {
        expect(formatWeightFromGrams(1000, 'pl-PL')).toBe('1,00 kg')
        expect(formatWeightFromGrams(2500, 'pl-PL')).toBe('2,50 kg')
        expect(formatWeightFromGrams(500, 'pl-PL')).toBe('500 g')
      })

      it('should format large values with thousand separators (en-US)', () => {
        expect(formatWeightFromGrams(10000000, 'en-US')).toBe('10,000.00 kg')
        expect(formatWeightFromGrams(100000000, 'en-US')).toBe('100,000.00 kg')
      })

      it('should format large values with thousand separators (pl-PL)', () => {
        // pl-PL uses non-breaking space (U+00A0) as thousand separator
        const nbsp = '\u00A0'
        expect(formatWeightFromGrams(10000000, 'pl-PL')).toBe(`10${nbsp}000,00 kg`)
        expect(formatWeightFromGrams(100000000, 'pl-PL')).toBe(`100${nbsp}000,00 kg`)
      })
    })
  })

  describe('formatWeightToPreferredUnit', () => {
    it('should format to grams', () => {
      expect(formatWeightToPreferredUnit(500, 'g')).toBe('500 g')
      expect(formatWeightToPreferredUnit(0, 'g')).toBe('0 g')
    })

    it('should format to kilograms', () => {
      expect(formatWeightToPreferredUnit(1000, 'kg')).toBe('1.00 kg')
      expect(formatWeightToPreferredUnit(2500, 'kg')).toBe('2.50 kg')
    })

    it('should format to pounds', () => {
      const weightInGrams = GRAMS_PER_POUND
      expect(formatWeightToPreferredUnit(weightInGrams, 'lb')).toBe('1.00 lb')
    })

    it('should format to ounces', () => {
      const weightInGrams = GRAMS_PER_OUNCE
      expect(formatWeightToPreferredUnit(weightInGrams, 'oz')).toBe('1.00 oz')
    })

    describe('locale support', () => {
      it('should format with en-US locale', () => {
        expect(formatWeightToPreferredUnit(1000, 'kg', 'en-US')).toBe('1.00 kg')
        expect(formatWeightToPreferredUnit(GRAMS_PER_POUND, 'lb', 'en-US')).toBe('1.00 lb')
        expect(formatWeightToPreferredUnit(500, 'g', 'en-US')).toBe('500 g')
      })

      it('should format with pl-PL locale', () => {
        expect(formatWeightToPreferredUnit(1000, 'kg', 'pl-PL')).toBe('1,00 kg')
        expect(formatWeightToPreferredUnit(GRAMS_PER_POUND, 'lb', 'pl-PL')).toBe('1,00 lb')
        expect(formatWeightToPreferredUnit(500, 'g', 'pl-PL')).toBe('500 g')
      })

      it('should format large values with thousand separators (en-US)', () => {
        expect(formatWeightToPreferredUnit(10000000, 'kg', 'en-US')).toBe('10,000.00 kg')
        expect(formatWeightToPreferredUnit(100000000, 'kg', 'en-US')).toBe('100,000.00 kg')
      })

      it('should format large values with thousand separators (pl-PL)', () => {
        // pl-PL uses non-breaking space (U+00A0) as thousand separator
        const nbsp = '\u00A0'
        expect(formatWeightToPreferredUnit(10000000, 'kg', 'pl-PL')).toBe(`10${nbsp}000,00 kg`)
        expect(formatWeightToPreferredUnit(100000000, 'kg', 'pl-PL')).toBe(`100${nbsp}000,00 kg`)
      })
    })
  })

  describe('formatWeightWithPreferredUnit', () => {
    it('should convert from kg to g', () => {
      const result = formatWeightWithPreferredUnit(1, 'kg', 'g')
      expect(result).toBe('1000 g')
    })

    it('should convert from g to kg', () => {
      const result = formatWeightWithPreferredUnit(1000, 'g', 'kg')
      expect(result).toBe('1.00 kg')
    })

    it('should convert from lb to oz', () => {
      const result = formatWeightWithPreferredUnit(1, 'lb', 'oz')
      // 1 lb = 16 oz
      expect(result).toBe('16.00 oz')
    })

    it('should convert from oz to g', () => {
      const result = formatWeightWithPreferredUnit(1, 'oz', 'g')
      expect(result).toBe(`${GRAMS_PER_OUNCE} g`)
    })

    it('should handle same unit conversion', () => {
      expect(formatWeightWithPreferredUnit(500, 'g', 'g')).toBe('500 g')
      expect(formatWeightWithPreferredUnit(2, 'kg', 'kg')).toBe('2.00 kg')
    })

    describe('locale support', () => {
      it('should format with en-US locale', () => {
        expect(formatWeightWithPreferredUnit(1000, 'g', 'kg', 'en-US')).toBe('1.00 kg')
        expect(formatWeightWithPreferredUnit(1, 'lb', 'oz', 'en-US')).toBe('16.00 oz')
        expect(formatWeightWithPreferredUnit(1, 'oz', 'g', 'en-US')).toBe(`${GRAMS_PER_OUNCE} g`)
      })

      it('should format with pl-PL locale', () => {
        expect(formatWeightWithPreferredUnit(1000, 'g', 'kg', 'pl-PL')).toBe('1,00 kg')
        expect(formatWeightWithPreferredUnit(1, 'lb', 'oz', 'pl-PL')).toBe('16,00 oz')
        expect(formatWeightWithPreferredUnit(1, 'oz', 'g', 'pl-PL')).toBe(`${GRAMS_PER_OUNCE} g`)
      })

      it('should format large values with thousand separators (en-US)', () => {
        expect(formatWeightWithPreferredUnit(10000, 'kg', 'kg', 'en-US')).toBe('10,000.00 kg')
        expect(formatWeightWithPreferredUnit(100000, 'kg', 'kg', 'en-US')).toBe('100,000.00 kg')
        expect(formatWeightWithPreferredUnit(10000, 'lb', 'lb', 'en-US')).toBe('10,000.00 lb')
      })

      it('should format large values with thousand separators (pl-PL)', () => {
        // pl-PL uses non-breaking space (U+00A0) as thousand separator
        const nbsp = '\u00A0'
        expect(formatWeightWithPreferredUnit(10000, 'kg', 'kg', 'pl-PL')).toBe(`10${nbsp}000,00 kg`)
        expect(formatWeightWithPreferredUnit(100000, 'kg', 'kg', 'pl-PL')).toBe(`100${nbsp}000,00 kg`)
        expect(formatWeightWithPreferredUnit(10000, 'lb', 'lb', 'pl-PL')).toBe(`10${nbsp}000,00 lb`)
      })
    })
  })

  describe('round-trip conversions', () => {
    it('should maintain accuracy in kg to g to kg conversion', () => {
      const original = 2.5
      const inGrams = convertToGrams(original, 'kg')
      const backToKg = convertFromGrams(inGrams, 'kg')
      expect(backToKg).toBeCloseTo(original, 5)
    })

    it('should maintain accuracy in lb to g to lb conversion', () => {
      const original = 5
      const inGrams = convertToGrams(original, 'lb')
      const backToLb = convertFromGrams(inGrams, 'lb')
      expect(backToLb).toBeCloseTo(original, 5)
    })

    it('should maintain accuracy in oz to g to oz conversion', () => {
      const original = 16
      const inGrams = convertToGrams(original, 'oz')
      const backToOz = convertFromGrams(inGrams, 'oz')
      expect(backToOz).toBeCloseTo(original, 5)
    })
  })
})

