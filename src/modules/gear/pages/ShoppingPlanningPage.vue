<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useDebounceFn } from '@vueuse/core'
import { Download, Plus, RotateCcw, ShoppingCart } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { computed, defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { config, SHOPPING_PLANNING_PAGE_FILTERS_KEY } from '@/shared/config/config'
import type { ICreateItemDto } from '../types/gear.types'
import type { TGearItemCategory, TGearItemPriority } from '../types/gear.types.v2'
import type { IItemWithContainerId } from '../types/shopping.types'
import AvailableItemCard from '../components/shopping/AvailableItemCard.vue'
import DeletedItemsList from '../components/shopping/DeletedItemsList.vue'
import ShoppingListFilters from '../components/shopping/ShoppingListFilters.vue'
import ShoppingListItem from '../components/shopping/ShoppingListItem.vue'
import ShoppingListSummary from '../components/shopping/ShoppingListSummary.vue'

// Lazy load dialogs - only loaded when user opens them
const AddItemToShoppingDialog = defineAsyncComponent(() => import('../components/shopping/AddItemToShoppingDialog.vue'))
const ShoppingExportDialog = defineAsyncComponent(() => import('../components/shopping/ShoppingExportDialog.vue'))
import type { IGearContainer } from '../types/gear.types'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { useGearMutations } from '../composables/useGearMutations'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearV2 } from '../composables/useGearV2'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { getDefaultItemValues } from '../utils/defaultValues'
import { isExpiringSoon } from '../utils/isExpiringSoon'
import { getReturnTo } from '../utils/navigationParams'
import { convertV2ContainerToV1, convertV2ItemToV1 } from '../utils/typeConverters'
import { type ItemFormData, itemSchema } from '../utils/validation'
import type { TUUID } from '@/shared/types/base.type'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const store = useGearStoreV2()
const { createItem, updateItem } = useGearMutations()
const { getItems } = useGearV2()
const { defaultCurrency } = useGearSettings()

// V1-shaped view (containers with nested items) built from the flat V2 store, so the
// existing shopping logic (which iterates container.items) and the V1-typed shopping
// components keep working unchanged.
const containers = computed<IGearContainer[]>(() =>
  store.getAllContainers.map(c => ({
    ...convertV2ContainerToV1(c),
    items: store.getChildrenOfItem(c.id).filter(i => i.itemType === 'item').map(convertV2ItemToV1),
  })),
)

// Load the full gear list into the V2 store
onMounted(() => {
  getItems().catch(() => {})
})
const { getCategoryLabel } = useCategoryLabel()

// Filters
const selectedCategories = ref<TGearItemCategory[]>([])
const budget = ref<number | null>(null)
const includeExpiringSoon = ref(true)
const itemsBeingPurchased = ref<Set<TUUID>>(new Set<TUUID>())

// Storage keys
const SHOPPING_LIST_STORAGE_KEY = `${config.app.id}:shopping-list`
const DELETED_ITEMS_STORAGE_KEY = `${config.app.id}:shopping-deleted-items`

// Helper to load filters from localStorage
interface FiltersState {
  selectedCategories: TGearItemCategory[]
  budget: number | null
  includeExpiringSoon: boolean
}

function loadFiltersFromStorage(): FiltersState | null {
  const stored = localStorage.getItem(SHOPPING_PLANNING_PAGE_FILTERS_KEY)
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
      selectedCategories: selectedCategories.value,
      budget: budget.value,
      includeExpiringSoon: includeExpiringSoon.value,
    }
    localStorage.setItem(SHOPPING_PLANNING_PAGE_FILTERS_KEY, JSON.stringify(filters))
  } catch (error) {
    console.error('Error saving filters to storage:', error)
  }
}

// Load filters from storage on mount
const savedFilters = loadFiltersFromStorage()
if (savedFilters) {
  selectedCategories.value = savedFilters.selectedCategories
  budget.value = savedFilters.budget
  includeExpiringSoon.value = savedFilters.includeExpiringSoon
}

// Watch filters and save to localStorage
watch([selectedCategories, budget, includeExpiringSoon], () => {
  saveFiltersToStorage()
}, { deep: true })

