import { computed, type Reactive, type Ref, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGearSettings } from './useGearSettings'

export const useContainerTypeLabel = (typeValue?: Ref<string> | Reactive<string> | string) => {
  const { t } = useI18n()
  const { customContainerTypes } = useGearSettings()

  const getContainerTypeLabel = (typeValue: string): string => {
    const customType = customContainerTypes.value.find(t => t.value === typeValue)
    if (customType) {
      return customType.value
    }
    return t(`gear.container.types.${typeValue}`)
  }

  const typeLabel = computed<string | undefined>(() => {
    if (!typeValue) return undefined
    return getContainerTypeLabel(toRef(typeValue).value)
  })

  return {
    getContainerTypeLabel,
    typeLabel,
  }
}
