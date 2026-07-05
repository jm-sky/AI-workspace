<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { Package } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { PUBLIC_CONTAINERS_BROWSER_PAGE_FILTERS_KEY } from '@/shared/config/config'
import type { IGearItemV2 } from '../types/gear.types.v2'
import ContainersFilters from '../components/ContainersFilters.vue'
import PublicContainerCard from '../components/PublicContainerCard.vue'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { GearRouteIcon } from '../routes'
import { publicContainersService } from '../services/publicContainersService'
import { convertV1ContainerToV2 } from '../utils/typeConverters'

const { t } = useI18n()
const { getContainerTypeLabel } = useContainerTypeLabel()

const containers = ref<IGearItemV2[]>([])
const loading = ref(true)

// Search filter
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)

// Helper to load filters from localStorage
interface FiltersState {
  searchQuery: string
}

function loadFiltersFromStorage(): FiltersState | null {
  const stored = localStorage.getItem(PUBLIC_CONTAINERS_BROWSER_PAGE_FILTERS_KEY)
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
    }
    localStorage.setItem(PUBLIC_CONTAINERS_BROWSER_PAGE_FILTERS_KEY, JSON.stringify(filters))
  } catch (error) {
    console.error('Error saving filters to storage:', error)
  }
}

// Load filters from storage on mount
const savedFilters = loadFiltersFromStorage()
if (savedFilters) {
  searchQueryRaw.value = savedFilters.searchQuery
}

// Watch filters and save to localStorage
watch(searchQueryRaw, () => {
  saveFiltersToStorage()
})

// Filtered containers
const filteredContainers = computed<IGearItemV2[]>(() => {
  if (!searchQuery.value.trim()) {
    return containers.value
  }

  const query = searchQuery.value.toLowerCase()
  return containers.value.filter(container => {
    return (
      container.name.toLowerCase().includes(query) ||
      container.description?.toLowerCase().includes(query) ||
      getContainerTypeLabel(container.containerType || 'backpack').toLowerCase().includes(query) ||
      container.authorName?.toLowerCase().includes(query)
    )
  })
})

const loadContainers = async () => {
  loading.value = true
  try {
    // Backend API returns V1 format - convert to V2 (backend will be updated to return V2 in future)
    const publicContainersV1 = await publicContainersService.getPublicContainers()
    containers.value = publicContainersV1.map(container => convertV1ContainerToV2(container))
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Failed to load public containers:', error)
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadContainers()
}

onMounted(() => {
  loadContainers()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <CommonPageHeader
        :icon="GearRouteIcon.PublicContainers"
        :label="t('gear.publicContainers.title')"
        :description="t('gear.publicContainers.description')"
      />

      <!-- Search and Filters -->
      <ContainersFilters
        v-model:search-query="searchQueryRaw"
        :loading
        @refresh="handleRefresh"
      />

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="h-48 bg-muted rounded-lg animate-pulse" />
      </div>

      <!-- Containers Grid -->
      <div v-else-if="filteredContainers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PublicContainerCard
          v-for="container in filteredContainers"
          :key="container.id"
          :container
        />
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <div class="rounded-full bg-muted p-6 mb-4">
          <Package class="size-12 text-muted-foreground" />
        </div>
        <h3 class="text-lg font-semibold mb-2">
          {{ t('gear.publicContainers.empty') }}
        </h3>
        <p class="text-muted-foreground max-w-md">
          {{ t('gear.publicContainers.emptyDescription') }}
        </p>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
