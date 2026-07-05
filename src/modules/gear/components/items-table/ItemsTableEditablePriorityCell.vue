<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DEFAULT_ITEM_PRIORITY } from '../../utils/constants'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearItemPriority } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto]
}>()

// In edit mode, always show select
const editedPriority = ref<TGearItemPriority>(props.item.priority ?? DEFAULT_ITEM_PRIORITY)

const priorities: TGearItemPriority[] = ['critical', 'high', 'medium', 'low']

// Handle priority change
function handlePriorityChange(newPriority: unknown) {
  if (newPriority === props.item.priority) {
    emit('change', {})
    return
  }

  emit('change', { priority: newPriority as TGearItemPriority })
}

// Watch for external changes to item
watch(
  () => props.item.priority,
  (newPriority) => {
    editedPriority.value = newPriority ?? DEFAULT_ITEM_PRIORITY
  },
)
</script>

<template>
  <Select
    :model-value="editedPriority"
    @update:model-value="handlePriorityChange"
  >
    <SelectTrigger
      :aria-label="t('gear.item.priority')"
      class="h-[2.1rem]! min-w-[120px] border-transparent"
    >
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="priority in priorities"
        :key="priority"
        :value="priority"
      >
        {{ t(`gear.item.priorities.${priority}`) }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>

