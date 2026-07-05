<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useGearSettings } from '../composables/useGearSettings'
import { formatCurrency } from '../utils/currencyFormatter'
import type { ChartConfig } from '@/components/ui/chart'

interface CategoryData {
  category: string
  weight: number
  quantity: number
  price?: number
  priority?: string
  percentage: number
  value: number
}

interface Props {
  categoryData: CategoryData[]
  chartConfig: ChartConfig
  chartMode: 'weight' | 'quantity' | 'price' | 'priority' | 'weight-breakdown'
  totalValue: number
}

defineProps<Props>()

const { t } = useI18n()
const { defaultCurrency } = useGearSettings()
</script>

<template>
  <div class="flex-1 space-y-2">
    <div class="text-sm font-medium">
      {{ t('gear.chart.legend', 'Legenda') }}
    </div>
    <div class="space-y-2">
      <div
        v-for="data in categoryData"
        :key="data.category"
        class="flex items-center justify-between gap-4 p-2 rounded hover:bg-muted transition-colors"
      >
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <div
            class="size-4 rounded shrink-0"
            :style="{
              backgroundColor: chartConfig[data.category]?.color || 'transparent',
            }"
          />
          <span class="text-sm font-medium truncate">
            <template v-if="chartMode === 'priority' && data.priority">
              {{ t(`gear.item.priorities.${data.priority}`, data.priority) }}
            </template>
            <template v-else-if="chartMode === 'weight-breakdown'">
              {{ t(`gear.weightBreakdown.${data.category}`, data.category) }}
            </template>
            <template v-else>
              {{ t(`gear.item.categories.${data.category}`, data.category) }}
            </template>
          </span>
        </div>
        <div class="text-sm text-muted-foreground shrink-0">
          <span class="font-semibold">{{ data.percentage.toFixed(1) }}%</span>
          <span class="ml-2">
            <template v-if="chartMode === 'weight' || chartMode === 'weight-breakdown'">
              ({{ data.weight.toFixed(2) }} g)
            </template>
            <template v-else-if="chartMode === 'price' && data.price != null">
              ({{ formatCurrency(data.price, defaultCurrency) }})
            </template>
            <template v-else>
              ({{ data.quantity }})
            </template>
          </span>
        </div>
      </div>
    </div>
    <div class="pt-4 px-2 border-t text-sm text-muted-foreground">
      <div class="flex flex-row items-center justify-between gap-2">
        {{ t('gear.chart.total', 'Łącznie') }}:
        <span class="font-semibold">
          <template v-if="chartMode === 'weight' || chartMode === 'weight-breakdown'">
            {{ totalValue.toFixed(2) }} g
          </template>
          <template v-else-if="chartMode === 'price'">
            {{ formatCurrency(totalValue, defaultCurrency) }}
          </template>
          <template v-else>
            {{ totalValue }}
          </template>
        </span>
      </div>
    </div>
  </div>
</template>

