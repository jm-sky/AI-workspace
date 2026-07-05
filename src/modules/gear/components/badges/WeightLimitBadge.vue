<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import type { IGearItemV2 } from '../../types/gear.types.v2'
import { useGearStoreV2 } from '../../store/useGearStoreV2'
import { calculateWeightLimitPercentageSyncV2 } from '../../utils/containerCalculationsV2'

const props = defineProps<{
  container: IGearItemV2
}>()

const { t } = useI18n()
const store = useGearStoreV2()

const weightLimitPercentage = computed<number | null>(() =>
  calculateWeightLimitPercentageSyncV2(props.container.id, store.getItemById, store.getChildrenOfItem)
)

const hasWeightLimit = computed<boolean>(() => weightLimitPercentage.value !== null)

const shouldShow = computed<boolean>(() =>
  hasWeightLimit.value && weightLimitPercentage.value !== null && weightLimitPercentage.value >= 90
)

const badgeClasses = computed<string>(() => {
  if (weightLimitPercentage.value === null) return ''
  return weightLimitPercentage.value >= 100
    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
})

const badgeText = computed<string>(() => {
  if (weightLimitPercentage.value === null) return ''
  const message = weightLimitPercentage.value >= 100
    ? t('gear.container.weightLimitExceeded')
    : t('gear.container.weightLimitWarning')
  return `${message} (${weightLimitPercentage.value}%)`
})
</script>

<template>
  <Badge
    v-if="shouldShow"
    :class="badgeClasses"
  >
    {{ badgeText }}
  </Badge>
</template>