// Helper to load shopping list from localStorage
function loadShoppingListFromStorage(): IItemWithContainerId[] {
  const stored = localStorage.getItem(SHOPPING_LIST_STORAGE_KEY)
  if (stored) {
    try {
      return JSON.parse(stored) as IItemWithContainerId[]
    } catch (error) {
      console.error('Error loading shopping list from storage:', error)
    }
  }
  return []
}

// Helper to save shopping list to localStorage
function saveShoppingListToStorage(list: IItemWithContainerId[]): void {
  try {
    localStorage.setItem(SHOPPING_LIST_STORAGE_KEY, JSON.stringify(list))
  } catch (error) {
    console.error('Error saving shopping list to storage:', error)
  }
}

// Helper to load deleted items from localStorage
function loadDeletedItemsFromStorage(): IItemWithContainerId[] {
  const stored = localStorage.getItem(DELETED_ITEMS_STORAGE_KEY)
  if (stored) {
    try {
      return JSON.parse(stored) as IItemWithContainerId[]
    } catch (error) {
      console.error('Error loading deleted items from storage:', error)
    }
  }
  return []
}

// Helper to save deleted items to localStorage
function saveDeletedItemsToStorage(items: IItemWithContainerId[]): void {
  try {
    localStorage.setItem(DELETED_ITEMS_STORAGE_KEY, JSON.stringify(items))
  } catch (error) {
    console.error('Error saving deleted items to storage:', error)
  }
}

// Shopping list (items selected for shopping)
const shoppingList = ref<IItemWithContainerId[]>(loadShoppingListFromStorage())

// Deleted items (local to this page)
const deletedItems = ref<IItemWithContainerId[]>(loadDeletedItemsFromStorage())

// Debounced save functions to reduce localStorage writes
const debouncedSaveShoppingList = useDebounceFn((list: IItemWithContainerId[]) => {
  saveShoppingListToStorage(list)
}, 500)

const debouncedSaveDeletedItems = useDebounceFn((items: IItemWithContainerId[]) => {
  saveDeletedItemsToStorage(items)
}, 500)

// Watch shopping list changes and save to localStorage (debounced)
watch(shoppingList, (newList) => {
  debouncedSaveShoppingList(newList)
}, { deep: true })

// Watch deleted items changes and save to localStorage (debounced)
watch(deletedItems, (newItems) => {
  debouncedSaveDeletedItems(newItems)
}, { deep: true })

// Get available items (toBuy + optionally expiring soon/expired) with container IDs
const availableItems = computed<IItemWithContainerId[]>(() => {
  const items: IItemWithContainerId[] = []

  containers.value.forEach(container => {
    container.items.forEach(item => {
      // Include items with status "toBuy"
      if (item.status === 'toBuy') {
        items.push({ ...item, _containerId: container.id })
      }
      // Optionally include items expiring soon or expired
      else if (includeExpiringSoon.value && isExpiringSoon(item)) {
        items.push({ ...item, _containerId: container.id })
      }
    })
  })

  return items
})

// Get all available categories
const allCategories = computed<TGearItemCategory[]>(() => {
  const categories = new Set<TGearItemCategory>()
  availableItems.value.forEach(item => {
    categories.add(item.category)
  })
  return Array.from(categories).sort()
})

// Priority order for sorting
const priorityOrder: Record<TGearItemPriority, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
}

// Filtered and sorted items
const filteredItems = computed<IItemWithContainerId[]>(() => {
  let items = [...availableItems.value]

  // Filter by categories
  if (selectedCategories.value.length > 0) {
    items = items.filter(item => selectedCategories.value.includes(item.category))
  }

  // Filter by budget (if set)
  if (budget.value !== null && budget.value > 0) {
    items = items.filter(item => {
      const itemPrice = item.price ?? 0
      const totalPrice = itemPrice * item.quantity
      return totalPrice <= budget.value!
    })
  }

  // Sort by priority (using toSorted to avoid mutating the array)
  return items.toSorted((a, b) => {
    return priorityOrder[a.priority] - priorityOrder[b.priority]
  })
})

