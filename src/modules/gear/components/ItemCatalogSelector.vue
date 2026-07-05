<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import ComboBox from '@/components/ui/combo-box/ComboBox.vue'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import { useItemCatalogV2 } from '../composables/useItemCatalogV2'
import CategoryIcon from './CategoryIcon.vue'
import type { ComboBoxOption } from '@/components/ui/combo-box/ComboBox.vue'
import type { TUUID } from '@/shared/types/base.type'

const props = withDefaults(defineProps<{
  containerId: TUUID
  modelValue?: string
}>(), {
  modelValue: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'select': [item: IItemWithContainer]
}>()

const { t } = useI18n()

// Get all items excluding items from current container
const { catalogItems } = useItemCatalogV2(() => props.containerId)

// Convert items to ComboBox options
const options = computed<ComboBoxOption<IItemWithContainer>[]>(() => {
  return catalogItems.value.map(item => ({
    value: item.id,
    label: item.name,
    data: item,
  }))
})

const selectedValue = computed({
  get: () => props.modelValue,
  set: (value: string) => {
    emit('update:modelValue', value)
    const selectedItem = catalogItems.value.find(item => item.id === value)
    if (selectedItem) {
      emit('select', selectedItem)
    }
  },
})
</script>

<template>
  <ComboBox
    v-model:value="selectedValue"
    :options="options"
    :placeholder="t('gear.item.catalog.selectItem')"
    :search-placeholder="t('gear.item.catalog.searchItems')"
    :empty-message="t('gear.item.catalog.noItemsFound')"
    popover-content-class="w-[400px]"
  >
    <template #option-content="{ option }">
      <div class="flex items-center justify-between gap-2 w-full">
        <div class="flex items-center gap-2 min-w-0 flex-1">
          <CategoryIcon
            :category="(option as ComboBoxOption<IItemWithContainer>).data!.category"
            :size="16"
            class="shrink-0"
          />
          <span class="truncate">{{ option.label }}</span>
        </div>
        <Badge
          variant="secondary"
          class="shrink-0"
        >
          {{ (option as ComboBoxOption<IItemWithContainer>).data!.containerName }}
        </Badge>
      </div>
    </template>
  </ComboBox>
</template>

