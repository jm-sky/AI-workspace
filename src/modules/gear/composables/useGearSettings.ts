import { computed } from 'vue'
import { config } from '@/shared/config/config'
import { useLocale } from '@/shared/i18n'
import type { IUpdateGearSettingsDto, IUserBrand, IUserCategory, IUserContainerType } from '../types/gearSettings.types'
import { useGearSettingsStore } from '../store/useGearSettingsStore'
import { detectDefaultCurrency, type SupportedCurrency } from '../utils/currencyFormatter'

/**
 * Composable for gear settings (custom categories, container types, brands, and preferred weight unit)
 */
export function useGearSettings() {
  const store = useGearSettingsStore()

  const { currentLocale } = useLocale()

  const settings = computed(() => ({
    customCategories: store.customCategories,
    customContainerTypes: store.customContainerTypes,
    customBrands: store.customBrands,
    preferredWeightUnit: store.preferredWeightUnit ?? config.defaults.preferredWeightUnit,
    defaultCurrency: store.defaultCurrency,
  }))

  const defaultCurrency = computed<SupportedCurrency>(() => {
    return (store.defaultCurrency as SupportedCurrency) || detectDefaultCurrency(currentLocale.value)
  })

  const customCategories = computed<IUserCategory[]>(() => store.getAllCategories)
  const customContainerTypes = computed<IUserContainerType[]>(() => store.getAllContainerTypes)
  const customBrands = computed<IUserBrand[]>(() => store.getAllBrands)

  const updateSettings = (data: IUpdateGearSettingsDto): void => {
    store.updateSettings(data)
  }

  const addCategory = (category: IUserCategory): void => {
    store.addCategory(category)
  }

  const updateCategory = (category: IUserCategory): void => {
    store.updateCategory(category)
  }

  const removeCategory = (id: string): void => {
    store.removeCategory(id)
  }

  const addContainerType = (containerType: IUserContainerType): void => {
    store.addContainerType(containerType)
  }

  const updateContainerType = (containerType: IUserContainerType): void => {
    store.updateContainerType(containerType)
  }

  const removeContainerType = (id: string): void => {
    store.removeContainerType(id)
  }

  const addBrand = (brand: IUserBrand): void => {
    store.addBrand(brand)
  }

  const updateBrand = (brand: IUserBrand): void => {
    store.updateBrand(brand)
  }

  const removeBrand = (id: string): void => {
    store.removeBrand(id)
  }

  return {
    settings,
    customCategories,
    customContainerTypes,
    customBrands,
    defaultCurrency,
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
  }
}