// Calculate total price for shopping list (per currency)
const totalPriceByCurrency = computed(() => {
  const totals: Record<string, number> = {}
  const defaultCurr = defaultCurrency.value
  shoppingList.value.forEach(item => {
    if (item.price != null && item.price > 0) {
      const currency = item.currency ?? defaultCurr
      const totalPrice = item.price * item.quantity
      totals[currency] = (totals[currency] || 0) + totalPrice
    }
  })
  return totals
})

// Check if item is in shopping list
const isInShoppingList = (item: IItemWithContainerId): boolean => {
  return shoppingList.value.some(i => i.id === item.id)
}

// Add item to shopping list
const addToShoppingList = (item: IItemWithContainerId) => {
  if (!isInShoppingList(item)) {
    shoppingList.value.push(item)
    toast.success(t('gear.shopping.addedToCart', 'Added to shopping list'))
  }
}

// Remove item from shopping list
const removeFromShoppingList = (item: IItemWithContainerId) => {
  const index = shoppingList.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    shoppingList.value.splice(index, 1)
    toast.success(t('gear.shopping.removedFromCart', 'Removed from shopping list'))
  }
}

// Toggle item in shopping list
const toggleShoppingList = (item: IItemWithContainerId) => {
  if (isInShoppingList(item)) {
    removeFromShoppingList(item)
  } else {
    addToShoppingList(item)
  }
}

// Mark item as purchased (change status to Owned and remove from list)
const markAsPurchased = async (item: IItemWithContainerId) => {
  try {
    itemsBeingPurchased.value.add(item.id)
    await updateItem(item.id, { status: 'owned' })
    itemsBeingPurchased.value.delete(item.id)
    removeFromShoppingList(item)
    toast.success(t('gear.shopping.markedAsPurchased', 'Item marked as purchased'))
  } catch (error) {
    console.error('Failed to mark item as purchased:', error)
    toast.error(t('common.error', 'Error'))
  } finally {
    itemsBeingPurchased.value.delete(item.id)
  }
}

// Update item quantity in shopping list
const updateShoppingListItemQuantity = (item: IItemWithContainerId, newQuantity: number) => {
  if (newQuantity < 1) return
  const index = shoppingList.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    const existingItem = shoppingList.value[index]
    shoppingList.value[index] = { ...existingItem, quantity: newQuantity } as IItemWithContainerId
  }
}

// Increment quantity
const incrementQuantity = (item: IItemWithContainerId) => {
  updateShoppingListItemQuantity(item, item.quantity + 1)
}

// Decrement quantity
const decrementQuantity = (item: IItemWithContainerId) => {
  if (item.quantity > 1) {
    updateShoppingListItemQuantity(item, item.quantity - 1)
  }
}

// Delete item from shopping list (move to deleted section)
const deleteFromShoppingList = (item: IItemWithContainerId) => {
  const index = shoppingList.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    shoppingList.value.splice(index, 1)
    deletedItems.value.push(item)
    toast.success(t('gear.shopping.deletedFromList', 'Item removed from shopping list'))
  }
}

// Restore item from deleted section
const restoreToShoppingList = (item: IItemWithContainerId) => {
  const index = deletedItems.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    deletedItems.value.splice(index, 1)
    if (!isInShoppingList(item)) {
      shoppingList.value.push(item)
      toast.success(t('gear.shopping.restoredToList', 'Item restored to shopping list'))
    }
  }
}

// Reset shopping list (reload from available items)
const resetShoppingList = () => {
  shoppingList.value = []
  deletedItems.value = []
  saveShoppingListToStorage([])
  saveDeletedItemsToStorage([])
  toast.success(t('gear.shopping.listReset', 'Shopping list reset'))
}

// Add all filtered items to shopping list
const addAllToShoppingList = () => {
  let addedCount = 0
  filteredItems.value.forEach(item => {
    if (!isInShoppingList(item)) {
      shoppingList.value.push(item)
      addedCount++
    }
  })
  if (addedCount > 0) {
    toast.success(t('gear.shopping.addedAllToCart', { count: addedCount }))
  } else {
    toast.info(t('gear.shopping.allItemsAlreadyInList'))
  }
}

