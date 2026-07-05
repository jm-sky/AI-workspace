<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'
import { Check, Package } from 'lucide-vue-next'
import { computed, defineAsyncComponent, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import { ITEMS_TABLE_COLUMN_VISIBILITY_KEY } from '@/shared/config/config'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearItemPriority } from '../types/gear.types.v2'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { formatItemPriceV2 } from '../composables/useFormattedItemPriceV2'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearV2 } from '../composables/useGearV2'
import { useItemsTableEditMode } from '../composables/useItemsTableEditMode'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { calculateTotalWeightSyncV2 } from '../utils/containerCalculationsV2'
import { isExpiringSoon } from '../utils/isExpiringSoon'
import { createItemsColumns } from '../utils/itemsColumns'
import { createNavigationQuery } from '../utils/navigationParams'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'
import ItemPriorityBadge from './badges/ItemPriorityBadge.vue'
import ItemsTableCategoryCell from './items-table/ItemsTableCategoryCell.vue'
import ItemsTableEditableCategoryCell from './items-table/ItemsTableEditableCategoryCell.vue'
import ItemsTableEditableNameCell from './items-table/ItemsTableEditableNameCell.vue'
import ItemsTableEditablePriceCell from './items-table/ItemsTableEditablePriceCell.vue'
import ItemsTableEditablePriorityCell from './items-table/ItemsTableEditablePriorityCell.vue'
import ItemsTableEditableQuantityCell from './items-table/ItemsTableEditableQuantityCell.vue'
import ItemsTableEditableStatusCell from './items-table/ItemsTableEditableStatusCell.vue'
import ItemsTableEditableWeightCell from './items-table/ItemsTableEditableWeightCell.vue'
import ItemsTableImageCell from './items-table/ItemsTableImageCell.vue'
import ItemsTableNameCell from './items-table/ItemsTableNameCell.vue'
import ItemsTableWeightCell from './items-table/ItemsTableWeightCell.vue'
import ItemsTableNestedContainerRow from './ItemsTableNestedContainerRow.vue'
import ItemStatusBadge from './ItemStatusBadge.vue'
import type { SortingState } from '@tanstack/vue-table'
import type { TUUID } from '@/shared/types/base.type'

// Lazy load row actions - only used in non-public mode
const ItemsTableRowActions = defineAsyncComponent(() => import('./ItemsTableRowActions.vue'))

const props = withDefaults(
  defineProps<{
    items: IGearItemV2[]
    loading?: boolean
    publicMode?: boolean
    containerId?: string
    globalFilter?: string
    page?: number
    pageSize?: number
  }>(),
  {
    loading: false,
    publicMode: false,
    containerId: undefined,
    globalFilter: undefined,
    page: undefined,
    pageSize: undefined,
  },
)

// Internal state for search and pagination (used when not provided via props)
const internalGlobalFilter = ref('')
const internalPage = ref(1)
const internalPageSize = ref(10)

// Use props if provided, otherwise use internal state
const globalFilterModel = computed({
  get: () => {
    if (props.globalFilter !== undefined) {
      return props.globalFilter
    }
    return internalGlobalFilter.value
  },
  set: (value: string) => {
    if (props.globalFilter !== undefined) {
      emit('update:globalFilter', value)
    } else {
      internalGlobalFilter.value = value
    }
  },
})

const pageModel = computed({
  get: () => {
    if (props.page !== undefined) {
      return props.page
    }
    return internalPage.value
  },
  set: (value: number) => {
    if (props.page !== undefined) {
      emit('update:page', value)
    } else {
      internalPage.value = value
    }
  },
})

const pageSizeModel = computed({
  get: () => props.pageSize !== undefined ? props.pageSize : internalPageSize.value,
  set: (value: number) => {
    if (props.pageSize !== undefined) {
      emit('update:pageSize', value)
    } else {
      internalPageSize.value = value
    }
  },
})

const emit = defineEmits<{
  edit: [item: IGearItemV2]
  delete: [item: IGearItemV2]
  move: [item: IGearItemV2]
  statusChange: [item: IGearItemV2, status: IGearItemV2['status']]
  recognizeParameters: [item: IGearItemV2]
  reorder: [items: IGearItemV2[]]
  sortingChange: [items: IGearItemV2[]]
  update: [item: IGearItemV2]
  unlinkFromCatalogue: [item: IGearItemV2]
  'update:globalFilter': [filter: string]
  'update:page': [page: number]
  'update:pageSize': [pageSize: number]
}>()

const { t } = useI18n()
const router = useRouter()
const storeV2 = useGearStoreV2()
const { getChildren } = useGearV2()

