import { useBackend } from '@/shared/composables/useBackend'
import { GEAR_SETTINGS_STORAGE_KEY, SETTINGS_STORAGE_KEY } from '@/shared/config/config'
import { logger } from '@/shared/utils/logger'
import type {
  IGearSettings,
  IGearSettingsService,
  IUpdateGearSettingsDto,
  IUserBrand,
  IUserCategory,
  IUserContainerType,
} from '../types/gearSettings.types'
import { gearSettingsApiService } from './gearSettingsApiService'

/**
 * Gear Settings Service (LocalStorage implementation)
 * Handles gear-specific settings: custom categories and container types
 * Implements IGearSettingsService interface for localStorage-based operations.
 */
class GearSettingsService implements IGearSettingsService {
  private static readonly STORAGE_KEY = GEAR_SETTINGS_STORAGE_KEY
  private static readonly OLD_STORAGE_KEY = SETTINGS_STORAGE_KEY // For migration

  /**
   * Migrate from old storage format if needed
   */
  private migrateFromOldStorage(): Partial<IGearSettings> | null {
    const oldStored = localStorage.getItem(GearSettingsService.OLD_STORAGE_KEY)
    if (!oldStored) return null

    try {
      const oldSettings = JSON.parse(oldStored)
      return {
        customCategories: oldSettings.customCategories,
        customContainerTypes: oldSettings.customContainerTypes,
      }
    } catch {
      return null
    }
  }

  /**
   * Load gear settings from localStorage
   */
  async loadFromStorage(): Promise<IGearSettings> {
    const stored = localStorage.getItem(GearSettingsService.STORAGE_KEY)
    let settings: Partial<IGearSettings> = {}

    if (stored) {
      try {
        settings = JSON.parse(stored)
      } catch (error) {
        console.error('Error loading gear settings from storage:', error)
      }
    } else {
      // Try to migrate from old storage
      const migrated = this.migrateFromOldStorage()
      if (migrated) {
        settings = migrated
        // Save to new location
        await this.saveToStorage({
          customCategories: migrated.customCategories ?? [],
          customContainerTypes: migrated.customContainerTypes ?? [],
          customBrands: [],
        })
      }
    }

    return Promise.resolve({
      customCategories: settings.customCategories ?? [],
      customContainerTypes: settings.customContainerTypes ?? [],
      customBrands: settings.customBrands ?? [],
      preferredWeightUnit: settings.preferredWeightUnit,
      defaultCurrency: settings.defaultCurrency,
    })
  }

  /**
   * Save gear settings to localStorage
   */
  async saveToStorage(settings: IGearSettings): Promise<void> {
    try {
      localStorage.setItem(GearSettingsService.STORAGE_KEY, JSON.stringify({
        customCategories: settings.customCategories,
        customContainerTypes: settings.customContainerTypes,
        customBrands: settings.customBrands,
        preferredWeightUnit: settings.preferredWeightUnit,
        defaultCurrency: settings.defaultCurrency,
      }))
      return Promise.resolve()
    } catch (error) {
      console.error('Error saving gear settings to storage:', error)
      return Promise.reject(error)
    }
  }

