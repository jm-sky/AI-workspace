<!--
  AI Cost Display Component
  Displays token usage and cost information
-->
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { IAiCost, IAiTokenUsage } from '../types'

const { t } = useI18n()

const { tokens, cost, class: className, precision = 4 } = defineProps<{
  tokens?: IAiTokenUsage
  cost?: IAiCost
  class?: string
  precision?: number
}>()
</script>

<template>
  <div v-if="tokens || cost" :class="className" class="flex flex-col gap-1 text-xs text-muted-foreground">
    <div v-if="tokens" class="flex items-center gap-3">
      <span class="min-w-10">{{ t('ai.cost.tokens') }}</span>
      <span class="min-w-12 text-end">{{ tokens.total.toLocaleString() }}</span>
      <span class="text-muted-foreground/70">
        ({{ tokens.input.toLocaleString() }} {{ t('ai.cost.in') }} / {{ tokens.output.toLocaleString() }} {{ t('ai.cost.out') }})
      </span>
    </div>
    <div v-if="cost" class="flex items-center gap-3">
      <span class="min-w-10">{{ t('ai.cost.cost') }}</span>
      <span class="min-w-12 text-end">${{ cost.total.toFixed(precision) }}</span>
      <span class="text-muted-foreground/70">
        (${{ cost.input.toFixed(precision) }} {{ t('ai.cost.in') }} / ${{ cost.output.toFixed(precision) }} {{ t('ai.cost.out') }})
      </span>
    </div>
  </div>
</template>

