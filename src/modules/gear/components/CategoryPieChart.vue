<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
} from '@/components/ui/chart'
import type { TGearItemPriority } from '../types/gear.types'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearSettings } from '../composables/useGearSettings'
import { usePieChartGeometry } from '../composables/usePieChartGeometry'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { calculateItemsByPriorityV2, calculatePriceByCategoryV2, calculateWeightBreakdownV2 } from '../utils/containerCalculationsV2'
import { formatCurrency, getCurrency } from '../utils/currencyFormatter'
import CategoryPieChartLabels from './CategoryPieChartLabels.vue'
import CategoryPieChartLegend from './CategoryPieChartLegend.vue'
import type { ChartConfig } from '@/components/ui/chart'

// Lazy load unovis components
const VisDonut = defineAsyncComponent(() => import('@unovis/vue').then(m => m.VisDonut))
const VisSingleContainer = defineAsyncComponent(() => import('@unovis/vue').then(m => m.VisSingleContainer))

type ChartMode = 'weight' | 'quantity' | 'price' | 'priority' | 'weight-breakdown'

interface CategoryData {
  category: string
  weight: number
  quantity: number
  price?: number
  priority?: TGearItemPriority
  percentage: number
  value: number // The value to display in the chart
}

const props = withDefaults(defineProps<{
  container: IGearItemV2
  includeNested?: boolean
}>(), {
  includeNested: false,
})

const { t } = useI18n()
const store = useGearStoreV2()
const { defaultCurrency } = useGearSettings()

const chartMode = ref<ChartMode>('weight')

const categoryData = computed<CategoryData[]>(() => {
  // Get all items including nested containers if enabled
  let allItems: IGearItemV2[] = store.getChildrenOfItem(props.container.id)
    .filter(child => child.itemType === 'item')

  if (props.includeNested) {
    // Get all nested containers recursively
    const collectNestedItems = (containerId: string): IGearItemV2[] => {
      const children = store.getChildrenOfItem(containerId)
      let items: IGearItemV2[] = []

      for (const child of children) {
        if (child.itemType === 'item') {
          items.push(child)
        } else if (child.itemType === 'container') {
          // Recursively collect items from nested containers
          items = items.concat(collectNestedItems(child.id))
        }
      }

      return items
    }

    allItems = collectNestedItems(props.container.id)
  }

  const mode = chartMode.value

  // Handle weight-breakdown mode
  if (mode === 'weight-breakdown') {
    const breakdown = calculateWeightBreakdownV2(props.container.id, store.getItemById, store.getChildrenOfItem)
    const total = breakdown.total

    const breakdownData: CategoryData[] = [
      {
        category: 'base',
        weight: breakdown.base,
        quantity: 0,
        percentage: total > 0 ? (breakdown.base / total) * 100 : 0,
        value: breakdown.base,
      },
      {
        category: 'worn',
        weight: breakdown.worn,
        quantity: 0,
        percentage: total > 0 ? (breakdown.worn / total) * 100 : 0,
        value: breakdown.worn,
      },
      {
        category: 'consumable',
        weight: breakdown.consumable,
        quantity: 0,
        percentage: total > 0 ? (breakdown.consumable / total) * 100 : 0,
        value: breakdown.consumable,
      },
    ]

    // Filter out categories with weight = 0
    return breakdownData.filter(item => item.weight > 0)
  }

  // Handle price mode
  // Note: V2 function already recurses into nested containers, so includeNested prop is not needed
  if (mode === 'price') {
    const priceData = calculatePriceByCategoryV2(props.container.id, store.getItemById, store.getChildrenOfItem)
    return priceData.map(({ category, totalPrice, percentage }) => ({
      category,
      weight: 0,
      quantity: 0,
      price: totalPrice,
      percentage,
      value: totalPrice,
    }))
  }

  // Handle priority mode
  // Note: V2 function already recurses into nested containers, so includeNested prop is not needed
  if (mode === 'priority') {
    const priorityData = calculateItemsByPriorityV2(props.container.id, store.getItemById, store.getChildrenOfItem)
    return priorityData.map(({ priority, count, percentage }) => ({
      category: priority, // Use priority as category key for chart
      weight: 0,
      quantity: count,
      priority,
      percentage,
      value: count,
    }))
  }

  // Handle weight and quantity modes (existing logic)
  const categoryMap = new Map<string, { weight: number; quantity: number }>()

  // Calculate totals
  let totalWeight = 0
  let totalQuantity = 0

  for (const item of allItems) {
    const itemWeight = (item.weight ?? 0) * (item.quantity ?? 1)
    totalWeight += itemWeight
    totalQuantity += (item.quantity ?? 1)

    const category = item.category || 'other'
    const existing = categoryMap.get(category) || { weight: 0, quantity: 0 }
    categoryMap.set(category, {
      weight: existing.weight + itemWeight,
      quantity: existing.quantity + (item.quantity ?? 1),
    })
  }

  // Convert to array and calculate percentages
  const data: CategoryData[] = Array.from(categoryMap.entries()).map(([category, values]) => {
    const value = mode === 'weight' ? values.weight : values.quantity
    const total = mode === 'weight' ? totalWeight : totalQuantity
    const percentage = total > 0 ? (value / total) * 100 : 0

    return {
      category,
      weight: values.weight,
      quantity: values.quantity,
      percentage,
      value,
    }
  })

  // Sort by percentage descending
  return data.sort((a, b) => b.percentage - a.percentage)
})

