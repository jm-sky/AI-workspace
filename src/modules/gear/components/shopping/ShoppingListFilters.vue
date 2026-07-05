<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import { onBeforeMount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { SHOPPING_PLANNING_PAGE_FILTERS_COLLAPSED_KEY } from '@/shared/config/config'
import type { TGearItemCategory } from '../../types/gear.types'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import CategoryIcon from '../CategoryIcon.vue'

const { t } = useI18n()

// Collapse state
const isCollapsed = ref(false)

// Load collapse state from localStorage
function loadCollapseState(): boolean {
  const stored = localStorage.getItem(SHOPPING_PLANNING_PAGE_FILTERS_COLLAPSED_KEY)
  if (stored !== null) {
    try {
      return JSON.parse(stored) as boolean
    } catch (error) {
      console.error('Error loading collapse state from storage:', error)
    }
  }
  return false // Default to expanded
}

// Save collapse state to localStorage
function saveCollapseState(collapsed: boolean): void {
  try {
    localStorage.setItem(SHOPPING_PLANNING_PAGE_FILTERS_COLLAPSED_KEY, JSON.stringify(collapsed))
  } catch (error) {
    console.error('Error saving collapse state to storage:', error)
  }
}

// Toggle collapse state
function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  saveCollapseState(isCollapsed.value)
}

// Load collapse state on mount
onBeforeMount(() => {
  isCollapsed.value = loadCollapseState()
})

const { allCategories, selectedCategories, budget, includeExpiringSoon, defaultCurrency } = defineProps<{
  allCategories: TGearItemCategory[]
  selectedCategories: TGearItemCategory[]
  budget: number | null
  includeExpiringSoon: boolean
  defaultCurrency: string
}>()

const emit = defineEmits<{
  'update:selectedCategories': [categories: TGearItemCategory[]]
  'update:budget': [budget: number | null]
  'update:includeExpiringSoon': [include: boolean]
}>()

const { getCategoryLabel } = useCategoryLabel()

// Category checkbox states - using reactive object for v-model compatibility
const categoryChecked = ref<Record<string, boolean>>({})

// Initialize categoryChecked from props
watch(
  () => allCategories,
  (categories) => {
    categories.forEach(category => {
      if (!(category in categoryChecked.value)) {
        categoryChecked.value[category] = selectedCategories.includes(category)
      }
    })
  },
  { immediate: true },
)

// Watch categoryChecked changes and emit
watch(
  categoryChecked,
  (checked) => {
    const newSelected: TGearItemCategory[] = []
    Object.entries(checked).forEach(([category, isChecked]) => {
      if (isChecked && allCategories.includes(category as TGearItemCategory)) {
        newSelected.push(category as TGearItemCategory)
      }
    })
    emit('update:selectedCategories', newSelected)
  },
  { deep: true },
)

// Watch selectedCategories changes from parent and sync to categoryChecked
watch(
  () => selectedCategories,
  (selected) => {
    allCategories.forEach(category => {
      categoryChecked.value[category] = selected.includes(category)
    })
  },
  { immediate: true },
)

const handleBudgetUpdate = (value: string | number) => {
  const stringValue = typeof value === 'number' ? value.toString() : value
  emit('update:budget', stringValue === '' ? null : Number(stringValue))
}

const handleClearBudget = () => {
  emit('update:budget', null)
}

const handleIncludeExpiringUpdate = (value: boolean | 'indeterminate') => {
  if (value === 'indeterminate') return
  emit('update:includeExpiringSoon', value)
}
</script>

<template>
  <div class="space-y-4 border rounded-lg bg-muted/50 transition-all" :class="isCollapsed ? 'py-1 px-4' : 'py-4 px-4'">
    <!-- Header with collapse button -->
    <div class="flex items-center justify-between">
      <h3 class="font-semibold text-base">
        {{ t('gear.shopping.filters', 'Filters') }}
      </h3>
      <Button
        variant="ghost"
        size="sm"
        :aria-label="isCollapsed ? t('gear.shopping.expandFilters', 'Expand filters') : t('gear.shopping.collapseFilters', 'Collapse filters')"
        @click="toggleCollapse"
      >
        <ChevronRight class="size-4 transition-transform" :class="isCollapsed ? 'rotate-90' : ''" />
      </Button>
    </div>

    <!-- Filter content (collapsible) -->
    <div v-if="!isCollapsed" class="space-y-4">
      <!-- Categories filter -->
      <div v-if="allCategories.length > 0" class="space-y-2">
        <p class="text-sm font-medium">
          {{ t('gear.shopping.filterByCategory', 'Filter by Category') }}:
        </p>
        <div class="flex flex-wrap gap-4">
          <div
            v-for="category in allCategories"
            :key="category"
            class="flex items-center gap-2"
          >
            <Checkbox
              :id="`category-${category}`"
              v-model="categoryChecked[category]"
            />
            <Label
              :for="`category-${category}`"
              class="text-sm cursor-pointer flex items-center gap-2"
            >
              <CategoryIcon :category="category" :size="14" />
              {{ getCategoryLabel(category) }}
            </Label>
          </div>
        </div>
      </div>

      <!-- Budget filter -->
      <div class="space-y-2">
        <Label
          for="shopping-budget-filter"
          class="text-sm"
        >
          {{ t('gear.shopping.filterByBudget', 'Filter by Budget') }}:
        </Label>
        <div class="flex items-center gap-2">
          <Input
            id="shopping-budget-filter"
            name="shopping-budget-filter"
            :model-value="budget?.toString() ?? ''"
            type="number"
            :placeholder="t('gear.shopping.budgetPlaceholder', 'Enter budget amount')"
            class="max-w-xs"
            min="0"
            step="0.01"
            @update:model-value="handleBudgetUpdate"
          />
          <span class="text-sm text-muted-foreground">{{ defaultCurrency }}</span>
          <Button
            v-if="budget !== null"
            variant="ghost"
            size="sm"
            @click="handleClearBudget"
          >
            {{ t('gear.shopping.clearBudget', 'Clear') }}
          </Button>
        </div>
      </div>

      <!-- Include expiring soon -->
      <div class="flex items-center gap-2">
        <Checkbox
          id="include-expiring"
          :model-value="includeExpiringSoon"
          @update:model-value="handleIncludeExpiringUpdate"
        />
        <Label
          for="include-expiring"
          class="text-sm cursor-pointer"
        >
          {{ t('gear.shopping.includeExpiringSoon', 'Include items expiring soon') }}
        </Label>
      </div>
    </div>
  </div>
</template>
