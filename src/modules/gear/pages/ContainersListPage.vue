<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { refDebounced } from '@vueuse/core'
import { FileInput, Package } from 'lucide-vue-next'
import { computed, defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import Pagination from '@/components/data-table/Pagination.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAi } from '@/modules/ai/composables/useAi'
import { useBackend } from '@/shared/composables/useBackend'
import { CONTAINERS_LIST_PAGE_FILTERS_KEY } from '@/shared/config/config'
import type { IGearItemV2 } from '../types/gear.types.v2'
import ContainerCard from '../components/ContainerCard.vue'
import ContainersFilters from '../components/ContainersFilters.vue'
import ContainersListPageDropdown from '../components/ContainersListPageDropdown.vue'
import GenerateExampleGearButton from '../components/GenerateExampleGearButton.vue'
import PremiumFeatureLockButton from '../components/PremiumFeatureLockButton.vue'

// Lazy load dialogs - only loaded when user opens them
const ExportToCSVDialog = defineAsyncComponent(() => import('../components/ExportToCSVDialog.vue'))
const ExportToPromptDialog = defineAsyncComponent(() => import('../components/ExportToPromptDialog.vue'))
const ImportMarkdownDialog = defineAsyncComponent(() => import('../components/ImportMarkdownDialog.vue'))
const AiChatDialog = defineAsyncComponent(() => import('@/modules/ai/components/AiChatDialog.vue'))
import { downloadBlob } from '@/shared/utils/downloadBlob'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useContainersWithChildren } from '../composables/useGearQueries'
import { useGearV2 } from '../composables/useGearV2'
import { GearRouteIcon, GearRoutePath } from '../routes'
import { getActionIcon } from '../utils/actionIcons'
import { exportContainersToJSONV2, generateAllContainersJSONFileName } from '../utils/exportToJsonV2'
import type { TUUID } from '@/shared/types/base.type'

// Action icons
const ExportAllToMarkdownIcon = getActionIcon('exportAllToMarkdown')
const CreateIcon = getActionIcon('create')

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const queryClient = useQueryClient()
const { containers: containersFromStore, rootContainers: rootContainersFromStore, deleteItem, refreshAll, getChildrenFromStore } = useGearV2()
const { getContainerTypeLabel } = useContainerTypeLabel()
const { canUseAi } = useAi()
const { shouldUseAPI } = useBackend()

// Fetch containers with children from API (for statistics like weight, readiness)
// Only enabled when backend is available
const { data: containersFromAPI, isLoading: isLoadingAPI } = useContainersWithChildren({
  enabled: computed(() => shouldUseAPI.value)
})

// Use API data if available, otherwise fall back to store (localStorage)
const containers = computed(() => {
  if (shouldUseAPI.value) {
    return containersFromAPI.value ?? []
  }
  return containersFromStore.value
})

const rootContainers = computed(() => {
  if (shouldUseAPI.value) {
    const apiContainers = containersFromAPI.value ?? []
    return apiContainers.filter(c => !c.parentItemId)
  }
  return rootContainersFromStore.value
})

// Filters - using refs that will be bound to ContainersFilters via v-model
const loading = computed(() => isLoadingAPI.value)

// Initialize from URL query params or localStorage fallback
function loadFiltersFromURL(): { searchQuery: string; showOnlyRootContainers: boolean } {
  const searchQuery = typeof route.query.search === 'string' ? route.query.search : ''
  const showOnlyRootContainers = route.query.rootOnly === 'true'

  return { searchQuery, showOnlyRootContainers }
}

function loadFiltersFromStorage(): { searchQuery: string; showOnlyRootContainers: boolean } | null {
  const stored = localStorage.getItem(CONTAINERS_LIST_PAGE_FILTERS_KEY)
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch (error) {
      console.error('Error loading filters from storage:', error)
    }
  }
  return null
}

// Load filters - prioritize URL params, fallback to localStorage
const urlFilters = loadFiltersFromURL()
const storedFilters = loadFiltersFromStorage()

const searchQueryRaw = ref<string>(urlFilters.searchQuery ?? storedFilters?.searchQuery ?? '')
const searchQuery = refDebounced<string>(searchQueryRaw, 300)
const showOnlyRootContainers = ref<boolean>(urlFilters.showOnlyRootContainers ?? storedFilters?.showOnlyRootContainers ?? false)

// Pagination state
const DEFAULT_PAGE_SIZE = 12
const page = ref<number>(1)
const pageSize = ref<number>(DEFAULT_PAGE_SIZE)