const { settings: gearSettings, defaultCurrency } = useGearSettings()

// Nested containers are children with itemType='container'. The container detail page only
// loads the current container's direct children, so a nested container's own children
// (grandchildren) aren't in the store yet. Fetch them here so their contents and weight
// render in the expanded row. Skipped in public mode (different, unauthenticated data path).
watch(
  () => props.items,
  (items) => {
    if (props.publicMode) return
    for (const item of items) {
      if (item.itemType === 'container') {
        getChildren(item.id).catch(() => {
          // Best-effort prefetch; ignore failures (e.g. offline)
        })
      }
    }
  },
  { immediate: true, deep: false },
)
const { getCategoryLabel } = useCategoryLabel()
const { editMode } = useItemsTableEditMode()

const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Expanded rows state (which containers are expanded)
const expandedRows = ref<Set<string>>(new Set())

// Load column visibility from localStorage
function loadColumnVisibility(): Record<string, boolean> {
  try {
    const stored = localStorage.getItem(ITEMS_TABLE_COLUMN_VISIBILITY_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      // Validate that it's an object with boolean values
      if (typeof parsed === 'object' && parsed !== null) {
        return parsed
      }
    }
  } catch (error) {
    console.error('Error loading column visibility from storage:', error)
  }
  // Default: hide brand, color, wearable, and consumable by default
  return {
    image: false,
    brand: false,
    color: false,
    wearable: false,
    consumable: false,
    order: false,
    price: false,
  }
}

// Column visibility state - load from localStorage or use defaults
const columnVisibility = ref<Record<string, boolean>>(loadColumnVisibility())

// Debounced save function to reduce localStorage writes
const debouncedSaveColumnVisibility = useDebounceFn((value: Record<string, boolean>) => {
  try {
    localStorage.setItem(ITEMS_TABLE_COLUMN_VISIBILITY_KEY, JSON.stringify(value))
  } catch (error) {
    console.error('Error saving column visibility to storage:', error)
  }
}, 500)

// Save column visibility to localStorage when it changes (debounced)
watch(
  columnVisibility,
  (newValue) => {
    debouncedSaveColumnVisibility(newValue)
  },
  { deep: true },
)

// Columns
const columns = computed<ReturnType<typeof createItemsColumns>>(() => {
  return createItemsColumns(t)
})

// Custom filter function for searching
const globalFilterFn = (row: IGearItemV2, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    row.notes?.toLowerCase().includes(query) ||
    (row.category ? getCategoryLabel(row.category).toLowerCase().includes(query) : false) ||
    (row.status ? t(`gear.item.statuses.${row.status}`).toLowerCase().includes(query) : false)
  )
}

// Helper do sprawdzania czy przedmiot jest przeterminowany
function isExpired(item: IGearItemV2): boolean {
  if (!item.expirationDate) return false
  return new Date(item.expirationDate) < new Date()
}

// Helper to check if item is a nested container
function isNestedContainer(item: IGearItemV2): boolean {
  return item.itemType === 'container'
}

// Navigate to nested container
function navigateToNestedContainer(item: IGearItemV2) {
  if (item.itemType === 'container') {
    if (props.publicMode) {
      router.push(GearRoutePath.PublicContainerDetailById(item.id))
    } else {
      router.push(GearRoutePath.ContainerDetailById(item.id))
    }
  }
}

// Navigate to item detail page
function navigateToItem(item: IGearItemV2) {
  if (props.publicMode && props.containerId) {
    router.push(GearRoutePath.PublicItemDetailById(props.containerId, item.id))
  } else if (props.containerId) {
    // Only pass navigation params, router.back() will preserve search/pagination from browser history
    router.push({
      path: GearRoutePath.ItemDetailById(props.containerId, item.id),
      query: createNavigationQuery(undefined, 'container'),
    })
  } else {
    // Fallback: emit edit event if containerId is not available
    emit('edit', item)
  }
}

// Toggle row expansion
function toggleRowExpansion(itemId: string) {
  if (expandedRows.value.has(itemId)) {
    expandedRows.value.delete(itemId)
  } else {
    expandedRows.value.add(itemId)
  }
}

// Check if row is expanded
function isRowExpanded(itemId: string): boolean {
  return expandedRows.value.has(itemId)
}

// Get nested container items
function getNestedContainerItems(item: IGearItemV2): IGearItemV2[] {
  if (item.itemType !== 'container') return []
  return storeV2.getChildrenOfItem(item.id)
}

