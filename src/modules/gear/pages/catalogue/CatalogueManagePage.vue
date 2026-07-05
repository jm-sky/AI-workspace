<script setup lang="ts">
import { BookIcon, CheckCircle2, Eye, MoreHorizontal, Plus, Trash2, XCircle } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import DataTable from '@/components/data-table/DataTable.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CategorySelect from '@/modules/gear/components/inputs/CategorySelect.vue'
import { useCatalogue } from '@/modules/gear/composables/catalogue/useCatalogue'
import { useCategoryLabel } from '@/modules/gear/composables/useCategoryLabel'
import { usePriceTierLabel } from '@/modules/gear/composables/usePriceTierLabel'
import { GearRoutePath } from '@/modules/gear/routes'
import { getActionIcon } from '@/modules/gear/utils/actionIcons'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePermissions } from '@/shared/composables/usePermissions'
import type { ColumnDef } from '@tanstack/vue-table'
import type { IGlobalCatalogueItem, TCataloguePriceTier } from '@/modules/gear/types/catalogue.types'
import type { TGearItemCategory, TGearItemQuality } from '@/modules/gear/types/gear.types'

const { t } = useI18n()
const { handleError } = useHandleError()
const { canAccessAdminPanel } = usePermissions()
const { getCategoryLabel } = useCategoryLabel()
const { getPriceTierLabel } = usePriceTierLabel()
const router = useRouter()

// Permission check
if (!canAccessAdminPanel.value) {
  // Redirect will be handled by router guard
}

const {
  catalogueItems,
  isLoadingItems,
  deleteCatalogueItem,
  updateCatalogueItem,
  updateSearchParams,
  clearFilters,
  refetchItems,
} = useCatalogue({ enableItemsQuery: true })

// Filter state
const searchQuery = ref('')
const selectedCategory = ref<TGearItemCategory | null>(null)
const selectedBrand = ref<string>('')
const selectedPriceTier = ref<TCataloguePriceTier | null>(null)
const selectedQuality = ref<TGearItemQuality | null>(null)
const selectedIsActive = ref<string>('all')

// Apply filters
const applyFilters = () => {
  updateSearchParams({
    query: searchQuery.value || null,
    category: selectedCategory.value,
    brand: selectedBrand.value || null,
    priceTier: selectedPriceTier.value,
    quality: selectedQuality.value,
    isActive: selectedIsActive.value === 'all' ? null : selectedIsActive.value === 'active',
    skip: 0,
    limit: 1000, // Load all for table
  })
}

// Initialize filters
onMounted(() => {
  applyFilters()
})

// Watch filters
watch([searchQuery, selectedCategory, selectedBrand, selectedPriceTier, selectedQuality, selectedIsActive], () => {
  applyFilters()
})

const EditIcon = getActionIcon('edit')

// View item
function handleView(item: IGlobalCatalogueItem) {
  router.push(GearRoutePath.CatalogueItemDetailById(item.id))
}

// Edit item
function handleEdit(item: IGlobalCatalogueItem) {
  router.push(GearRoutePath.CatalogueItemEditById(item.id))
}

// Toggle active status
async function handleToggleActive(item: IGlobalCatalogueItem) {
  try {
    await updateCatalogueItem(item.id, { isActive: !item.isActive })
    toast.success(t('common.success'))
    await refetchItems()
  } catch (error) {
    console.error('Failed to toggle active status:', error)
    handleError(error, { fallbackMessage: t('common.error') })
  }
}

// Delete item
async function handleDelete(item: IGlobalCatalogueItem) {
  if (!confirm(t('gear.catalogue.deleteConfirm'))) {
    return
  }

  try {
    await deleteCatalogueItem(item.id)
    toast.success(t('common.success'))
    await refetchItems()
  } catch (error) {
    console.error('Failed to delete catalogue item:', error)
    handleError(error, { fallbackMessage: t('common.error') })
  }
}

// Columns
const columns = computed<ColumnDef<IGlobalCatalogueItem>[]>(() => [
  {
    id: 'name',
    accessorKey: 'name',
    header: () => t('gear.item.name'),
    enableSorting: true,
  },
  {
    id: 'category',
    accessorKey: 'category',
    header: () => t('gear.item.category'),
    enableSorting: true,
  },
  {
    id: 'brand',
    accessorKey: 'brand',
    header: () => t('gear.item.brand'),
    enableSorting: true,
  },
  {
    id: 'model',
    accessorKey: 'model',
    header: () => t('gear.catalogue.model'),
    enableSorting: true,
  },
  {
    id: 'priceTier',
    accessorKey: 'priceTier',
    header: () => t('gear.catalogue.priceTier'),
    enableSorting: true,
  },
  {
    id: 'quality',
    accessorKey: 'quality',
    header: () => t('gear.catalogue.quality'),
    enableSorting: true,
  },
  {
    id: 'weight',
    accessorKey: 'weight',
    header: () => t('gear.item.weight'),
    enableSorting: true,
  },
  {
    id: 'isActive',
    accessorKey: 'isActive',
    header: () => t('gear.catalogue.isActive'),
    enableSorting: true,
  },
  {
    id: 'createdAt',
    accessorKey: 'createdAt',
    header: () => t('gear.catalogue.metadataCreated'),
    enableSorting: true,
  },
  {
    id: 'actions',
    header: () => t('gear.item.actions'),
    enableSorting: false,
    meta: {
      pinned: 'right',
    },
  },
])