// Update URL when filters change
watch([searchQueryRaw, showOnlyRootContainers], ([newSearch, newRootOnly]) => {
  const query = { ...route.query } as Record<string, string | undefined>

  if (newSearch) {
    query.search = newSearch
  } else {
    delete query.search
  }

  if (newRootOnly) {
    query.rootOnly = 'true'
  } else {
    delete query.rootOnly
  }

  // Preserve other query params (like import)
  router.replace({ query })
}, { deep: true })

// Watch for URL changes (browser back/forward, refresh)
watch(() => route.query, (newQuery) => {
  const urlSearch = typeof newQuery.search === 'string' ? newQuery.search : ''
  const urlRootOnly = newQuery.rootOnly === 'true'

  if (searchQueryRaw.value !== urlSearch) {
    searchQueryRaw.value = urlSearch
  }

  if (showOnlyRootContainers.value !== urlRootOnly) {
    showOnlyRootContainers.value = urlRootOnly
  }
}, { immediate: false })

// Dialogs
const importDialogOpen = ref(false)
const isExportToPromptDialogOpen = ref(false)
const isExportToCSVDialogOpen = ref(false)
const isAiDialogOpen = ref(false)
const restoreHistoryId = ref<string | null>(null)

// Watch for restoreHistoryId query param
watch(() => route.query.restoreHistoryId, (historyId) => {
  if (typeof historyId === 'string' && historyId) {
    restoreHistoryId.value = historyId
    isAiDialogOpen.value = true
    // Remove query param from URL
    router.replace({ query: { ...route.query, restoreHistoryId: undefined } })
  }
}, { immediate: true })

// Check for import query parameter and open dialog
// Note: Container loading is now handled by TanStack Query (useContainersWithChildren)
onMounted(() => {
  if (route.query.import === 'true') {
    importDialogOpen.value = true
    // Remove query parameter from URL
    router.replace({ query: { ...route.query, import: undefined } })
  }
})

// Watch for route changes (in case user navigates back/forward)
watch(() => route.query.import, (shouldImport) => {
  if (shouldImport === 'true') {
    importDialogOpen.value = true
    // Remove query parameter from URL
    router.replace({ query: { ...route.query, import: undefined } })
  }
})

// Filtered containers
const filteredContainers = computed<IGearItemV2[]>(() => {
  // First filter by root containers if enabled
  let baseContainers = containers.value
  if (showOnlyRootContainers.value) {
    baseContainers = rootContainers.value
  } else {
    // Hide containers with hideWhenNested=true AND parentItemId set
    baseContainers = baseContainers.filter(container => {
      if (container.hideWhenNested && container.parentItemId) {
        return false // Hide this container
      }
      return true
    })
  }

  // Then filter by search query
  let filtered = baseContainers
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = baseContainers.filter(container => {
      return (
        container.name.toLowerCase().includes(query) ||
        container.description?.toLowerCase().includes(query) ||
        getContainerTypeLabel(container.containerType || 'backpack').toLowerCase().includes(query)
      )
    })
  }

  // Sort: favorites first, then by creation date (newest first)
  return filtered.sort((a, b) => {
    // Favorites first
    if (a.favorite && !b.favorite) return -1
    if (!a.favorite && b.favorite) return 1
    // Then by creation date (newest first)
    return new Date(b.createdAt || '').getTime() - new Date(a.createdAt || '').getTime()
  })
})