// Get nested container
function getNestedContainer(item: IGearItemV2) {
  if (item.itemType !== 'container') return undefined
  return item
}

// Calculate total weight for nested container (sync helper, V2)
function calculateTotalWeight(containerId: string): number {
  return calculateTotalWeightSyncV2(
    containerId,
    id => storeV2.getItemById(id),
    id => storeV2.getChildrenOfItem(id),
  )
}

// Sorting state from DataTable
const tableSorting = ref<SortingState>([])

// Sort items by order (default sorting) or by table sorting
// Using toSorted() instead of sort() to avoid mutating the array
const sortedItems = computed<IGearItemV2[]>(() => {
  const items = [...props.items]

  // If table has active sorting, apply it
  if (tableSorting.value.length > 0) {
    const sortConfig = tableSorting.value[0]
    if (!sortConfig) return items

    const columnId = sortConfig.id
    const direction = sortConfig.desc ? -1 : 1

    return items.toSorted((a, b) => {
      const aValue: unknown = a[columnId as keyof IGearItemV2]
      const bValue: unknown = b[columnId as keyof IGearItemV2]

      // Handle different data types
      const aVal = aValue === null || aValue === undefined ? '' : aValue
      const bVal = bValue === null || bValue === undefined ? '' : bValue

      // String comparison
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return aVal.localeCompare(bVal) * direction
      }

      // Number comparison
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return (aVal - bVal) * direction
      }

      // Fallback
      return String(aVal).localeCompare(String(bVal)) * direction
    })
  }

  // Default: Sort by orderIndex (null/undefined items go to end)
  return items.toSorted((a, b) => {
    const orderA = a.orderIndex ?? Number.MAX_SAFE_INTEGER
    const orderB = b.orderIndex ?? Number.MAX_SAFE_INTEGER
    return orderA - orderB
  })
})

// Track previous sorting to detect changes
const previousSorting = ref<SortingState>([])

// Watch for sorting changes and update local order
watch(
  tableSorting,
  (newSorting) => {
    // Check if sorting actually changed
    const sortingChanged = JSON.stringify(newSorting) !== JSON.stringify(previousSorting.value)
    previousSorting.value = [...newSorting]

    if (!sortingChanged) return

    // If sorting was cleared (back to default), emit empty array to clear pending changes
    if (newSorting.length === 0 && !props.publicMode) {
      emit('sortingChange', [])
      return
    }

    // Only emit if sorting is active (not default order sorting) and not in public mode
    if (newSorting.length > 0 && !props.publicMode) {
      // Get current sorted items based on new sorting
      const items = [...props.items]
      const sortConfig = newSorting[0]
      if (!sortConfig) return

      const columnId = sortConfig.id
      const direction = sortConfig.desc ? -1 : 1

      // Apply sorting (using toSorted to avoid mutating original array)
      const sorted = items.toSorted((a, b) => {
        const aValue: unknown = a[columnId as keyof IGearItemV2]
        const bValue: unknown = b[columnId as keyof IGearItemV2]

        const aVal = aValue === null || aValue === undefined ? '' : aValue
        const bVal = bValue === null || bValue === undefined ? '' : bValue

        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return aVal.localeCompare(bVal) * direction
        }

        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return (aVal - bVal) * direction
        }

        return String(aVal).localeCompare(String(bVal)) * direction
      })

      // Update order field based on current sorted order
      const updatedItems = sorted.map((item, index) => ({
        ...item,
        order: index,
      }))

      // Emit event for batch save (parent will handle saving)
      emit('sortingChange', updatedItems)
    }
  },
  { deep: true },
)

// Handle move up
function handleMoveUp(item: IGearItemV2) {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  if (currentIndex <= 0) return

  const reordered = [...sortedItems.value]
  const movedItem = reordered[currentIndex]
  if (!movedItem) return

  reordered.splice(currentIndex, 1)
  reordered.splice(currentIndex - 1, 0, movedItem)

  // Recalculate order values
  const updatedItems = reordered.map((item, index) => ({
    ...item,
    order: index,
  }))

  emit('reorder', updatedItems)
}

// Handle move down
function handleMoveDown(item: IGearItemV2) {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  if (currentIndex < 0 || currentIndex >= sortedItems.value.length - 1) return

  const reordered = [...sortedItems.value]
  const movedItem = reordered[currentIndex]
  if (!movedItem) return

  reordered.splice(currentIndex, 1)
  reordered.splice(currentIndex + 1, 0, movedItem)

  // Recalculate order values
  const updatedItems = reordered.map((item, index) => ({
    ...item,
    order: index,
  }))

  emit('reorder', updatedItems)
}

