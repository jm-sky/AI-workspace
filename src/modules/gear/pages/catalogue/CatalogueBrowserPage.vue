<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { BookIcon, Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { CATALOGUE_BROWSER_PAGE_FILTERS_KEY } from '@/shared/config/config'
import type { TCataloguePriceTier } from '../../types/catalogue.types'
import type { TGearItemCategory, TGearItemQuality } from '../../types/gear.types'
import CatalogueFilters from '../../components/catalogue/CatalogueFilters.vue'
import CatalogueItemCard from '../../components/catalogue/CatalogueItemCard.vue'
import { useCatalogue } from '../../composables/catalogue/useCatalogue'

const { t } = useI18n()
const {
  catalogueItems,
  isLoadingItems,
  updateSearchParams,
  clearFilters,
  refetchItems,
} = useCatalogue({ enableItemsQuery: true })

// Search filter
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)

// Category filter
const selectedCategory = ref<TGearItemCategory | null>(null)

// Brand filter
const brandFilterRaw = ref('')
const brandFilter = refDebounced(brandFilterRaw, 300)

// Price tier filter
const priceTierFilter = ref<TCataloguePriceTier | null>(null)

// Quality filter
const qualityFilter = ref<TGearItemQuality | null>(null)

// Helper to load filters from localStorage
interface FiltersState {
  searchQuery: string
  category: TGearItemCategory | null
  brand: string
  priceTier: TCataloguePriceTier | null
  quality: TGearItemQuality | null
}

function loadFiltersFromStorage(): FiltersState | null {
  const stored = localStorage.getItem(CATALOGUE_BROWSER_PAGE_FILTERS_KEY)
  if (stored) {
    try {
      return JSON.parse(stored) as FiltersState
    } catch (error) {
      console.error('Error loading filters from storage:', error)
    }
  }
  return null
}

// Helper to save filters to localStorage
function saveFiltersToStorage(): void {
  try {
    const filters: FiltersState = {
      searchQuery: searchQueryRaw.value,
      category: selectedCategory.value,
      brand: brandFilterRaw.value,
      priceTier: priceTierFilter.value,
      quality: qualityFilter.value,
    }
    localStorage.setItem(CATALOGUE_BROWSER_PAGE_FILTERS_KEY, JSON.stringify(filters))
  } catch (error) {
    console.error('Error saving filters to storage:', error)
  }
}

// Load filters from storage on mount
const savedFilters = loadFiltersFromStorage()
if (savedFilters) {
  searchQueryRaw.value = savedFilters.searchQuery
  selectedCategory.value = savedFilters.category
  brandFilterRaw.value = savedFilters.brand
  priceTierFilter.value = savedFilters.priceTier
  qualityFilter.value = savedFilters.quality
}

// Watch filters and update search params
watch(
  [searchQuery, selectedCategory, brandFilter, priceTierFilter, qualityFilter],
  () => {
    updateSearchParams({
      query: searchQuery.value ?? null,
      category: selectedCategory.value,
      brand: brandFilter.value ?? null,
      priceTier: priceTierFilter.value,
      quality: qualityFilter.value,
      skip: 0,
    })
    saveFiltersToStorage()
  },
  { immediate: true },
)

const handleClearFilters = () => {
  searchQueryRaw.value = ''
  selectedCategory.value = null
  brandFilterRaw.value = ''
  priceTierFilter.value = null
  qualityFilter.value = null
  clearFilters()
  saveFiltersToStorage()
}

const handleRefresh = () => {
  refetchItems()
}

const hasActiveFilters = computed(() => {
  return (
    searchQueryRaw.value !== '' ||
    selectedCategory.value !== null ||
    brandFilterRaw.value !== '' ||
    priceTierFilter.value !== null ||
    qualityFilter.value !== null
  )
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="w-full max-w-full space-y-6">
      <!-- Header -->
      <CommonPageHeader
        :icon="BookIcon"
        :label="t('gear.catalogue.title')"
        :description="t('gear.catalogue.subtitle')"
      />

      <!-- Search and Filters -->
      <CatalogueFilters
        v-model:search-query="searchQueryRaw"
        v-model:category="selectedCategory"
        v-model:brand="brandFilterRaw"
        v-model:price-tier="priceTierFilter"
        v-model:quality="qualityFilter"
        :loading="isLoadingItems"
        :has-active-filters
        @clear-filters="handleClearFilters"
        @refresh="handleRefresh"
      />

      <!-- Loading State -->
      <div v-if="isLoadingItems" class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="i in 6" :key="i" class="h-64 animate-pulse rounded-lg bg-muted" />
      </div>

      <!-- Catalogue Items Grid -->
      <div v-else-if="catalogueItems.length > 0" class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <CatalogueItemCard v-for="item in catalogueItems" :key="item.id" :item />
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <div class="mb-4 rounded-full bg-muted p-6">
          <Package class="size-12 text-muted-foreground" />
        </div>
        <h3 class="mb-2 text-lg font-semibold">
          {{ hasActiveFilters ? t('gear.catalogue.noResults') : t('gear.catalogue.empty') }}
        </h3>
        <p class="max-w-md text-muted-foreground">
          {{ hasActiveFilters ? t('gear.catalogue.noResultsDescription') : t('gear.catalogue.emptyDescription') }}
        </p>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
