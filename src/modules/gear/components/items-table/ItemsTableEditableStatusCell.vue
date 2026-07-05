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
import { DEFAULT_ITEM_STATUS } from '../../utils/constants'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearItemStatus } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto]
}>()

// In edit mode, always show select
const editedStatus = ref<TGearItemStatus>(props.item.status ?? DEFAULT_ITEM_STATUS)

const statuses: TGearItemStatus[] = ['owned', 'missing', 'toBuy']

// Handle status change
function handleStatusChange(newStatus: unknown) {
  if (newStatus === props.item.status) {
    emit('change', {})
    return
  }

  emit('change', { status: newStatus as TGearItemStatus })
}

// Watch for external changes to item
watch(
  () => props.item.status,
  (newStatus) => {
    editedStatus.value = newStatus ?? DEFAULT_ITEM_STATUS
  },
)
</script>

<template>
  <Select
    :model-value="editedStatus"
    @update:model-value="handleStatusChange"
  >
    <SelectTrigger
      :aria-label="t('gear.item.status')"
      class="h-[2.1rem]! min-w-[120px] border-transparent"
    >
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="status in statuses"
        :key="status"
        :value="status"
      >
        {{ t(`gear.item.statuses.${status}`) }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>