// Check if item can move up
function canMoveUp(item: IGearItemV2): boolean {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  return currentIndex > 0
}

// Check if item can move down
function canMoveDown(item: IGearItemV2): boolean {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  return currentIndex >= 0 && currentIndex < sortedItems.value.length - 1
}

// Track dirty state per row - Map<itemId, IUpdateGearItemV2Dto>
const dirtyChanges = ref<Map<string, IUpdateGearItemV2Dto>>(new Map())
const savingItems = ref<Set<TUUID>>(new Set())

// Handle cell change - accumulate changes per row
function handleCellChange(item: IGearItemV2, updates: IUpdateGearItemV2Dto, save?: boolean) {
  const itemId = item.id
  const currentChanges = dirtyChanges.value.get(itemId) ?? {}

  // Merge updates with existing changes
  const mergedChanges: IUpdateGearItemV2Dto = { ...currentChanges, ...updates }

  // Remove empty updates (no actual changes)
  const hasChanges = Object.keys(mergedChanges).some(key => {
    const value = mergedChanges[key as keyof IUpdateGearItemV2Dto]
    return value !== undefined && value !== null
  })

  if (hasChanges) {
    dirtyChanges.value.set(itemId, mergedChanges)
  } else {
    dirtyChanges.value.delete(itemId)
  }

  if (save && hasChanges) {
    handleSaveRow(item)
  }
}

// Check if row has dirty changes
function hasDirtyChanges(itemId: string): boolean {
  return dirtyChanges.value.has(itemId)
}

// Save all changes for a row
async function handleSaveRow(item: IGearItemV2) {
  const changes = dirtyChanges.value.get(item.id)
  if (!changes || Object.keys(changes).length === 0) return

  const { updateItem } = useGearV2()
  try {
    savingItems.value.add(item.id)
    const updated = await updateItem(item.id, changes)
    // Clear dirty state for this row
    dirtyChanges.value.delete(item.id)
    emit('update', updated)
    savingItems.value.delete(item.id)
  } catch (error) {
    console.error('Failed to save row changes:', error)
  } finally {
    savingItems.value.delete(item.id)
  }
}


// Handle upload photo - navigate to item detail page with image upload
function handleUploadPhoto(item: IGearItemV2) {
  if (!props.containerId) return
  router.push({
    path: GearRoutePath.ItemDetailById(props.containerId, item.id),
    query: createNavigationQuery(undefined, 'container'),
  })
}

// Handle star item - toggle priority between critical and medium
async function handleStarItem(item: IGearItemV2, newPriority: TGearItemPriority) {
  const { updateItem } = useGearV2()
  try {
    const updated = await updateItem(item.id, { priority: newPriority })
    emit('update', updated)
  } catch (error) {
    console.error('Failed to update item priority:', error)
  }
}
</script>

