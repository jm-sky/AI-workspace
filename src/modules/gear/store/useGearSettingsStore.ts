import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import type { IGearSettings, IUpdateGearSettingsDto, IUserBrand, IUserCategory, IUserContainerType } from '../types/gearSettings.types'
import { gearSettingsService } from '../services/gearSettingsService'

// Helper to load settings synchronously for initial state
// This is a workaround for store initialization - in the future this should be async
function loadSettingsSync(): IGearSettings {
  const stored = localStorage.getItem('gear-stack:gear-settings')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      return {
        customCategories: parsed.customCategories ?? [],
        customContainerTypes: parsed.customContainerTypes ?? [],
        customBrands: parsed.customBrands ?? [],
        preferredWeightUnit: parsed.preferredWeightUnit,
        defaultCurrency: parsed.defaultCurrency,
      }
    } catch {
      // Fall through to default
    }
  }
  return {
    customCategories: [],
    customContainerTypes: [],
    customBrands: [],
    defaultCurrency: undefined,
  }
}

export const useGearSettingsStore = defineStore('gearSettings', () => {
  const state = reactive<IGearSettings>(loadSettingsSync())

  const getAllCategories = computed<IUserCategory[]>(() => state.customCategories)
  const getAllContainerTypes = computed<IUserContainerType[]>(() => state.customContainerTypes)
  const getAllBrands = computed<IUserBrand[]>(() => state.customBrands)

  // Actions
  async function updateSettings(updates: IUpdateGearSettingsDto): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateSettings(state, updates)
    state.customCategories = updated.customCategories
    state.customContainerTypes = updated.customContainerTypes
    state.customBrands = updated.customBrands
    state.preferredWeightUnit = updated.preferredWeightUnit
    state.defaultCurrency = updated.defaultCurrency
  }

  async function addCategory(category: IUserCategory): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.addCategory(state, category)
    state.customCategories = updated.customCategories
  }

  async function updateCategory(category: IUserCategory): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateCategory(state, category)
    state.customCategories = updated.customCategories
  }

  async function removeCategory(categoryId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.removeCategory(state, categoryId)
    state.customCategories = updated.customCategories
  }

  async function addContainerType(containerType: IUserContainerType): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.addContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function updateContainerType(containerType: IUserContainerType): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function removeContainerType(containerTypeId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.removeContainerType(state, containerTypeId)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function addBrand(brand: IUserBrand): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.addBrand(state, brand)
    state.customBrands = updated.customBrands
  }

  async function updateBrand(brand: IUserBrand): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateBrand(state, brand)
    state.customBrands = updated.customBrands
  }

  async function removeBrand(brandId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.removeBrand(state, brandId)
    state.customBrands = updated.customBrands
  }

  async function loadFromStorageAction(): Promise<void> {
    const service = gearSettingsService()
    const loaded = await service.loadFromStorage()
    state.customCategories = loaded.customCategories
    state.customContainerTypes = loaded.customContainerTypes
    state.customBrands = loaded.customBrands
    state.preferredWeightUnit = loaded.preferredWeightUnit
    state.defaultCurrency = loaded.defaultCurrency
  }

  return {
    // State
    customCategories: computed(() => state.customCategories),
    customContainerTypes: computed(() => state.customContainerTypes),
    customBrands: computed(() => state.customBrands),
    preferredWeightUnit: computed(() => state.preferredWeightUnit),
    defaultCurrency: computed(() => state.defaultCurrency),

    // Getters
    getAllCategories,
    getAllContainerTypes,
    getAllBrands,

    // Actions
    updateSettings,
    addCategory,
    updateCategory,
    removeCategory,
    addContainerType,
    updateContainerType,
    removeContainerType,
    addBrand,
    updateBrand,
    removeBrand,
    loadFromStorage: loadFromStorageAction,
  }
})

