<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ComboBox from '@/components/ui/combo-box/ComboBox.vue'
import { cn } from '@/lib/utils'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import { getBrandOptions } from '@/modules/gear/utils/suggestedValues'
import type { HTMLAttributes } from 'vue'

const { t } = useI18n()
const { customBrands } = useGearSettings()

const modelValue = defineModel<string>('value', { default: '' })

const { placeholder = '', class: className } = defineProps<{
  placeholder?: string
  createLabel?: string
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <ComboBox
    v-model:value="modelValue"
    :options="getBrandOptions(customBrands)"
    :placeholder
    :create-label="createLabel ?? t('gear.comboBox.add')"
    :class="cn('w-full', className)"
    creatable
    clearable
  />
</template>
