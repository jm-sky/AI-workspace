<script setup lang="ts">
import { Package2, Trash2 } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { toast } from 'vue-sonner'
import DataTable from '@/components/data-table/DataTable.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IAdminItem } from '../types/admin.types'
import { adminApiService } from '../services/adminApiService'
import type { ColumnDef } from '@tanstack/vue-table'

const { t } = useI18n()
const { handleError } = useHandleError()
const items = ref<IAdminItem[]>([])
const loading = ref(false)

// Load items
async function loadItems() {
  loading.value = true
  try {
    items.value = await adminApiService.getItems(0, 1000)
  } catch (error) {
    console.error('Failed to load items:', error)
    handleError(error, { fallbackMessage: t('admin.items.loadError', 'Failed to load items') })
  } finally {
    loading.value = false
  }
}

// Delete item
async function deleteItem(itemId: string) {
  if (!confirm(t('admin.items.deleteConfirm', 'Are you sure you want to delete this item?'))) {
    return
  }

  try {
    await adminApiService.deleteItem(itemId)
    toast.success(t('admin.items.deleteSuccess', 'Item deleted successfully'))
    await loadItems()
  } catch (error) {
    console.error('Failed to delete item:', error)
    handleError(error, { fallbackMessage: t('admin.items.deleteError', 'Failed to delete item') })
  }
}

// Columns
const columns = computed<ColumnDef<IAdminItem>[]>(() => [
  {
    id: 'name',
    accessorKey: 'name',
    header: () => t('admin.items.columns.name', 'Name'),
    enableSorting: true,
  },
  {
    id: 'category',
    accessorKey: 'category',
    header: () => t('admin.items.columns.category', 'Category'),
    enableSorting: true,
  },
  {
    id: 'containerName',
    accessorKey: 'containerName',
    header: () => t('admin.items.columns.container', 'Container'),
    enableSorting: true,
  },
  {
    id: 'authorName',
    accessorKey: 'authorName',
    header: () => t('admin.items.columns.author', 'Author'),
    enableSorting: true,
  },
  {
    id: 'quantity',
    accessorKey: 'quantity',
    header: () => t('admin.items.columns.quantity', 'Quantity'),
    enableSorting: true,
  },
  {
    id: 'weight',
    accessorKey: 'weight',
    header: () => t('admin.items.columns.weight', 'Weight'),
    enableSorting: true,
  },
  {
    id: 'status',
    accessorKey: 'status',
    header: () => t('admin.items.columns.status', 'Status'),
    enableSorting: true,
  },
  {
    id: 'priority',
    accessorKey: 'priority',
    header: () => t('admin.items.columns.priority', 'Priority'),
    enableSorting: true,
  },
  {
    id: 'createdAt',
    accessorKey: 'createdAt',
    header: () => t('admin.items.columns.createdAt', 'Created'),
    enableSorting: true,
  },
  {
    id: 'actions',
    header: () => t('admin.items.columns.actions', 'Actions'),
    enableSorting: false,
    meta: {
      pinned: 'right',
    },
  },
])

// Global filter function
const globalFilterFn = (row: IAdminItem, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    row.category.toLowerCase().includes(query) ||
    (row.containerName?.toLowerCase().includes(query) ?? false) ||
    (row.authorName?.toLowerCase().includes(query) ?? false)
  )
}

onMounted(() => {
  loadItems()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <CommonPageHeader
        :icon="Package2"
        :label="t('admin.items.title', 'Items Management')"
        :description="t('admin.items.subtitle', 'View and manage all items')"
      />

      <!-- Table -->
      <DataTable
        :loading="loading"
        :columns="columns"
        :data="items"
        :search-placeholder="t('admin.items.search', 'Search items...')"
        :global-filter-fn="globalFilterFn"
        :enable-sorting="true"
        :enable-filtering="true"
        :enable-pagination="true"
        :initial-page-size="20"
      >
        <template #name="{ row }">
          <span class="font-medium">{{ row.original.name }}</span>
        </template>

        <template #category="{ row }">
          <span class="text-muted-foreground">{{ row.original.category }}</span>
        </template>

        <template #containerName="{ row }">
          <RouterLink
            v-if="row.original.containerName"
            :to="GearRoutePath.ContainerDetailById(row.original.containerId)"
            class="text-primary hover:underline"
          >
            {{ row.original.containerName }}
          </RouterLink>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #authorName="{ row }">
          <span v-if="row.original.authorName" class="text-muted-foreground">
            {{ row.original.authorName }}
          </span>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #quantity="{ row }">
          <span class="text-muted-foreground">{{ row.original.quantity }}</span>
        </template>

        <template #weight="{ row }">
          <span class="text-muted-foreground">
            {{ row.original.weight }} {{ row.original.weightUnit }}
          </span>
        </template>

        <template #status="{ row }">
          <Badge variant="outline">
            {{ row.original.status }}
          </Badge>
        </template>

        <template #priority="{ row }">
          <Badge variant="outline">
            {{ row.original.priority }}
          </Badge>
        </template>

        <template #createdAt="{ row }">
          <span class="text-sm text-muted-foreground">
            {{ new Date(row.original.createdAt).toLocaleDateString() }}
          </span>
        </template>

        <template #actions="{ row }">
          <Button
            variant="ghost"
            size="sm"
            class="text-destructive hover:text-destructive"
            @click="deleteItem(row.original.id)"
          >
            <Trash2 class="size-4" />
          </Button>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :colspan="columns.length"
            :title="t('admin.items.empty', 'No items found')"
            :description="t('admin.items.emptyDescription', 'No items match your search criteria.')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>
