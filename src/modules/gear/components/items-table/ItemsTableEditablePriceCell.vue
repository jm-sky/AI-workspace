<script setup lang="ts">
import { XIcon } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useGearSettings } from '../../composables/useGearSettings'
import { SUPPORTED_CURRENCIES } from '../../utils/currencyFormatter'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()
const { defaultCurrency } = useGearSettings()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto]
}>()

// In edit mode, always show input
const editedPrice = ref(props.item.price?.toString() ?? '')
const editedCurrency = ref<string>(props.item.currency ?? defaultCurrency.value)

// Handle change - emit updates to parent
function handleChange() {
  const priceValue = editedPrice.value.trim() === '' ? null : parseFloat(editedPrice.value)
  
  // Validation - price must be >= 0 if provided
  if (priceValue !== null && (isNaN(priceValue) || priceValue < 0)) {
    editedPrice.value = props.item.price?.toString() ?? ''
    editedCurrency.value = props.item.currency ?? defaultCurrency.value
    emit('change', {})
    return
  }

  const originalPrice = props.item.price ?? null
  const originalCurrency = props.item.currency ?? defaultCurrency.value

  if (priceValue !== originalPrice || editedCurrency.value !== originalCurrency) {
    emit('change', {
      price: priceValue,
      currency: editedCurrency.value,
    })
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
  () => [props.item.price, props.item.currency],
  ([newPrice, newCurrency]) => {
    editedPrice.value = newPrice?.toString() ?? ''
    editedCurrency.value = (newCurrency ?? defaultCurrency.value) as string
  },
)

// Reset value
function handleReset() {
  editedPrice.value = props.item.price?.toString() ?? ''
  editedCurrency.value = props.item.currency ?? defaultCurrency.value
  emit('change', {})
}

const hasChanges = computed(() => {
  const priceValue = editedPrice.value.trim() === '' ? null : parseFloat(editedPrice.value)
  const originalPrice = props.item.price ?? null
  const originalCurrency = props.item.currency ?? defaultCurrency.value
  
  return (
    priceValue !== originalPrice ||
    editedCurrency.value !== originalCurrency
  )
})
</script>

<template>
  <div class="flex items-center gap-2">
    <div class="relative flex-1">
      <Input
        :id="`item-price-${item.id}`"
        v-model="editedPrice"
        :name="`item-price-${item.id}`"
        type="number"
        min="0"
        step="0.01"
        :aria-label="t('gear.item.price')"
        :placeholder="t('gear.item.price')"
        class="pr-8 py-1! h-[2.1rem]! border-0"
        @keyup.enter="handleEnter"
        @blur="handleChange"
      />
      <!-- Reset button -->
      <button
        v-if="hasChanges"
        type="button"
        class="absolute right-2 top-0 bottom-0 my-auto p-0"
        @click.stop.prevent="handleReset"
      >
        <XIcon class="size-4" />
      </button>
    </div>
    <Select
      v-model="editedCurrency"
      @update:model-value="handleChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.currency')"
        class="w-[100px] h-[2.1rem]! border-transparent"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="curr in SUPPORTED_CURRENCIES"
          :key="curr.value"
          :value="curr.value"
        >
          {{ curr.label }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
