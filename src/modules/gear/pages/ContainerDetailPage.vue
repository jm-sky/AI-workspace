<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { AlertTriangle } from 'lucide-vue-next'
import { computed, defineAsyncComponent, ref, watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAi } from '@/modules/ai/composables/useAi'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useBackend } from '@/shared/composables/useBackend'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import type { IGearItemV2 } from '../types/gear.types.v2'
import type { TContainerColor } from '../types/gear.types.v2'
import ContainerHeader from '../components/ContainerHeader.vue'
import ContainerItemImagesGallery from '../components/ContainerItemImagesGallery.vue'
import ContainerRatingSection from '../components/ContainerRatingSection.vue'
import SortConfirmationAlert from '../components/SortConfirmationAlert.vue'
import { useCatalogue } from '../composables/catalogue/useCatalogue'
import { useContainerV2 } from '../composables/useContainerV2'
import { useGearMutations } from '../composables/useGearMutations'
import { useContainerWithChildren } from '../composables/useGearQueries'
import { useItemsParamRecognition } from '../composables/useItemsParamRecognition'
import { useJsonImportExport } from '../composables/useJsonImportExport'
import { useSearchPaginationUrl } from '../composables/useSearchPaginationUrl'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { COLOR_BORDER_CLASSES, COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { createNavigationQuery } from '../utils/navigationParams'
import { gearQueryKeys } from '../utils/queryKeys'

// Lazy load dialogs - only loaded when user opens them
const ItemsTable = defineAsyncComponent(() => import('../components/ItemsTable.vue'))
const AddNestedContainerDialog = defineAsyncComponent(() => import('../components/AddNestedContainerDialog.vue'))
const ExportToPromptDialog = defineAsyncComponent(() => import('../components/ExportToPromptDialog.vue'))
const ExportToCSVDialog = defineAsyncComponent(() => import('../components/ExportToCSVDialog.vue'))
const MoveItemDialog = defineAsyncComponent(() => import('../components/MoveItemDialog.vue'))

// Lazy load CategoryPieChart - not critical for initial render
const CategoryPieChart = defineAsyncComponent(() => import('../components/CategoryPieChart.vue'))

// Lazy load AI Chat Dialog - only needed when user opens AI dialog
// This reduces initial bundle size and improves critical path performance
const AiChatDialog = defineAsyncComponent(() => import('@/modules/ai/components/AiChatDialog.vue'))

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const storeV2 = useGearStoreV2()
const queryClient = useQueryClient()
const { shouldUseAPI } = useBackend()
const { container: containerFromStore } = useContainerV2()
// useGearMutations auto-invalidates the gear query cache after each mutation,
// keeping the page (driven by useContainerWithChildren) in sync.
const { deleteItem, updateItem, moveItem, batchUpdateOrder } = useGearMutations()

// Refresh the page data (TanStack Query cache). Used for pure refreshes that the
// cache doesn't know about, e.g. restoring original order or manual refresh.
const refreshContainer = () => queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })
const { user, isAuthenticated } = useAuth()
const { canUseAi } = useAi()
const { setTitle } = usePageTitle()
const { unlinkItemFromCatalogue } = useCatalogue()

const containerId = route.params.id as string

// Fetch container + children from API when using backend
const {
  container: containerFromAPI,
  children: childrenFromAPI,
  isLoading: _isLoadingAPI
} = useContainerWithChildren(
  computed(() => shouldUseAPI.value ? containerId : undefined)
)

// Use API data if available, otherwise fall back to store
const container = computed(() => {
  if (shouldUseAPI.value && containerFromAPI.value) {
    return containerFromAPI.value
  }
  return containerFromStore.value
})

const cardClass = computed(() => {
  if (!container.value?.color) return ''
  if (container.value.color === 'default') return ''
  const color = container.value.color as TContainerColor
  return `${COLOR_TEXT_CLASSES[color]} border ${COLOR_BORDER_CLASSES[color]} outline-2 outline-current/15`
})

// Set dynamic page title
watchEffect(() => {
  if (container.value?.name) {
    setTitle('gear.pages.containerDetail', { name: container.value.name })
  }
})

// Check if user can edit container (admin AND owner)
const canEditContainer = computed(() => {
  if (!isAuthenticated.value || !user.value || !container.value) {
    return false
  }
  // Check if user is admin
  const isAdmin = user.value?.isAdmin ?? false
  if (!isAdmin) return false

  // For public containers, check authorId
  if (container.value.authorId) {
    return container.value.authorId === user.value.id
  }
  // For private containers (no authorId), if we can access the container,
  // it means we own it (backend handles authorization)
  // For localStorage, all containers are considered owned by current user
  return true
})

// Dialog state
const isAddContainerDialogOpen = ref(false)
const isExportToPromptDialogOpen = ref(false)
const isExportToCSVDialogOpen = ref(false)
const isAiDialogOpen = ref(false)
const isMoveItemDialogOpen = ref(false)
const itemToMove = ref<IGearItemV2 | null>(null)
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

// Rating section moved to ContainerRatingSection.vue component

// File operations handled in handleImport