  /**
   * Update gear settings
   */
  async updateSettings(current: IGearSettings, updates: IUpdateGearSettingsDto): Promise<IGearSettings> {
    const updated: IGearSettings = {
      customCategories: updates.customCategories ?? current.customCategories,
      customContainerTypes: updates.customContainerTypes ?? current.customContainerTypes,
      customBrands: updates.customBrands ?? current.customBrands,
      preferredWeightUnit: updates.preferredWeightUnit ?? current.preferredWeightUnit,
      defaultCurrency: updates.defaultCurrency ?? current.defaultCurrency,
    }

    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Generic helper: Add item to array
   */
  private async addToArray<T extends { id: string }>(
    settings: IGearSettings,
    key: 'customCategories' | 'customContainerTypes' | 'customBrands',
    item: T,
  ): Promise<IGearSettings> {
    const updated = {
      ...settings,
      [key]: [...(settings[key] as unknown as T[]), item],
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Generic helper: Update item in array by ID
   */
  private async updateInArray<T extends { id: string }>(
    settings: IGearSettings,
    key: 'customCategories' | 'customContainerTypes' | 'customBrands',
    item: T,
  ): Promise<IGearSettings> {
    const updated = {
      ...settings,
      [key]: (settings[key] as unknown as T[]).map(existing => existing.id === item.id ? item : existing),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Generic helper: Remove item from array by ID
   */
  private async removeFromArray(
    settings: IGearSettings,
    key: 'customCategories' | 'customContainerTypes' | 'customBrands',
    itemId: string,
  ): Promise<IGearSettings> {
    const updated = {
      ...settings,
      [key]: (settings[key] as Array<{ id: string }>).filter(item => item.id !== itemId),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Add a custom category
   */
  async addCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
    return this.addToArray(settings, 'customCategories', category)
  }

  /**
   * Update a custom category
   */
  async updateCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
    return this.updateInArray(settings, 'customCategories', category)
  }

  /**
   * Remove a custom category
   */
  async removeCategory(settings: IGearSettings, categoryId: string): Promise<IGearSettings> {
    return this.removeFromArray(settings, 'customCategories', categoryId)
  }

  /**
   * Add a custom container type
   */
  async addContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
    return this.addToArray(settings, 'customContainerTypes', containerType)
  }

  /**
   * Update a custom container type
   */
  async updateContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
    return this.updateInArray(settings, 'customContainerTypes', containerType)
  }

  /**
   * Remove a custom container type
   */
  async removeContainerType(settings: IGearSettings, containerTypeId: string): Promise<IGearSettings> {
    return this.removeFromArray(settings, 'customContainerTypes', containerTypeId)
  }

  /**
   * Add a custom brand
   */
  async addBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
    return this.addToArray(settings, 'customBrands', brand)
  }

  /**
   * Update a custom brand
   */
  async updateBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
    return this.updateInArray(settings, 'customBrands', brand)
  }

  /**
   * Remove a custom brand
   */
  async removeBrand(settings: IGearSettings, brandId: string): Promise<IGearSettings> {
    return this.removeFromArray(settings, 'customBrands', brandId)
  }

  // Static helper methods for backward compatibility
  // Generic wrapper that creates instance and delegates to instance method
  private static delegate<TArgs extends unknown[], TReturn>(
    method: (instance: GearSettingsService, ...args: TArgs) => TReturn,
  ): (...args: TArgs) => TReturn {
    return (...args: TArgs) => {
      const instance = new GearSettingsService()
      return method(instance, ...args)
    }
  }

  static loadFromStorage = GearSettingsService.delegate((inst) => inst.loadFromStorage())
  static saveToStorage = GearSettingsService.delegate((inst, settings: IGearSettings) => inst.saveToStorage(settings))
  static updateSettings = GearSettingsService.delegate((inst, current: IGearSettings, updates: IUpdateGearSettingsDto) => inst.updateSettings(current, updates))
  static addCategory = GearSettingsService.delegate((inst, settings: IGearSettings, category: IUserCategory) => inst.addCategory(settings, category))
  static updateCategory = GearSettingsService.delegate((inst, settings: IGearSettings, category: IUserCategory) => inst.updateCategory(settings, category))
  static removeCategory = GearSettingsService.delegate((inst, settings: IGearSettings, categoryId: string) => inst.removeCategory(settings, categoryId))
  static addContainerType = GearSettingsService.delegate((inst, settings: IGearSettings, containerType: IUserContainerType) => inst.addContainerType(settings, containerType))
  static updateContainerType = GearSettingsService.delegate((inst, settings: IGearSettings, containerType: IUserContainerType) => inst.updateContainerType(settings, containerType))
  static removeContainerType = GearSettingsService.delegate((inst, settings: IGearSettings, containerTypeId: string) => inst.removeContainerType(settings, containerTypeId))
  static addBrand = GearSettingsService.delegate((inst, settings: IGearSettings, brand: IUserBrand) => inst.addBrand(settings, brand))
  static updateBrand = GearSettingsService.delegate((inst, settings: IGearSettings, brand: IUserBrand) => inst.updateBrand(settings, brand))
  static removeBrand = GearSettingsService.delegate((inst, settings: IGearSettings, brandId: string) => inst.removeBrand(settings, brandId))
}

export { GearSettingsService }

/**
 * Gear Settings Service Factory
 *
 * Returns appropriate service based on backend status and authentication.
 * When backend is enabled AND user is authenticated, uses API service with localStorage backup.
 * Otherwise, uses localStorage service.
 */
export const gearSettingsService = () => {
  const { shouldUseAPI } = useBackend()

  if (shouldUseAPI.value) {
    // Wrap API service to sync localStorage as backup
    const localService = new GearSettingsService()
    return {
      async loadFromStorage(): Promise<IGearSettings> {
        try {
          const settings = await gearSettingsApiService.getSettings()
          // Save to localStorage as backup
          await localService.saveToStorage(settings)
          return settings
        } catch (error) {
          // Fallback to localStorage on API error
          logger.warn('API failed, falling back to localStorage', error)
          return localService.loadFromStorage()
        }
      },
      async saveToStorage(settings: IGearSettings): Promise<void> {
        try {
          await gearSettingsApiService.updateSettings(settings)
          // Also save to localStorage as backup
          await localService.saveToStorage(settings)
        } catch (error) {
          // Fallback to localStorage on API error
          logger.warn('API failed, falling back to localStorage', error)
          await localService.saveToStorage(settings)
        }
      },
      async updateSettings(current: IGearSettings, updates: IUpdateGearSettingsDto): Promise<IGearSettings> {
        try {
          const updated = await gearSettingsApiService.updateSettings(updates)
          // Also save to localStorage as backup
          await localService.saveToStorage(updated)
          return updated
        } catch (error) {
          // Fallback to localStorage on API error
          logger.warn('API failed, falling back to localStorage', error)
          return localService.updateSettings(current, updates)
        }
      },
      async addCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customCategories: [...settings.customCategories, category],
        }
        return this.updateSettings(settings, { customCategories: updated.customCategories })
      },
      async updateCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customCategories: settings.customCategories.map(c => c.id === category.id ? category : c),
        }
        return this.updateSettings(settings, { customCategories: updated.customCategories })
      },
      async removeCategory(settings: IGearSettings, categoryId: string): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customCategories: settings.customCategories.filter(c => c.id !== categoryId),
        }
        return this.updateSettings(settings, { customCategories: updated.customCategories })
      },
      async addContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customContainerTypes: [...settings.customContainerTypes, containerType],
        }
        return this.updateSettings(settings, { customContainerTypes: updated.customContainerTypes })
      },
      async updateContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customContainerTypes: settings.customContainerTypes.map(t => t.id === containerType.id ? containerType : t),
        }
        return this.updateSettings(settings, { customContainerTypes: updated.customContainerTypes })
      },
      async removeContainerType(settings: IGearSettings, containerTypeId: string): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customContainerTypes: settings.customContainerTypes.filter(t => t.id !== containerTypeId),
        }
        return this.updateSettings(settings, { customContainerTypes: updated.customContainerTypes })
      },
      async addBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customBrands: [...settings.customBrands, brand],
        }
        return this.updateSettings(settings, { customBrands: updated.customBrands })
      },
      async updateBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customBrands: settings.customBrands.map(b => b.id === brand.id ? brand : b),
        }
        return this.updateSettings(settings, { customBrands: updated.customBrands })
      },
      async removeBrand(settings: IGearSettings, brandId: string): Promise<IGearSettings> {
        const updated = {
          ...settings,
          customBrands: settings.customBrands.filter(b => b.id !== brandId),
        }
        return this.updateSettings(settings, { customBrands: updated.customBrands })
      },
    }
  }

  // Use localStorage service when backend is not available
  return new GearSettingsService()
}