// Generate markdown export (only from shopping list, respecting filters)
const generateMarkdown = (): string => {
  // Filter shopping list items by current filters
  let itemsToExport = [...shoppingList.value]

  // Apply category filter
  if (selectedCategories.value.length > 0) {
    itemsToExport = itemsToExport.filter(item => selectedCategories.value.includes(item.category))
  }

  // Apply budget filter
  if (budget.value !== null && budget.value > 0) {
    itemsToExport = itemsToExport.filter(item => {
      const itemPrice = item.price ?? 0
      const totalPrice = itemPrice * item.quantity
      return totalPrice <= budget.value!
    })
  }

  if (itemsToExport.length === 0) {
    return t('gear.shopping.emptyList', 'Shopping list is empty')
  }

  let markdown = `# ${t('gear.shopping.title', 'Shopping List')}\n\n`
  markdown += `${t('gear.shopping.generatedAt', 'Generated at')}: ${new Date().toLocaleString()}\n\n`

  // Group by priority
  const byPriority: Record<TGearItemPriority, IItemWithContainerId[]> = {
    critical: [],
    high: [],
    medium: [],
    low: [],
  }

  itemsToExport.forEach(item => {
    byPriority[item.priority].push(item)
  })

  // Output by priority
  Object.entries(byPriority).forEach(([priority, items]) => {
    if (items.length > 0) {
      markdown += `## ${t(`gear.item.priorities.${priority}`)}\n\n`
      items.forEach(item => {
        const categoryLabel = getCategoryLabel(item.category ?? 'other')
        const currency = item.currency ?? defaultCurrency.value
        const price = item.price ? ` - ${item.price.toFixed(2)} ${currency}` : ''
        const quantity = (item.quantity ?? 1) > 1 ? ` x${item.quantity}` : ''
        const brand = item.brand ? ` **${item.brand}**` : ''
        const expiration = item.expirationDate ? ` (${t('gear.item.expiration.expiringSoon')}: ${new Date(item.expirationDate).toLocaleDateString()})` : ''

        markdown += `- ${item.name}${brand}${quantity}${price}${expiration} [${categoryLabel}]\n`
      })
      markdown += '\n'
    }
  })

  // Calculate total price per currency
  const exportTotalPriceByCurrency: Record<string, number> = {}
  itemsToExport.forEach(item => {
    if (item.price != null && item.price > 0) {
      const currency = item.currency ?? defaultCurrency.value
      const totalPrice = item.price * item.quantity
      exportTotalPriceByCurrency[currency] = (exportTotalPriceByCurrency[currency] || 0) + totalPrice
    }
  })

  if (Object.keys(exportTotalPriceByCurrency).length > 0) {
    markdown += `\n**${t('gear.shopping.totalPrice', 'Total')}**:\n`
    Object.entries(exportTotalPriceByCurrency).forEach(([currency, amount]) => {
      markdown += `- ${amount.toFixed(2)} ${currency}\n`
    })
  }

  return markdown
}

// Export dialog
const exportDialogOpen = ref(false)
const markdownContent = computed(() => generateMarkdown())

const handleCopyMarkdown = async () => {
  try {
    await navigator.clipboard.writeText(markdownContent.value)
    toast.success(t('gear.shopping.markdownCopied', 'Markdown copied to clipboard'))
    exportDialogOpen.value = false
  } catch (error) {
    console.error('Failed to copy markdown:', error)
    toast.error(t('gear.shopping.copyFailed', 'Failed to copy markdown'))
  }
}

// Add new item dialog
const addItemDialogOpen = ref(false)
const firstContainerId = computed(() => containers.value[0]?.id)

const getInitialAddItemValues = (): ItemFormData => {
  return {
    ...getDefaultItemValues(),
    status: 'toBuy', // Default to "To Buy" status
  } as ItemFormData
}

const addItemForm = useForm({
  validationSchema: toTypedSchema(itemSchema),
  initialValues: getInitialAddItemValues(),
})

const { handleSubmit: handleAddItemSubmit, isSubmitting: isAddingItem, resetForm: resetAddItemForm } = addItemForm