const totalValue = computed(() => {
  const mode = chartMode.value
  if (mode === 'weight' || mode === 'weight-breakdown') {
    return categoryData.value.reduce((sum, item) => sum + item.weight, 0)
  }
  if (mode === 'price') {
    return categoryData.value.reduce((sum, item) => sum + (item.price || 0), 0)
  }
  if (mode === 'priority') {
    return categoryData.value.reduce((sum, item) => sum + item.quantity, 0)
  }
  return categoryData.value.reduce((sum, item) => sum + item.quantity, 0)
})

// Build chart config from category data
const chartConfig = computed<ChartConfig>(() => {
  const config: ChartConfig = {}
  const mode = chartMode.value

  // Priority colors (for priority mode)
  const priorityColors: Record<TGearItemPriority, string> = {
    critical: '#ef4444', // red
    high: '#f97316', // orange
    medium: '#eab308', // yellow
    low: '#22c55e', // green
  }

  // Category colors (for weight/quantity/price modes)
  const categoryColors = [
    'var(--chart-1)',
    'var(--chart-2)',
    'var(--chart-3)',
    'var(--chart-4)',
    'var(--chart-5)',
    'var(--primary)',
    'var(--secondary)',
    'var(--accent)',
  ]

  categoryData.value.forEach((data, index) => {
    if (mode === 'priority' && data.priority) {
      // Use priority colors for priority mode
      config[data.category] = {
        label: t(`gear.item.priorities.${data.priority}`, data.priority),
        color: priorityColors[data.priority],
      }
    } else if (mode === 'weight-breakdown') {
      // Use fixed colors for weight-breakdown mode
      const weightBreakdownColors: Record<string, string> = {
        base: '#94a3b8', // slate-400 - lighter gray for base weight
        worn: '#3b82f6', // blue-500
        consumable: '#22c55e', // green-500
      }
      config[data.category] = {
        label: t(`gear.weightBreakdown.${data.category}`, data.category),
        color: weightBreakdownColors[data.category] ?? 'var(--muted-foreground)',
      }
    } else {
      // Use category colors for other modes
      config[data.category] = {
        label: t(`gear.item.categories.${data.category}`, data.category),
        color: categoryColors[index % categoryColors.length] ?? 'var(--muted-foreground)',
      }
    }
  })

  return config
})

// Use composable for chart geometry calculations
const { chartGeometry, calculateLabelPositions } = usePieChartGeometry({
  svgWidth: 430,
  svgHeight: 300,
  margin: 30,
  arcWidth: 60, // Must match :arc-width in VisDonut
  padAngle: 0.02, // Must match :pad-angle in VisDonut
  labelDistance: 50, // Distance from arc middle to label (increase to move labels further out)
})

// Prepare data for VisDonut
// Format: { [category]: value } to match chartConfig keys for tooltip
// Also calculate label positions for percentage labels
const chartData = computed(() => {
  const mode = chartMode.value
  const dataWithLabels = calculateLabelPositions(categoryData.value, mode)

  return dataWithLabels.map((data) => {
    let chartValue: number
    if (mode === 'weight' || mode === 'weight-breakdown') {
      chartValue = data.weight
    } else if (mode === 'price') {
      chartValue = (data.price ?? 0) as number
    } else {
      chartValue = data.quantity
    }

    return {
      [data.category]: chartValue,
      category: data.category,
      value: data.value,
      percentage: data.percentage,
      weight: data.weight,
      quantity: data.quantity,
      price: data.price,
      priority: data.priority,
      labelX: data.labelX,
      labelY: data.labelY,
    }
  })
})

type Data = typeof chartData.value[number]

const hasData = computed<boolean>(() => categoryData.value.length > 0 && totalValue.value > 0)

// Lazy load Donut selector
const donutSelectors = ref<typeof import('@unovis/ts').Donut.selectors | null>(null)

onMounted(async () => {
  try {
    const { Donut } = await import('@unovis/ts')
    donutSelectors.value = Donut.selectors
  } catch (error) {
    console.error('Failed to load @unovis/ts:', error)
  }
})

