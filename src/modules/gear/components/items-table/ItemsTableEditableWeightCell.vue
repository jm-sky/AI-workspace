<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DEFAULT_ITEM_WEIGHT } from '../../utils/constants'
import { WEIGHT_UNITS } from '../../utils/weightUnits'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearWeightUnit } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto]
}>()

// In edit mode, always show input
const editedWeight = ref((props.item.weight ?? DEFAULT_ITEM_WEIGHT).toString())
const editedWeightUnit = ref<TGearWeightUnit>(props.item.weightUnit ?? 'g')

// Handle change - emit updates to parent
function handleChange() {
  const weightValue = parseFloat(editedWeight.value)

  // Validation - weight must be >= 0
  if (isNaN(weightValue) || weightValue < 0) {
    editedWeight.value = (props.item.weight ?? DEFAULT_ITEM_WEIGHT).toString()
    editedWeightUnit.value = props.item.weightUnit ?? 'g'
    emit('change', {})
    return
  }

  if (weightValue !== props.item.weight || editedWeightUnit.value !== (props.item.weightUnit ?? 'g')) {
    emit('change', {
      weight: weightValue,
      weightUnit: editedWeightUnit.value,
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
  () => [props.item.weight, props.item.weightUnit],
  ([newWeight, newUnit]) => {
    editedWeight.value = newWeight?.toString() ?? ''
    editedWeightUnit.value = (newUnit ?? 'g') as TGearWeightUnit
  },
)
</script>

<template>
  <div class="flex items-center gap-2">
    <Input
      :id="`item-weight-${item.id}`"
      v-model="editedWeight"
      :name="`item-weight-${item.id}`"
      type="number"
      min="0"
      step="0.01"
      :aria-label="t('gear.item.weight')"
      class="py-1! h-[2.1rem]! w-20 border-0"
      @keyup.enter="handleEnter"
      @blur="handleChange"
    />
    <Select
      v-model="editedWeightUnit"
      @update:model-value="handleChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.weightUnit')"
        class="w-[70px] h-[2.1rem]! border-transparent"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="unit in WEIGHT_UNITS"
          :key="unit"
          :value="unit"
        >
          {{ t(`gear.item.weightUnits.${unit}`) }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>