const onAddItemSubmit = handleAddItemSubmit(async (data: ItemFormData) => {
  if (!firstContainerId.value) {
    toast.error(t('gear.shopping.noContainer', 'No container available'))
    return
  }

  try {
    // Convert form data to DTO (omit form-only shelfLifeValue/shelfLifeUnit, add shelfLife)
    const { shelfLifeValue, shelfLifeUnit, ...rest } = data
    const dtoData: ICreateItemDto = {
      ...rest,
      shelfLife:
        shelfLifeValue && shelfLifeUnit
          ? { value: shelfLifeValue, unit: shelfLifeUnit }
          : null,
    }

    // Drop the V1-only nested containerId; V2 hierarchy is parentItemId
    const { containerId: _nestedContainerId, ...itemFields } = dtoData
    const newItem = await createItem({
      ...itemFields,
      itemType: 'item',
      parentItemId: firstContainerId.value,
    })
    // Add to shopping list (convert back to the V1 shape the shopping components use)
    const itemWithContainer: IItemWithContainerId = { ...convertV2ItemToV1(newItem), _containerId: firstContainerId.value }
    addToShoppingList(itemWithContainer)
    addItemDialogOpen.value = false
    resetAddItemForm({ values: getInitialAddItemValues() })
    toast.success(t('gear.shopping.itemAdded', 'Item added'))
  } catch (error) {
    console.error('Failed to add item:', error)
    toast.error(t('common.error', 'Error'))
  }
})

const handleCancelAddItem = () => {
  addItemDialogOpen.value = false
  resetAddItemForm({ values: getInitialAddItemValues() })
}

// Sync shopping list with current container data
// This ensures items in shopping list are up-to-date with container data
function syncShoppingListWithContainers() {
  const updatedList: IItemWithContainerId[] = []

  shoppingList.value.forEach(shoppingItem => {
    // Find the item in current containers
    let found = false
    containers.value.forEach(container => {
      const currentItem = container.items.find(item => item.id === shoppingItem.id)
      if (currentItem) {
        // Update item with current data
        updatedList.push({ ...currentItem, _containerId: container.id })
        found = true
      }
    })

    // If item not found in containers, it might have been deleted
    // We keep it in the list for now, but it will be filtered out
    if (!found) {
      updatedList.push(shoppingItem)
    }
  })

  shoppingList.value = updatedList
}

// Sync deleted items with current container data
function syncDeletedItemsWithContainers() {
  const updatedDeleted: IItemWithContainerId[] = []

  deletedItems.value.forEach(deletedItem => {
    // Find the item in current containers
    let found = false
    containers.value.forEach(container => {
      const currentItem = container.items.find(item => item.id === deletedItem.id)
      if (currentItem) {
        // Update item with current data
        updatedDeleted.push({ ...currentItem, _containerId: container.id })
        found = true
      }
    })

    // If item not found, keep it as is
    if (!found) {
      updatedDeleted.push(deletedItem)
    }
  })

  deletedItems.value = updatedDeleted
}

// Watch containers changes and sync shopping list
// Track only item IDs instead of deep watching to reduce reactivity overhead
watch(() => {
  // Create a string of all item IDs from all containers
  // This will change when items are added/removed, but won't trigger on property changes
  return containers.value
    .flatMap(container => container.items.map(item => item.id))
    .join(',')
}, () => {
  syncShoppingListWithContainers()
  syncDeletedItemsWithContainers()
})