const chartTooltipTriggers = computed(() => {
  if (!donutSelectors.value) {
    return {}
  }
  const config = chartConfig.value as ChartConfig
  const mode = chartMode.value
  return {
    [donutSelectors.value.segment]: (d: Data & { data?: Data }) => {
      // Unovis passes {data: Data, index, value, ...} structure
      const data = (d.data || d) as Data
      const template = componentToString(config, ChartTooltipContent, {
        hideLabel: true,
        valueFormatter,
      })
      if (!template) return ''
      // Pass raw numeric value - ChartTooltipContent will format it
      // The key must match the category in chartConfig for proper label translation
      let rawValue: number
      if (mode === 'weight' || mode === 'weight-breakdown') {
        rawValue = data.weight ?? 0
      } else if (mode === 'price') {
        rawValue = (data.price ?? 0) as number
      } else {
        rawValue = data.quantity ?? 0
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const payload: Record<string, any> = {
        [data.category]: rawValue,
      }
      return template(payload, data.value)
    },
  }
})

const valueFormatter = (value: number) => {
  const mode = chartMode.value
  if (mode === 'weight' || mode === 'weight-breakdown') {
    return `${value.toFixed(2)} g`
  }
  if (mode === 'price') {
    // Use first item's currency or default currency
    const children = store.getChildrenOfItem(props.container.id)
    const firstItem = children
      .filter(child => child.itemType === 'item')
      .find(item => item.price != null && item.price > 0)
    const currency = firstItem?.currency ? getCurrency(firstItem.currency, defaultCurrency.value) : defaultCurrency.value
    return formatCurrency(value, currency)
  }
  if (mode === 'priority') {
    return `${value.toLocaleString()} ${t('gear.item.units.piece', 'szt.')}`
  }
  return `${value.toLocaleString()} ${t('gear.item.units.piece', 'szt.')}`
}
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex flex-col md:flex-row gap-2 items-center justify-between">
        <div>
          <CardTitle>
            {{ t('gear.chart.title', 'Rozkład kategorii') }}
          </CardTitle>
          <CardDescription>
            {{ t('gear.chart.description', 'Wizualizacja kategorii przedmiotów w kontenerze') }}
          </CardDescription>
        </div>
        <div class="flex flex-wrap w-full justify-end gap-2">
          <Button
            :variant="chartMode === 'weight' ? 'default' : 'outline'"
            size="sm"
            @click="chartMode = 'weight'"
          >
            {{ t('gear.chart.byWeight', 'Waga') }}
          </Button>
          <Button
            :variant="chartMode === 'quantity' ? 'default' : 'outline'"
            size="sm"
            @click="chartMode = 'quantity'"
          >
            {{ t('gear.chart.byQuantity', 'Ilość') }}
          </Button>
          <Button
            :variant="chartMode === 'price' ? 'default' : 'outline'"
            size="sm"
            @click="chartMode = 'price'"
          >
            {{ t('gear.chart.byPrice', 'Cena') }}
          </Button>
          <Button
            :variant="chartMode === 'priority' ? 'default' : 'outline'"
            size="sm"
            @click="chartMode = 'priority'"
          >
            {{ t('gear.chart.byPriority', 'Priorytet') }}
          </Button>
          <Button
            :variant="chartMode === 'weight-breakdown' ? 'default' : 'outline'"
            size="sm"
            @click="chartMode = 'weight-breakdown'"
          >
            {{ t('gear.chart.byWeightBreakdown', 'Podział wag') }}
          </Button>
        </div>
      </div>
    </CardHeader>
    <CardContent>
      <div v-if="!hasData" class="flex items-center justify-center py-12 text-muted-foreground">
        {{ t('gear.chart.noData', 'Brak danych do wyświetlenia') }}
      </div>
      <div v-else-if="!donutSelectors" class="flex items-center justify-center py-12 text-muted-foreground">
        {{ t('gear.chart.loading', 'Ładowanie wykresu...') }}
      </div>
      <div v-else class="flex flex-col md:flex-row gap-6">
        <!-- Pie Chart - Left side -->
        <div class="shrink-0 md:w-1/2 relative max-w-full overflow-hidden">
          <ChartContainer :config="chartConfig" class="mx-auto aspect-square max-h-[300px] w-full max-w-full">
            <Suspense>
              <template #default>
                <VisSingleContainer
                  :data="chartData"
                  :margin="{ top: 30, bottom: 30, left: 30, right: 30 }"
                >
                  <VisDonut
                    :value="(d: Data) => d.value"
                    :color="(d: Data) => chartConfig[d.category as keyof typeof chartConfig]?.color"
                    :arc-width="60"
                    :pad-angle="0.02"
                  />
                  <ChartTooltip :triggers="chartTooltipTriggers" />
                </VisSingleContainer>
              </template>
              <template #fallback>
                <div class="flex items-center justify-center py-12 text-muted-foreground">
                  {{ t('gear.chart.loading', 'Ładowanie wykresu...') }}
                </div>
              </template>
            </Suspense>
            <!-- Labels for segments with percentages - rendered outside VisSingleContainer -->
            <CategoryPieChartLabels
              v-if="donutSelectors"
              :chart-data
              :center-x="chartGeometry.centerX"
              :center-y="chartGeometry.centerY"
              :label-radius="chartGeometry.labelRadius"
            />
          </ChartContainer>
        </div>

        <!-- Legend - Right side -->
        <CategoryPieChartLegend
          :category-data="categoryData"
          :chart-config="chartConfig"
          :chart-mode="chartMode"
          :total-value="totalValue"
        />
      </div>
    </CardContent>
  </Card>
</template>
