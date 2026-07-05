import { describe, expect, it } from 'vitest'
import type { TGearItemCategory } from '../types/gear.types'
import { CATEGORY_ICONS, getCategoryIcon } from './categoryIcons'

describe('categoryIcons', () => {
  describe('CATEGORY_ICONS', () => {
    it('should have icons for all default categories', () => {
      const defaultCategories: TGearItemCategory[] = [
        'water',
        'food',
        'shelter',
        'fire',
        'firstAid',
        'blades',
        'tools',
        'light',
        'navigation',
        'communication',
        'clothing',
        'hygiene',
        'other',
      ]

      defaultCategories.forEach(category => {
        expect(CATEGORY_ICONS[category]).toBeDefined()
        expect(CATEGORY_ICONS[category]).not.toBeNull()
      })
    })

    it('should have PocketKnife icon for blades category', () => {
      expect(CATEGORY_ICONS.blades).toBeDefined()
      expect(CATEGORY_ICONS.blades).not.toBeNull()
    })
  })

  describe('getCategoryIcon', () => {
    it('should return correct icon for known categories', () => {
      expect(getCategoryIcon('water')).toBe(CATEGORY_ICONS.water)
      expect(getCategoryIcon('food')).toBe(CATEGORY_ICONS.food)
      expect(getCategoryIcon('shelter')).toBe(CATEGORY_ICONS.shelter)
      expect(getCategoryIcon('fire')).toBe(CATEGORY_ICONS.fire)
      expect(getCategoryIcon('firstAid')).toBe(CATEGORY_ICONS.firstAid)
      expect(getCategoryIcon('blades')).toBe(CATEGORY_ICONS.blades)
      expect(getCategoryIcon('tools')).toBe(CATEGORY_ICONS.tools)
      expect(getCategoryIcon('light')).toBe(CATEGORY_ICONS.light)
      expect(getCategoryIcon('navigation')).toBe(CATEGORY_ICONS.navigation)
      expect(getCategoryIcon('communication')).toBe(CATEGORY_ICONS.communication)
      expect(getCategoryIcon('clothing')).toBe(CATEGORY_ICONS.clothing)
      expect(getCategoryIcon('hygiene')).toBe(CATEGORY_ICONS.hygiene)
      expect(getCategoryIcon('other')).toBe(CATEGORY_ICONS.other)
    })

    it('should return other icon for unknown categories', () => {
      expect(getCategoryIcon('unknownCategory' as TGearItemCategory)).toBe(
        CATEGORY_ICONS.other
      )
      expect(getCategoryIcon('customCategory' as TGearItemCategory)).toBe(
        CATEGORY_ICONS.other
      )
    })

    it('should return other icon for empty string', () => {
      expect(getCategoryIcon('' as TGearItemCategory)).toBe(CATEGORY_ICONS.other)
    })
  })
})