// Handle redirect from edit page
onMounted(() => {
  const returnTo = getReturnTo(route)
  if (returnTo === 'shopping') {
    // Clear the query param
    router.replace({ query: {} })
  }

  // Sync shopping list with current container data on mount
  syncShoppingListWithContainers()
  syncDeletedItemsWithContainers()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <CommonPageHeader
        :icon="ShoppingCart"
        :label="t('gear.shopping.title', 'Shopping Planning')"
        :description="t('gear.shopping.subtitle', 'Plan your purchases for items to buy and expiring soon')"
      >
        <template #actions>
          <Button
            variant="default"
            @click="addItemDialogOpen = true"
          >
            <Plus class="size-4" />
            {{ t('gear.shopping.addItem', 'Add') }}
          </Button>
          <Button
            v-if="shoppingList.length > 0"
            variant="outline"
            @click="exportDialogOpen = true"
          >
            <Download class="size-4" />
            {{ t('gear.shopping.exportMarkdown', 'Export Markdown') }}
          </Button>
          <Button
            variant="outline"
            @click="resetShoppingList"
          >
            <RotateCcw class="size-4" />
            {{ t('gear.shopping.reset', 'Reset') }}
          </Button>
        </template>
      </CommonPageHeader>

      <!-- Summary above list -->
      <ShoppingListSummary
        :shopping-list="shoppingList"
        :total-price-by-currency="totalPriceByCurrency"
      />

      <!-- Filters -->
      <ShoppingListFilters
        :all-categories="allCategories"
        :selected-categories="selectedCategories"
        :budget="budget"
        :include-expiring-soon="includeExpiringSoon"
        :default-currency="defaultCurrency"
        @update:selected-categories="selectedCategories = $event"
        @update:budget="budget = $event"
        @update:include-expiring-soon="includeExpiringSoon = $event"
      />

      <!-- Shopping list section -->
      <div
        v-if="shoppingList.length > 0"
        class="space-y-4"
      >
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">
            {{ t('gear.shopping.shoppingList', 'Shopping List') }}
          </h2>
          <Button
            variant="outline"
            size="sm"
            @click="shoppingList = []"
          >
            {{ t('gear.shopping.clearList', 'Clear List') }}
          </Button>
        </div>

        <div class="space-y-2">
          <ShoppingListItem
            v-for="item in shoppingList"
            :key="item.id"
            v-memo="[item.id, item.quantity, itemsBeingPurchased.has(item.id)]"
            :item="item"
            :is-being-purchased="itemsBeingPurchased.has(item.id)"
            @purchase="markAsPurchased(item)"
            @increment="incrementQuantity(item)"
            @decrement="decrementQuantity(item)"
            @delete="deleteFromShoppingList(item)"
          />
        </div>
      </div>

      <!-- Available items list -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">
            {{ t('gear.shopping.availableItems', 'Available Items') }}
          </h2>
          <Button
            v-if="filteredItems.length > 0"
            variant="outline"
            size="sm"
            @click="addAllToShoppingList"
          >
            <Plus class="size-4" />
            {{ t('gear.shopping.addAll', 'Add All') }}
          </Button>
        </div>

        <div class="space-y-2">
          <div
            v-if="filteredItems.length === 0"
            class="text-center py-12 text-muted-foreground"
          >
            <p class="text-lg">
              {{ t('gear.shopping.noItems', 'No items found') }}
            </p>
            <p class="text-sm mt-2">
              {{ t('gear.shopping.noItemsDescription', 'Try adjusting your filters') }}
            </p>
          </div>

          <AvailableItemCard
            v-for="item in filteredItems"
            :key="item.id"
            v-memo="[item.id, item.status, item.priority, isInShoppingList(item), itemsBeingPurchased.has(item.id)]"
            :item="item"
            :is-in-shopping-list="isInShoppingList(item)"
            :is-being-purchased="itemsBeingPurchased.has(item.id)"
            @toggle="toggleShoppingList(item)"
            @purchase="markAsPurchased(item)"
          />
        </div>
      </div>

      <!-- Summary below list -->
      <ShoppingListSummary
        :shopping-list="shoppingList"
        :total-price-by-currency="totalPriceByCurrency"
      />

      <!-- Deleted items section -->
      <DeletedItemsList
        :deleted-items="deletedItems"
        @restore="restoreToShoppingList"
      />

      <!-- Export Dialog -->
      <ShoppingExportDialog
        v-model:open="exportDialogOpen"
        :markdown-content="markdownContent"
        @copy="handleCopyMarkdown"
      />

      <!-- Add Item Dialog -->
      <AddItemToShoppingDialog
        v-model:open="addItemDialogOpen"
        :loading="isAddingItem"
        @submit="onAddItemSubmit"
        @cancel="handleCancelAddItem"
      />
    </div>
  </AuthenticatedLayout>
</template>