// Global filter function for search
const globalFilterFn = (row: IGlobalCatalogueItem, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    (row.category?.toLowerCase().includes(query) ?? false) ||
    (row.brand?.toLowerCase().includes(query) ?? false) ||
    (row.model?.toLowerCase().includes(query) ?? false) ||
    (row.description?.toLowerCase().includes(query) ?? false)
  )
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <CommonPageHeader
        :icon="BookIcon"
        :label="t('gear.catalogue.title')"
        :description="t('gear.catalogue.subtitle')"
      >
        <template #top-actions>
          <RouterLink :to="GearRoutePath.CatalogueItemNew">
            <Button size="sm">
              <Plus class="size-4" />
              {{ t('gear.actions.add') }}
            </Button>
          </RouterLink>
        </template>
      </CommonPageHeader>

      <!-- Filters -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div class="space-y-1.5">
          <Label class="text-xs text-muted-foreground">
            {{ t('gear.catalogue.search') }}
          </Label>
          <Input
            v-model="searchQuery"
            :placeholder="t('gear.catalogue.searchPlaceholder')"
          />
        </div>
        <div class="space-y-1.5">
          <Label class="text-xs text-muted-foreground">
            {{ t('gear.catalogue.category') }}
          </Label>
          <CategorySelect
            v-model="selectedCategory"
            :nullable="true"
            :placeholder="t('gear.filters.all')"
          />
        </div>
        <div class="space-y-1.5">
          <Label class="text-xs text-muted-foreground">
            {{ t('gear.catalogue.brand') }}
          </Label>
          <Input
            v-model="selectedBrand"
            :placeholder="t('gear.filters.all')"
          />
        </div>
        <div class="space-y-1.5">
          <Label class="text-xs text-muted-foreground">
            {{ t('gear.catalogue.isActive') }}
          </Label>
          <Select v-model="selectedIsActive">
            <SelectTrigger>
              <SelectValue :placeholder="t('gear.filters.all')" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">
                {{ t('gear.filters.all') }}
              </SelectItem>
              <SelectItem value="active">
                {{ t('gear.catalogue.makeActive') }}
              </SelectItem>
              <SelectItem value="inactive">
                {{ t('gear.catalogue.makeInactive') }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div class="flex justify-end">
        <Button
          variant="outline"
          size="sm"
          @click="clearFilters(); searchQuery = ''; selectedCategory = null; selectedBrand = ''; selectedPriceTier = null; selectedQuality = null; selectedIsActive = 'all'; applyFilters()"
        >
          {{ t('gear.catalogue.clearFilters') }}
        </Button>
      </div>

      <!-- Table -->
      <DataTable
        :loading="isLoadingItems"
        :columns="columns"
        :data="catalogueItems"
        :search-placeholder="t('gear.catalogue.searchPlaceholder')"
        :global-filter-fn="globalFilterFn"
        :enable-sorting="true"
        :enable-filtering="true"
        :enable-pagination="true"
        :initial-page-size="20"
      >
        <template #name="{ row }">
          <RouterLink
            :to="GearRoutePath.CatalogueItemDetailById(row.original.id)"
            class="font-medium text-primary hover:underline"
          >
            {{ row.original.name }}
          </RouterLink>
        </template>

        <template #category="{ row }">
          <span class="text-muted-foreground">
            {{ getCategoryLabel(row.original.category) }}
          </span>
        </template>

        <template #brand="{ row }">
          <span v-if="row.original.brand" class="text-muted-foreground">
            {{ row.original.brand }}
          </span>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #model="{ row }">
          <span v-if="row.original.model" class="text-muted-foreground">
            {{ row.original.model }}
          </span>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #priceTier="{ row }">
          <span v-if="row.original.priceTier" class="text-muted-foreground">
            {{ getPriceTierLabel(row.original.priceTier) }}
          </span>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #quality="{ row }">
          <span v-if="row.original.quality" class="text-muted-foreground">
            {{ t(`gear.item.qualities.${row.original.quality}`) }}
          </span>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #weight="{ row }">
          <span class="text-muted-foreground">
            {{ row.original.weight }}{{ row.original.weightUnit }}
          </span>
        </template>

        <template #isActive="{ row }">
          <Badge :variant="row.original.isActive ? 'default' : 'secondary'">
            {{ row.original.isActive ? t('gear.catalogue.makeActive') : t('gear.catalogue.makeInactive') }}
          </Badge>
        </template>

        <template #createdAt="{ row }">
          <span class="text-sm text-muted-foreground">
            {{ new Date(row.original.createdAt).toLocaleDateString() }}
          </span>
        </template>

        <template #actions="{ row }">
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button
                v-tooltip.bottom="t('gear.actions.moreActions')"
                variant="ghost"
                class="size-8 p-0"
                :aria-label="t('gear.actions.moreActions')"
              >
                <MoreHorizontal class="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="handleView(row.original)">
                <Eye class="size-4 mr-2" />
                {{ t('gear.actions.show') }}
              </DropdownMenuItem>
              <DropdownMenuItem @click="handleEdit(row.original)">
                <EditIcon class="size-4 mr-2" />
                {{ t('gear.actions.edit') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleToggleActive(row.original)">
                <CheckCircle2 v-if="!row.original.isActive" class="size-4 mr-2" />
                <XCircle v-else class="size-4 mr-2" />
                {{ row.original.isActive ? t('gear.catalogue.makeInactive') : t('gear.catalogue.makeActive') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
                @click="handleDelete(row.original)"
              >
                <Trash2 class="size-4 mr-2" />
                {{ t('gear.actions.delete') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :colspan="columns.length"
            :title="t('gear.catalogue.empty')"
            :description="t('gear.catalogue.emptyDescription')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>
