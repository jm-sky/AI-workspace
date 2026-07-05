<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import {
  READINESS_EXCELLENT_THRESHOLD,
  READINESS_GOOD_THRESHOLD,
} from '../utils/constants'
import {
  calculateReadinessPercentageSyncV2,
  calculateTotalPriceSyncV2,
  calculateTotalWeightSyncV2,
  calculateWeightLimitPercentageSyncV2,
} from '../utils/containerCalculationsV2'
import { formatCurrency } from '../utils/currencyFormatter'
import { convertToGrams, formatWeightToPreferredUnit } from '../utils/formatWeight'

const props = defineProps<{
  container: IGearItemV2
  showTotalPrice?: boolean
}>()

const { t, locale } = useI18n()
const store = useGearStoreV2()
const { settings: gearSettings, defaultCurrency } = useGearSettings()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

const totalWeight = computed<number>(() => calculateTotalWeightSyncV2(props.container.id, store.getItemById, store.getChildrenOfItem))
const readinessPercentage = computed<number>(() => calculateReadinessPercentageSyncV2(props.container.id, store.getItemById, store.getChildrenOfItem))
const itemsCount = computed<number>(() => {
  const children = store.getChildrenOfItem(props.container.id)
  return children.filter(child => child.itemType === 'item').length
})
const totalPriceByCurrency = computed<Record<string, number>>(() => calculateTotalPriceSyncV2(props.container.id, store.getItemById, store.getChildrenOfItem, defaultCurrency.value))

// Format weight (totalWeight is in grams)
const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit, locale.value))

// Readiness color
const readinessColor = computed<string>(() => {
  if (readinessPercentage.value >= READINESS_EXCELLENT_THRESHOLD) return 'text-green-600'
  if (readinessPercentage.value >= READINESS_GOOD_THRESHOLD) return 'text-yellow-600'
  return 'text-red-600'
})

// Weight limit
const weightLimitPercentage = computed<number | null>(() => {
  return calculateWeightLimitPercentageSyncV2(props.container.id, store.getItemById, store.getChildrenOfItem)
})

const hasWeightLimit = computed<boolean>(() => weightLimitPercentage.value !== null)
const weightLimitColor = computed<string>(() => {
  if (!weightLimitPercentage.value) return ''
  if (weightLimitPercentage.value >= 100) return 'text-red-600'
  if (weightLimitPercentage.value >= 90) return 'text-orange-600'
  if (weightLimitPercentage.value >= 70) return 'text-yellow-600'
  return 'text-green-600'
})

const formattedMaxWeight = computed<string>(() => {
  if (!props.container.maxWeight || !props.container.maxWeightUnit) return ''
  return formatWeightToPreferredUnit(
    convertToGrams(props.container.maxWeight, props.container.maxWeightUnit),
    settings.value.preferredWeightUnit,
    locale.value
  )
})
</script>

<template>
  <div class="grid grid-cols-1 gap-4" :class="showTotalPrice ? 'md:grid-cols-4' : 'md:grid-cols-3'">
    <!-- Items Count -->
    <div class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-1">
        {{ t('gear.container.itemsCountLabel') }}
      </div>
      <div class="text-2xl font-bold">
        {{ itemsCount }}
      </div>
    </div>

    <!-- Total Weight -->
    <div class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-1">
        {{ t('gear.container.totalWeight') }}
      </div>
      <div :class="['text-2xl font-bold', hasWeightLimit ? weightLimitColor : '']">
        {{ formattedWeight }}
        <span v-if="hasWeightLimit" class="text-sm text-muted-foreground">
          / {{ formattedMaxWeight }}
        </span>
      </div>
      <div v-if="hasWeightLimit && weightLimitPercentage !== null" class="w-full bg-muted rounded-full h-2 mt-2">
        <div
          :class="[
            'h-2 rounded-full transition-all',
            weightLimitPercentage >= 100 ? 'bg-red-600' : weightLimitPercentage >= 90 ? 'bg-orange-600' : weightLimitPercentage >= 70 ? 'bg-yellow-600' : 'bg-green-600',
          ]"
          :style="{ width: `${Math.min(weightLimitPercentage, 100)}%` }"
        />
      </div>
    </div>

    <!-- Readiness -->
    <div class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-1">
        {{ t('gear.container.readiness') }}
      </div>
      <div :class="['text-2xl font-bold', readinessColor]">
        {{ readinessPercentage }}%
      </div>
      <div class="w-full bg-muted rounded-full h-2 mt-2">
        <div
          :class="[
            'h-2 rounded-full transition-all',
            readinessPercentage >= READINESS_EXCELLENT_THRESHOLD ? 'bg-green-600' : readinessPercentage >= READINESS_GOOD_THRESHOLD ? 'bg-yellow-600' : 'bg-red-600',
          ]"
          :style="{ width: `${readinessPercentage}%` }"
        />
      </div>
    </div>

    <!-- Total Price (if any items have prices) -->
    <div v-if="showTotalPrice && Object.keys(totalPriceByCurrency).length > 0" class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('gear.item.totalPrice') }}
      </div>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(amount, currency) in totalPriceByCurrency"
          :key="currency"
          class="text-lg font-bold text-nowrap border rounded-md px-3 py-1"
        >
          {{ formatCurrency(amount, currency) }}
        </div>
      </div>
    </div>
  </div>
</template>