// Items - use API data if available, otherwise fall back to store
const items = computed<IGearItemV2[]>(() => {
  if (!container.value) return []

  // Use API data if available (when backend is enabled)
  if (shouldUseAPI.value && childrenFromAPI.value) {
    return childrenFromAPI.value
  }

  // Fall back to store (localStorage)
  return storeV2.getChildrenOfItem(container.value.id)
})

// Search and pagination state synchronized with URL
const { search, page, pageSize } = useSearchPaginationUrl({
  defaultPageSize: 10,
  preserveKeys: ['returnTo', 'from'],
})

const globalFilter = search

// Display items with pending sorting changes applied
// This ensures that when user reorders items, the table shows the new order immediately
// even before saving, allowing for multiple reorders in sequence
const displayItems = computed<IGearItemV2[]>(() => {
  if (pendingSortingChanges.value.length === 0) {
    return items.value
  }

  // Create a map of pending changes by item ID
  const pendingMap = new Map(pendingSortingChanges.value.map(item => [item.id, item]))

  // Merge pending changes with current items
  // Items with pending changes use pending orderIndex, others keep their current orderIndex
  const mergedItems = items.value.map(item => {
    const pending = pendingMap.get(item.id)
    if (pending) {
      return { ...item, orderIndex: pending.orderIndex }
    }
    return item
  })

  // If pending changes contain all items (complete reorder), sort by orderIndex
  // Otherwise, items are already in correct order from items.value
  if (pendingSortingChanges.value.length === items.value.length) {
    return [...mergedItems].sort((a, b) => {
      const orderA = a.orderIndex ?? Number.MAX_SAFE_INTEGER
      const orderB = b.orderIndex ?? Number.MAX_SAFE_INTEGER
      return orderA - orderB
    })
  }

  return mergedItems
})

// Pending sorting changes (for batch save when backend enabled)
const pendingSortingChanges = ref<IGearItemV2[]>([])
const isSavingSorting = ref(false)

// Actions
const handleEditItem = (item: IGearItemV2) => {
  router.push({
    path: GearRoutePath.ItemEditById(containerId, item.id),
    query: createNavigationQuery('container'),
  })
}

