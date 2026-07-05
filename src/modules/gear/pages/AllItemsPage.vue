<script setup lang="ts">
import { Package, RefreshCcwIcon } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import AllItemsFilterBadges from '@/components/layout/AllItemsFilterBadges.vue'
import AllItemsFiltersMenu from '@/components/layout/AllItemsFiltersMenu.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { ALL_ITEMS_PAGE_FILTERS_KEY, ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY, config } from '@/shared/config/config'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import ItemPriorityBadge from '../components/badges/ItemPriorityBadge.vue'
import CategoryIcon from '../components/CategoryIcon.vue'
import ContainerIcon from '../components/ContainerIcon.vue'
import ItemsTableImageCell from '../components/items-table/ItemsTableImageCell.vue'
import ItemStatusBadge from '../components/ItemStatusBadge.vue'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { formatItemWeight } from '../composables/useFormattedItemWeight'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearV2 } from '../composables/useGearV2'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { createAllItemsColumns } from '../utils/allItemsColumns'
import { COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { getAllItemsForCatalogV2 } from '../utils/getAllItemsForCatalogV2'
import { createNavigationQuery } from '../utils/navigationParams'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()
const store = useGearStoreV2()
const { getItems } = useGearV2()
const { getCategoryLabel } = useCategoryLabel()
const { settings: gearSettings } = useGearSettings()
const { getContainerTypeLabel } = useContainerTypeLabel()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Loading state for refresh
const loading = ref(false)

// Helper to load filters from URL query params
function loadFiltersFromURL(): {
  globalFilter: string
  filterType: 'all' | 'containers' | 'items'
  hasImageFilter: 'all' | 'withImage' | 'withoutImage'
  page: number
  pageSize: number
} {
  const globalFilter = typeof route.query.search === 'string' ? route.query.search : ''
  const filterType = (route.query.filterType === 'containers' || route.query.filterType === 'items')
    ? route.query.filterType
    : 'all'
  const hasImageFilter = (route.query.hasImage === 'withImage' || route.query.hasImage === 'withoutImage')
    ? route.query.hasImage
    : 'all'
  const page = typeof route.query.page === 'string' ? parseInt(route.query.page, 10) : 1
  const pageSize = typeof route.query.pageSize === 'string' ? parseInt(route.query.pageSize, 10) : 20

  return {
    globalFilter,
    filterType,
    hasImageFilter,
    page: isNaN(page) || page < 1 ? 1 : page,
    pageSize: isNaN(pageSize) || pageSize < 1 ? 20 : pageSize,
  }
}

// Helper to load filters from localStorage (fallback)
interface FiltersState {
  globalFilter: string
  filterType: 'all' | 'containers' | 'items'
  hasImageFilter?: 'all' | 'withImage' | 'withoutImage'
}

function loadFiltersFromStorage(): FiltersState | null {
  const stored = localStorage.getItem(ALL_ITEMS_PAGE_FILTERS_KEY)
  if (stored) {
    try {
      return JSON.parse(stored) as FiltersState
    } catch (error) {
      console.error('Error loading filters from storage:', error)
    }
  }
  return null
}

// Initialize from URL or localStorage fallback
const urlFilters = loadFiltersFromURL()
const storedFilters = loadFiltersFromStorage()

// Filter type: 'all' | 'containers' | 'items'
const filterType = ref<'all' | 'containers' | 'items'>(urlFilters.filterType ?? storedFilters?.filterType ?? 'all')

// Image filter: 'all' | 'withImage' | 'withoutImage'
const hasImageFilter = ref<'all' | 'withImage' | 'withoutImage'>(urlFilters.hasImageFilter ?? storedFilters?.hasImageFilter ?? 'all')

// Global filter (search) for DataTable
const globalFilter = ref(urlFilters.globalFilter ?? storedFilters?.globalFilter ?? '')

// Pagination state
const page = ref(urlFilters.page)
const pageSize = ref(urlFilters.pageSize)

// Update URL when filters/search/pagination change
watch([globalFilter, filterType, hasImageFilter, page, pageSize], ([newSearch, newFilterType, newHasImage, newPage, newPageSize]) => {
  const query = { ...route.query } as Record<string, string | undefined>

  if (newSearch) {
    query.search = newSearch
  } else {
    delete query.search
  }

  if (newFilterType && newFilterType !== 'all') {
    query.filterType = newFilterType
  } else {
    delete query.filterType
  }

  if (newHasImage && newHasImage !== 'all') {
    query.hasImage = newHasImage
  } else {
    delete query.hasImage
  }

  if (newPage && newPage > 1) {
    query.page = String(newPage)
  } else {
    delete query.page
  }

  if (newPageSize && newPageSize !== 20) {
    query.pageSize = String(newPageSize)
  } else {
    delete query.pageSize
  }

  router.replace({ query })
}, { deep: true })

// Watch for URL changes (browser back/forward, refresh)
watch(() => route.query, () => {
  const urlFilters = loadFiltersFromURL()

  if (globalFilter.value !== urlFilters.globalFilter) {
    globalFilter.value = urlFilters.globalFilter
  }

  if (filterType.value !== urlFilters.filterType) {
    filterType.value = urlFilters.filterType
  }

  if (hasImageFilter.value !== urlFilters.hasImageFilter) {
    hasImageFilter.value = urlFilters.hasImageFilter
  }

  if (page.value !== urlFilters.page) {
    page.value = urlFilters.page
  }

  if (pageSize.value !== urlFilters.pageSize) {
    pageSize.value = urlFilters.pageSize
  }
}, { immediate: false })

// Get all items from all containers (includes containers as items), flattened from the V2 store
const allItemsRaw = computed<IItemWithContainer[]>(() => {
  return getAllItemsForCatalogV2(store.getAllItems)
})

// Refresh the full gear list from the active V2 service (API or localStorage) into the store
async function refreshItems() {
  try {
    loading.value = true
    await getItems()
  } catch (error) {
    console.error('Failed to refresh items:', error)
  } finally {
    loading.value = false
  }
}

// Load on mount
onMounted(() => {
  refreshItems()
})

// Filter items based on filterType and image filter
const allItems = computed<IItemWithContainer[]>(() => {
  let filtered = allItemsRaw.value

  // Apply filterType filter
  if (filterType.value === 'containers') {
    filtered = filtered.filter(item => item.isContainer === true)
  } else if (filterType.value === 'items') {
    filtered = filtered.filter(item => item.isContainer !== true)
  }

  // Apply image filter
  if (hasImageFilter.value === 'withImage') {
    filtered = filtered.filter(item => !!item.primaryImageUrl)
  } else if (hasImageFilter.value === 'withoutImage') {
    filtered = filtered.filter(item => !item.primaryImageUrl)
  }

  return filtered
})

// Handle filter removal
function removeImageFilter(filterKey: 'withImage' | 'withoutImage') {
  if (hasImageFilter.value === filterKey) {
    hasImageFilter.value = 'all'
  }
}

function removeFilterType() {
  filterType.value = 'all'
}

// Column visibility
function loadColumnVisibility(): Record<string, boolean> {
  try {
    const stored = localStorage.getItem(ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (typeof parsed === 'object' && parsed !== null) {
        return parsed
      }
    }
  } catch (error) {
    console.error('Error loading column visibility from storage:', error)
  }
  return {
    image: false,
    brand: false,
    color: false,
    wearable: false,
    consumable: false,
  }
}

const columnVisibility = ref<Record<string, boolean>>(loadColumnVisibility())

// Save column visibility to localStorage when it changes
watch(
  columnVisibility,
  (newValue) => {
    try {
      localStorage.setItem(ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY, JSON.stringify(newValue))
    } catch (error) {
      console.error('Error saving column visibility to storage:', error)
    }
  },
  { deep: true },
)

// Columns
const columns = computed(() => createAllItemsColumns(t))

// Global filter function
const globalFilterFn = (row: IItemWithContainer, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    row.containerName.toLowerCase().includes(query) ||
    getCategoryLabel(row.category).toLowerCase().includes(query) ||
    t(`gear.item.statuses.${row.status}`).toLowerCase().includes(query) ||
    (row.brand?.toLowerCase().includes(query) ?? false) ||
    (row.color?.toLowerCase().includes(query) ?? false)
  )
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <CommonPageHeader
        :icon="Package"
        :label="t('gear.allItems.title', 'All Items')"
        :description="t('gear.allItems.subtitle', 'View and manage all items from all containers')"
      >
        <template #actions>
          <Button
            v-tooltip.bottom="t('common.refresh', 'Refresh items')"
            variant="ghost"
            size="sm"
            :aria-label="t('common.refresh', 'Refresh items')"
            @click="refreshItems"
          >
            <RefreshCcwIcon class="size-4" :class="{ 'animate-spin': loading }" />
          </Button>
        </template>
      </CommonPageHeader>

      <!-- Table -->
      <DataTable
        v-model:column-visibility="columnVisibility"
        v-model:global-filter="globalFilter"
        v-model:page="page"
        v-model:page-size="pageSize"
        :columns="columns"
        :data="allItems"
        :search-placeholder="t('gear.filters.search')"
        :global-filter-fn="globalFilterFn"
        :enable-sorting="true"
        :enable-filtering="true"
        :enable-pagination="true"
        :enable-column-visibility="true"
        :initial-page-size="20"
      >
        <template #toolbar-filters>
          <div class="flex flex-wrap items-center gap-2 sm:gap-4">
            <AllItemsFiltersMenu
              v-model:filter-type="filterType"
              v-model:has-image-filter="hasImageFilter"
            />
          </div>
        </template>

        <template #toolbar-badges>
          <AllItemsFilterBadges
            :filter-type="filterType"
            :has-image-filter="hasImageFilter"
            @remove-filter-type="removeFilterType"
            @remove-filter="removeImageFilter"
          />
        </template>

        <template #image="{ row }">
          <ItemsTableImageCell
            :item-id="row.original.id"
            :container-id="row.original.containerId"
            :primary-image-url="row.original.primaryImageUrl"
          />
        </template>

        <template #category="{ row }">
          <div class="flex items-center gap-2">
            <template v-if="row.original.isContainer">
              <ContainerIcon :type="row.original.containerType ?? 'other'" :color="row.original.containerColor" :size="4" />
              <span>{{ getContainerTypeLabel(row.original.containerType ?? 'other') }}</span>
            </template>
            <template v-else>
              <CategoryIcon :category="row.original.category" :size="16" class="text-muted-foreground" />
              <span>{{ getCategoryLabel(row.original.category) }}</span>
            </template>
          </div>
        </template>

        <template #name="{ row }">
          <div class="flex items-center gap-2">
            <RouterLink
              :to="row.original.isContainer ? { path: GearRoutePath.ContainerDetailById(row.original.id), query: createNavigationQuery(undefined, 'all-items') } : { path: GearRoutePath.ItemDetailById(row.original.containerId, row.original.id), query: createNavigationQuery(undefined, 'all-items') }"
              class="font-medium hover:text-primary hover:underline transition-colors"
            >
              {{ row.original.name }}
            </RouterLink>
            <Badge v-if="row.original.isContainer" variant="outline" class="text-xs">
              {{ t('gear.item.container', 'Container') }}
            </Badge>
          </div>
        </template>

        <template #container="{ row }">
          <RouterLink
            v-if="row.original.containerId !== row.original.id"
            :to="{ path: GearRoutePath.ContainerDetailById(row.original.containerId), query: createNavigationQuery(undefined, 'all-items') }"
            class="flex items-center gap-2 cursor-pointer hover:underline font-medium"
            :class="COLOR_TEXT_CLASSES[row.original.containerColor]"
            :title="JSON.stringify(row.original)"
          >
            <ContainerIcon :type="row.original.containerType ?? 'other'" :color="row.original.containerColor" :size="4" />
            {{ row.original.containerName }}
          </RouterLink>
          <span v-else>-</span>
        </template>

        <template #quantity="{ row }">
          {{ row.original.quantity }}
        </template>

        <template #weight="{ row }">
          {{ formatItemWeight(row.original, true, settings.preferredWeightUnit ?? config.defaults.preferredWeightUnit, undefined, locale) }}
        </template>

        <template #status="{ row }">
          <ItemStatusBadge :status="row.original.status" />
        </template>

        <template #priority="{ row }">
          <ItemPriorityBadge :priority="row.original.priority" />
        </template>

        <template #brand="{ row }">
          {{ row.original.brand ?? '-' }}
        </template>

        <template #color="{ row }">
          <div v-if="row.original.color" class="flex items-center gap-2">
            <div
              class="size-3 rounded-full shrink-0 border border-border"
              :style="{
                backgroundColor: getColorHex(row.original.color) ?? DEFAULT_COLOR,
              }"
            />
            <span>{{ row.original.color }}</span>
          </div>
          <span v-else>-</span>
        </template>

        <template #wearable="{ row }">
          <Badge v-if="row.original.wearable" variant="outline" class="text-xs">
            {{ t('gear.item.wearable') }}
          </Badge>
          <span v-else>-</span>
        </template>

        <template #consumable="{ row }">
          <Badge v-if="row.original.consumable" variant="outline" class="text-xs">
            {{ t('gear.item.consumable') }}
          </Badge>
          <span v-else>-</span>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :colspan="columns.length"
            :title="t('gear.allItems.empty', 'No items found')"
            :description="t('gear.allItems.emptyDescription', 'Create containers and add items to see them here.')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>

