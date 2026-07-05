<script setup lang="ts">
import { READINESS_EXCELLENT_THRESHOLD, READINESS_GOOD_THRESHOLD } from '../utils/constants'

defineProps<{
  readinessPercentage: number
}>()
</script>

<template>
  <div class="w-full bg-muted rounded-full h-2">
    <div
      :class="[
        'h-2 rounded-full transition-all',
        readinessPercentage >= READINESS_EXCELLENT_THRESHOLD ? 'bg-green-600' : readinessPercentage >= READINESS_GOOD_THRESHOLD ? 'bg-yellow-600' : 'bg-red-600',
      ]"
      :style="{ width: `${readinessPercentage}%` }"
    />
  </div>
</template>
