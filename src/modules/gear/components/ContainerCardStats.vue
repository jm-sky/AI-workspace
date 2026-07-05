<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps<{
  itemsCount: number
  formattedWeight: string
  readinessPercentage: number
  readinessColor: string
}>()
</script>

<template>
  <div class="grid grid-cols-3 gap-2 sm:gap-4 text-sm">
    <div>
      <div class="text-muted-foreground">
        {{ t('gear.container.itemsCountLabel') }}
      </div>
      <div class="font-semibold">
        {{ itemsCount }}
      </div>
    </div>
    <div>
      <div class="text-muted-foreground">
        {{ t('gear.container.totalWeight') }}
      </div>
      <div class="font-semibold">
        {{ formattedWeight }}
      </div>
    </div>
    <div>
      <div class="text-muted-foreground">
        {{ t('gear.container.readiness') }}
      </div>
      <div :class="['font-semibold', readinessColor]">
        {{ readinessPercentage }}%
      </div>
    </div>
  </div>
</template>
