<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ComboBox from '@/components/ui/combo-box/ComboBox.vue'
import { getColorOptions } from '@/modules/gear/utils/suggestedValues'

const { t } = useI18n()
const modelValue = defineModel<string>('value', { default: '' })
</script>

<template>
  <ComboBox
    v-model:value="modelValue"
    :options="getColorOptions()"
    :placeholder="''"
    :create-label="t('gear.comboBox.add')"
    class="w-full"
    clearable
    creatable
  >
    <template #value>
      <div class="flex items-center gap-2">
        <div class="size-4 rounded-full" :style="{ backgroundColor: modelValue as string }" />
        <span>{{ modelValue }}</span>
      </div>
    </template>
    <template #option-content="{ option }">
      <div class="flex items-center gap-2">
        <div class="size-4 rounded-full" :style="{ backgroundColor: option.data as string }" />
        <span>{{ option.label }}</span>
      </div>
    </template>
  </ComboBox>
</template>