const handleDeleteItem = async (item: IGearItemV2) => {
  if (!confirm(t('gear.item.deleteConfirm'))) return
  try {
    await deleteItem(item.id)
    toast.success(t('common.success'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleStatusChange = async (item: IGearItemV2, status: IGearItemV2['status']) => {
  try {
    await updateItem(item.id, { status })
    toast.success(t('common.success'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleUnlinkFromCatalogue = async (item: IGearItemV2) => {
  try {
    await unlinkItemFromCatalogue(item.id)
    toast.success(t('gear.catalogue.unlinkedSuccess'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleMoveItem = (item: IGearItemV2) => {
  itemToMove.value = item
  isMoveItemDialogOpen.value = true
}

const handleMoveConfirm = async (targetContainerId: string) => {
  if (!itemToMove.value) return

  try {
    await moveItem(itemToMove.value.id, targetContainerId)
    toast.success(t('gear.actions.moved') ?? 'Item moved successfully')
  } catch (error) {
    console.error('Failed to move item:', error)
    toast.error(t('common.error'))
  }
}

const handleHideItemImages = async () => {
  if (!container.value) return
  try {
    await updateItem(container.value.id, { showItemImages: false })
    toast.success(t('gear.container.itemImages.hidden', 'Item images hidden'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleReorder = (reorderedItems: IGearItemV2[]) => {
  // Store pending changes - don't save yet, wait for user confirmation
  // Alert will show for both backend and localStorage
  // This works the same way as handleSortingChange - batch mode with confirmation
  pendingSortingChanges.value = reorderedItems
}

const handleSortingChange = (sortedItems: IGearItemV2[]) => {
  // If sorting was cleared (empty array), clear pending changes
  if (sortedItems.length === 0) {
    pendingSortingChanges.value = []
    return
  }

  // Store pending changes - don't save yet, wait for user confirmation
  // Alert will show for both backend and localStorage
  pendingSortingChanges.value = sortedItems
}

const handleSaveSorting = async () => {
  if (pendingSortingChanges.value.length === 0) return

  try {
    isSavingSorting.value = true

    await batchUpdateOrder(
      pendingSortingChanges.value.map((item, index) => ({
        id: item.id,
        orderIndex: item.orderIndex ?? index,
      })),
    )
    toast.success(t('gear.item.reorderSuccess', 'Kolejność przedmiotów została zaktualizowana'))
    pendingSortingChanges.value = []
  } catch {
    toast.error(t('common.error'))
  } finally {
    isSavingSorting.value = false
  }
}

const handleCancelSorting = async () => {
  // Clear pending changes
  pendingSortingChanges.value = []

  // Reload container to restore original order
  // For localStorage: store is reactive, so clearing pending changes is enough
  // For backend: we need to reload from API to get original order
  if (shouldUseAPI.value && container.value) {
    try {
      // Reload container from API to restore original order
      await refreshContainer()
    } catch {
      // If refresh fails, just clear pending changes
      // User can manually reset sorting
    }
  }
}

const { handleJsonExport, handleJsonImport } = useJsonImportExport()

const handleAddContainer = () => {
  isAddContainerDialogOpen.value = true
}

// Rating handlers moved to ContainerRatingSection.vue component

const handleAddNestedContainer = async (nestedContainerId: string) => {
  try {
    const nestedContainer = storeV2.getItemById(nestedContainerId)
    if (!nestedContainer) {
      toast.error(t('common.error'))
      return
    }

    // V2-native nesting: re-parent the existing container under this one by setting
    // its parentItemId. No placeholder item is needed (that was the V1 dual model).
    await updateItem(nestedContainerId, { parentItemId: containerId })
    toast.success(t('common.success'))
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error adding nested container:', error)
  }
}

const handleExportToPrompt = () => {
  if (!container.value) return
  isExportToPromptDialogOpen.value = true
}

const handleExportToCSV = () => {
  if (!container.value) return
  isExportToCSVDialogOpen.value = true
}

const { handleRecognizeParameters, handleRecognizeParametersAll } = useItemsParamRecognition(container, items)

const handleManageShareTokens = () => {
  router.push(GearRoutePath.ContainerShareTokensById(containerId))
}

const handleRefresh = async () => {
  if (!container.value) return
  try {
    await refreshContainer()
    toast.success(t('common.refreshed'))
  } catch (error) {
    console.error('Failed to refresh container:', error)
    toast.error(t('common.error'))
  }
}

// Redirect if container not found
if (!container.value) {
  router.push(GearRoutePath.Containers)
}
</script>

<template>
  <AuthenticatedLayout :card-class="cardClass">
    <div v-if="container" class="space-y-6 w-full max-w-full text-card-foreground">
      <!-- ContainerHeader uses V2 types -->
      <ContainerHeader
        :container="container"
        @export="handleJsonExport"
        @import="handleJsonImport"
        @add-container="handleAddContainer"
        @export-to-prompt="handleExportToPrompt"
        @export-to-csv="handleExportToCSV"
        @recognize-parameters-all="handleRecognizeParametersAll"
        @ai-chat="isAiDialogOpen = true"
        @manage-share-tokens="handleManageShareTokens"
        @refresh="handleRefresh"
      />

      <!-- Hidden by Reports Alert (for container owner) -->
      <Alert
        v-if="container?.isHiddenByReports && canEditContainer"
        variant="destructive"
        class="mb-4"
      >
        <AlertTriangle />
        <AlertTitle>
          {{ t('gear.container.hiddenByReports.title') }}
        </AlertTitle>
        <AlertDescription>
          {{ t('gear.container.hiddenByReports.description') }}
        </AlertDescription>
      </Alert>

      <!-- Sort Confirmation Alert (always show when there are pending changes) -->
      <SortConfirmationAlert
        v-if="pendingSortingChanges.length > 0"
        :pending-items="pendingSortingChanges"
        :loading="isSavingSorting"
        @save="handleSaveSorting"
        @cancel="handleCancelSorting"
      />

      <!-- Items Table -->
      <ItemsTable
        v-model:global-filter="globalFilter"
        v-model:page="page"
        v-model:page-size="pageSize"
        :items="displayItems"
        :container-id="containerId"
        @edit="handleEditItem"
        @delete="handleDeleteItem"
        @status-change="handleStatusChange"
        @recognize-parameters="handleRecognizeParameters"
        @reorder="handleReorder"
        @sorting-change="handleSortingChange"
        @unlink-from-catalogue="handleUnlinkFromCatalogue"
        @move="handleMoveItem"
      />

      <!-- Container Item Images Gallery -->
      <ContainerItemImagesGallery
        :items="items"
        :container-id="containerId"
        :editable="canEditContainer"
        :show-item-images="container.showItemImages"
        @hide="handleHideItemImages"
      />

      <!-- Category Pie Chart -->
      <CategoryPieChart v-if="container" :container="container" />

      <!-- Rating Section -->
      <ContainerRatingSection v-if="container" :container="container" />

      <!-- Add Nested Container Dialog -->
      <AddNestedContainerDialog
        v-model:open="isAddContainerDialogOpen"
        :current-container-id="containerId"
        @confirm="handleAddNestedContainer"
      />

      <!-- Export to Prompt Dialog -->
      <ExportToPromptDialog
        v-model:open="isExportToPromptDialogOpen"
        :container="container"
      />

      <!-- Export to CSV Dialog -->
      <ExportToCSVDialog
        v-model:open="isExportToCSVDialogOpen"
        :container="container"
      />

      <!-- AI Chat Dialog -->
      <AiChatDialog
        v-if="canUseAi"
        v-model:open="isAiDialogOpen"
        :context="{ container_ids: [containerId] }"
        :restore-history-id="restoreHistoryId"
      />

      <MoveItemDialog
        v-if="itemToMove"
        v-model:open="isMoveItemDialogOpen"
        :item-id="itemToMove.id"
        :current-container-id="containerId"
        @move="handleMoveConfirm"
      />
    </div>
  </AuthenticatedLayout>
</template>