// Paginated containers
const paginatedContainers = computed<IGearItemV2[]>(() => {
  const start = (page.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredContainers.value.slice(start, end)
})

// Reset to first page when filters change
watch([searchQuery, showOnlyRootContainers], () => {
  page.value = 1
})

// Actions
const handleCreate = () => {
  router.push(GearRoutePath.ContainerNew)
}

const handleImport = () => {
  importDialogOpen.value = true
}

const handleRefresh = async () => {
  if (shouldUseAPI.value) {
    // Invalidate all gear queries to refetch fresh data
    await queryClient.invalidateQueries({ queryKey: ['gear'] })
    toast.success(t('common.refresh'))
  } else {
    // For localStorage, use legacy refresh
    try {
      await refreshAll({ itemType: 'container' })
      toast.success(t('common.refresh'))
    } catch (error) {
      console.error('Failed to refresh containers:', error)
      toast.error(t('common.error'))
    }
  }
}

const handleImportComplete = () => {
  // Refresh is automatic via store reactivity
}

const handleDelete = async (id: TUUID) => {
  if (confirm(t('gear.container.deleteConfirm'))) {
    try {
      await deleteItem(id)
      toast.success(t('common.success'))
    } catch {
      toast.error(t('common.error'))
    }
  }
}

const handleExportAllToMarkdown = () => {
  if (containers.value.length === 0) {
    toast.error(t('gear.export.noContainers'))
    return
  }

  isExportToPromptDialogOpen.value = true
}

const handleExportAllToCSV = () => {
  if (containers.value.length === 0) {
    toast.error(t('gear.export.noContainers'))
    return
  }

  isExportToCSVDialogOpen.value = true
}

const handleExportAllToJson = () => {
  const roots = rootContainers.value
  if (roots.length === 0) {
    toast.error(t('gear.export.noContainers'))
    return
  }

  const json = exportContainersToJSONV2(roots, {
    getChildrenOfItem: getChildrenFromStore,
    includeNestedContainers: true,
  })
  downloadBlob(new Blob([json], { type: 'application/json' }), generateAllContainersJSONFileName())
  toast.success(t('gear.export.jsonSuccess', { count: roots.length }))
}

const handleAiChat = () => {
  isAiDialogOpen.value = true
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <CommonPageHeader
        :icon="GearRouteIcon.Containers"
        :label="t('gear.page.containers')"
        :description="t('gear.page.title')"
      >
        <template #actions>
          <PremiumFeatureLockButton
            :has-access="canUseAi"
            icon="ai"
            :tooltip="t('gear.actions.aiAssistant')"
            :aria-label="t('gear.actions.aiAssistant')"
            @click="handleAiChat"
          />
          <Button
            v-if="containers.length > 0"
            v-tooltip.bottom="t('gear.export.allToMarkdown')"
            variant="ghost"
            size="sm"
            class="shrink-0"
            :aria-label="$t('gear.export.allToMarkdown')"
            @click="handleExportAllToMarkdown"
          >
            <ExportAllToMarkdownIcon class="size-4" />
          </Button>
          <Button
            v-tooltip.bottom="t('gear.container.create.title')"
            variant="default"
            class="shrink-0 flex-1 sm:flex-none"
            @click="handleCreate"
          >
            <CreateIcon class="size-4" />
            {{ t('gear.container.create.title') }}
          </Button>
        </template>
        <template #dropdown>
          <ContainersListPageDropdown
            @export-all-to-markdown="handleExportAllToMarkdown"
            @export-all-to-csv="handleExportAllToCSV"
            @export-all-to-json="handleExportAllToJson"
            @import="handleImport"
          />
        </template>
      </CommonPageHeader>

      <!-- Search and Filters -->
      <ContainersFilters
        v-model:search-query="searchQueryRaw"
        v-model:show-only-root-containers="showOnlyRootContainers"
        root-containers-filter
        :loading
        @refresh="handleRefresh"
      />

      <!-- Containers Grid -->
      <div v-if="filteredContainers.length > 0" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        <ContainerCard
          v-for="container in paginatedContainers"
          :key="container.id"
          :container="container"
          @delete="handleDelete"
        />
      </div>

      <!-- Pagination -->
      <Pagination
        v-if="filteredContainers.length > 0"
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="filteredContainers.length"
        :page-size-options="[6, 12, 24, 48, 100]"
      />

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <div class="rounded-full bg-muted p-6 mb-4">
          <Package class="size-12 text-muted-foreground" />
        </div>
        <h3 class="text-lg font-semibold mb-2">
          {{ t('gear.container.empty') }}
        </h3>
        <p class="text-muted-foreground mb-6 max-w-md">
          {{ t('gear.container.emptyDescription') }}
        </p>
        <div class="flex flex-col items-center justify-center flex-wrap gap-3">
          <Button @click="handleCreate">
            <CreateIcon class="size-4" />
            {{ t('gear.container.create.title') }}
          </Button> -

          <div class="flex items-center gap-2 text-muted-foreground">
            <span>{{ t('common.or', 'or') }}</span>
          </div>

          <GenerateExampleGearButton size="default" :redirect="false" />

          <ButtonLink
            variant="outline"
            :to="GearRoutePath.Import"
          >
            <FileInput class="size-4" />
            {{ t('gear.import.fromMarkdown', 'Import from Markdown') }}
          </ButtonLink>
        </div>
      </div>
    </div>

    <!-- Import Dialog -->
    <ImportMarkdownDialog
      v-model:open="importDialogOpen"
      @import-complete="handleImportComplete"
    />

    <!-- Export to Prompt Dialog -->
    <ExportToPromptDialog
      v-model:open="isExportToPromptDialogOpen"
      :containers="containers"
    />

    <!-- Export to CSV Dialog -->
    <ExportToCSVDialog
      v-model:open="isExportToCSVDialogOpen"
      :containers="containers"
    />

    <!-- AI Chat Dialog -->
    <AiChatDialog
      v-if="canUseAi"
      v-model:open="isAiDialogOpen"
      :context="{ container_ids: filteredContainers.map(c => c.id) }"
      :restore-history-id="restoreHistoryId"
    />
  </AuthenticatedLayout>
</template>

