<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatWeightToPreferredUnit, formatWeightWithPreferredUnit } from '@/modules/gear/utils/formatWeight'
import { DEFAULT_ITEM_QUANTITY, DEFAULT_ITEM_WEIGHT } from '../../utils/constants'
import type { IGearItemV2, TGearWeightUnit } from '@/modules/gear/types/gear.types.v2'

const { item, isNestedContainer, totalWeight, preferredWeightUnit } = defineProps<{
  item: IGearItemV2
  isNestedContainer: boolean
  totalWeight?: number
  preferredWeightUnit: TGearWeightUnit
}>()

const { locale } = useI18n()

const formattedWeight = computed<string>(() => {
  if (isNestedContainer && totalWeight !== undefined) {
    return formatWeightToPreferredUnit(totalWeight * (item.quantity ?? DEFAULT_ITEM_QUANTITY), preferredWeightUnit, locale.value)
  }
  return formatWeightWithPreferredUnit(
    (item.weight ?? DEFAULT_ITEM_WEIGHT) * (item.quantity ?? DEFAULT_ITEM_QUANTITY),
    item.weightUnit ?? 'g',
    preferredWeightUnit,
    locale.value,
  )
})
</script>

<template>
  <div class="text-end px-4">
    {{ formattedWeight }}
  </div>
</template>