<template>
  <DataTable
    v-model:column-visibility="columnVisibility"
    v-model:sorting="tableSorting"
    v-model:global-filter="globalFilterModel"
    v-model:page="pageModel"
    v-model:page-size="pageSizeModel"
    :columns="columns"
    :data="sortedItems"
    :search-placeholder="t('gear.filters.search')"
    :global-filter-fn="globalFilterFn"
    :enable-sorting="true"
    :enable-filtering="true"
    :enable-pagination="true"
    :enable-column-visibility="true"
    :aria-label="t('gear.items.table.title', 'Items table')"
    :class="{ 'items-table-edit-mode': editMode && !publicMode }"
  >
    <template #name="{ row }">
      <ItemsTableEditableNameCell
        v-if="editMode && !publicMode"
        :item="row.original"
        :is-expired="isExpired(row.original)"
        :is-expiring-soon="isExpiringSoon(row.original)"
        :is-saving="savingItems.has(row.original.id)"
        :can-move-up="canMoveUp(row.original)"
        :can-move-down="canMoveDown(row.original)"
        @change="(updates, save) => handleCellChange(row.original, updates, save)"
        @move-up="handleMoveUp(row.original)"
        @move-down="handleMoveDown(row.original)"
      />
      <ItemsTableNameCell
        v-else
        :item="row.original"
        :public-mode="publicMode"
        :is-expired="isExpired(row.original)"
        :is-expiring-soon="isExpiringSoon(row.original)"
        :is-nested-container="isNestedContainer(row.original)"
        :is-row-expanded="isRowExpanded(row.original.id)"
        :can-move-up="canMoveUp(row.original)"
        :can-move-down="canMoveDown(row.original)"
        :nested-container="getNestedContainer(row.original)"
        @move-up="handleMoveUp(row.original)"
        @move-down="handleMoveDown(row.original)"
        @navigate="navigateToItem(row.original)"
        @navigate-to-nested-container="navigateToNestedContainer(row.original)"
        @toggle-expand="toggleRowExpansion(row.original.id)"
      />
    </template>

    <template #image="{ row }">
      <ItemsTableImageCell
        :item-id="row.original.id"
        :primary-image-url="row.original.primaryImageUrl"
        :container-id="containerId"
        :public-mode="publicMode"
      />
    </template>

    <template #category="{ row }">
      <ItemsTableEditableCategoryCell
        v-if="editMode && !publicMode"
        :item="row.original"
        @change="(updates) => handleCellChange(row.original, updates)"
      />
      <ItemsTableCategoryCell
        v-else-if="row.original.category"
        :category="row.original.category"
      />
    </template>

    <template #quantity="{ row }">
      <ItemsTableEditableQuantityCell
        v-if="editMode && !publicMode"
        :item="row.original"
        @change="(updates) => handleCellChange(row.original, updates)"
      />
      <span v-else>{{ row.original.quantity }}</span>
    </template>

    <template #weight="{ row }">
      <ItemsTableEditableWeightCell
        v-if="editMode && !publicMode && !isNestedContainer(row.original)"
        :item="row.original"
        @change="(updates) => handleCellChange(row.original, updates)"
      />
      <ItemsTableWeightCell
        v-else
        :item="row.original"
        :is-nested-container="isNestedContainer(row.original)"
        :total-weight="isNestedContainer(row.original) ? calculateTotalWeight(row.original.id) : undefined"
        :preferred-weight-unit="settings.preferredWeightUnit"
      />
    </template>

    <template #priority="{ row }">
      <ItemsTableEditablePriorityCell
        v-if="editMode && !publicMode"
        :item="row.original"
        @change="(updates) => handleCellChange(row.original, updates)"
      />
      <ItemPriorityBadge
        v-else-if="row.original.priority"
        :priority="row.original.priority"
      />
    </template>

    <template #status="{ row }">
      <ItemsTableEditableStatusCell
        v-if="editMode && !publicMode"
        :item="row.original"
        @change="(updates) => handleCellChange(row.original, updates)"
      />
      <ItemStatusBadge
        v-else-if="row.original.status"
        :status="row.original.status"
      />
    </template>

    <template #price="{ row }">
      <ItemsTableEditablePriceCell
        v-if="editMode && !publicMode"
        :item="row.original"
        @change="(updates) => handleCellChange(row.original, updates)"
      />
      <div v-else-if="row.original.price != null" class="text-end px-4">
        {{ formatItemPriceV2(row.original, false, defaultCurrency) }}
      </div>
      <span v-else class="text-muted-foreground">-</span>
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

    <template #actions="{ row }">
      <div v-if="!publicMode" class="flex items-center gap-2">
        <Button
          v-if="editMode"
          v-tooltip="t('gear.actions.save')"
          size="sm"
          :disabled="!hasDirtyChanges(row.original.id)"
          variant="ghost"
          class="size-8 p-0"
          :aria-label="t('gear.actions.save')"
          @click="handleSaveRow(row.original)"
        >
          <Check class="size-4" />
        </Button>
        <ItemsTableRowActions
          :row="row.original"
          @edit="emit('edit', row.original)"
          @delete="emit('delete', row.original)"
          @status-change="(status) => emit('statusChange', row.original, status)"
          @view-container="navigateToNestedContainer"
          @recognize-parameters="emit('recognizeParameters', row.original)"
          @upload-photo="handleUploadPhoto"
          @star-item="handleStarItem"
          @unlink-from-catalogue="emit('unlinkFromCatalogue', row.original)"
          @move="emit('move', row.original)"
        />
      </div>
    </template>

    <!-- Expanded content for nested containers (rendered after each row) -->
    <template #row-after="{ row }">
      <ItemsTableNestedContainerRow
        v-if="isNestedContainer(row.original) && isRowExpanded(row.original.id)"
        :nested-items="getNestedContainerItems(row.original)"
        :columns-length="columns.length"
        :container="getNestedContainer(row.original)"
      />
    </template>

    <template #empty>
      <TableEmptyDecorated
        :colspan="columns.length"
        :icon="Package"
        :title="t('gear.item.empty')"
        :description="t('gear.item.emptyDescription')"
      />
    </template>
  </DataTable>
</template>

<style scoped>
.items-table-edit-mode :deep([data-slot="table-cell"]) {
  padding: .5rem .5rem;
}
</style>

