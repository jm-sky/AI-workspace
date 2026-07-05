<script setup lang="ts">
import { UndoIcon } from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Input } from '@/components/ui/input'
import { DEFAULT_ITEM_QUANTITY } from '../../utils/constants'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto]
}>()

// In edit mode, always show input
const editedQuantity = ref((props.item.quantity ?? DEFAULT_ITEM_QUANTITY).toString())

// Handle change - emit updates to parent
function handleChange() {
  const quantityValue = parseInt(editedQuantity.value, 10)

  // Validation - quantity must be >= 1
  if (isNaN(quantityValue) || quantityValue < 1) {
    editedQuantity.value = (props.item.quantity ?? DEFAULT_ITEM_QUANTITY).toString()
    emit('change', {})
    return
  }

  if (quantityValue !== props.item.quantity) {
    emit('change', { quantity: quantityValue })
  } else {
    emit('change', {})
  }
}

// Handle Enter - same as blur
function handleEnter() {
  handleChange()
}

// Watch for external changes to item
watch(
  () => props.item.quantity,
  (newQuantity) => {
    editedQuantity.value = (newQuantity ?? DEFAULT_ITEM_QUANTITY).toString()
  },
)

// Reset value
function handleReset() {
  editedQuantity.value = (props.item.quantity ?? DEFAULT_ITEM_QUANTITY).toString()
  emit('change', {})
}
</script>

<template>
  <div class="relative w-20">
    <Input
      :id="`item-quantity-${item.id}`"
      v-model="editedQuantity"
      :name="`item-quantity-${item.id}`"
      type="number"
      min="1"
      step="1"
      :aria-label="t('gear.item.quantity')"
      class="py-1! h-[2.1rem]! border-0"
      @keyup.enter="handleEnter"
      @blur="handleChange"
    />
    <!-- Reset button -->
    <button
      v-if="editedQuantity && parseInt(editedQuantity, 10) !== props.item.quantity"
      type="button"
      class="absolute right-8 top-0 bottom-0 my-auto p-0"
      @click.stop.prevent="handleReset"
    >
      <UndoIcon class="size-4" />
    </button>
  </div>
</template>

