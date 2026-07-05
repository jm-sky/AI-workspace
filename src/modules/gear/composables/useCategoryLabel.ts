import { computed, type Reactive, type Ref, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGearSettings } from './useGearSettings'

export const useCategoryLabel = (categoryValue?: Ref<string> | Reactive<string> | string) => {
  const { t } = useI18n()
  const { customCategories } = useGearSettings()

  const getCategoryLabel = (categoryValue: string): string => {
    const customCategory = customCategories.value.find(c => c.value === categoryValue)
    if (customCategory) {
      return customCategory.value
    }
    // Fallback: handle singular "tool" -> plural "tools"
    const normalizedCategory = categoryValue === 'tool' ? 'tools' : categoryValue
    return t(`gear.item.categories.${normalizedCategory}`, categoryValue)
  }

  const categoryLabel = computed<string | undefined>(() => {
    if (!categoryValue) return undefined
    return getCategoryLabel(toRef(categoryValue).value)
  })

  return {
    categoryLabel,
    getCategoryLabel,
  }
}
