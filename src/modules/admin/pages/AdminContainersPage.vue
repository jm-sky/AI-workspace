<script setup lang="ts">
import { Package, Trash2 } from 'lucide-vue-next'
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
import type { IAdminContainer } from '../types/admin.types'
import { adminApiService } from '../services/adminApiService'
import type { ColumnDef } from '@tanstack/vue-table'

const { t } = useI18n()
const { handleError } = useHandleError()
const containers = ref<IAdminContainer[]>([])
const loading = ref(false)

// Load containers
async function loadContainers() {
  loading.value = true
  try {
    containers.value = await adminApiService.getContainers(0, 1000)
  } catch (error) {
    console.error('Failed to load containers:', error)
    handleError(error, { fallbackMessage: t('admin.containers.loadError', 'Failed to load containers') })
  } finally {
    loading.value = false
  }
}

// Delete container
async function deleteContainer(containerId: string) {
  if (!confirm(t('admin.containers.deleteConfirm', 'Are you sure you want to delete this container?'))) {
    return
  }

  try {
    await adminApiService.deleteContainer(containerId)
    toast.success(t('admin.containers.deleteSuccess', 'Container deleted successfully'))
    await loadContainers()
  } catch (error) {
    console.error('Failed to delete container:', error)
    handleError(error, { fallbackMessage: t('admin.containers.deleteError', 'Failed to delete container') })
  }
}

// Columns
const columns = computed<ColumnDef<IAdminContainer>[]>(() => [
  {
    id: 'name',
    accessorKey: 'name',
    header: () => t('admin.containers.columns.name', 'Name'),
    enableSorting: true,
  },
  {
    id: 'type',
    accessorKey: 'type',
    header: () => t('admin.containers.columns.type', 'Type'),
    enableSorting: true,
  },
  {
    id: 'authorName',
    accessorKey: 'authorName',
    header: () => t('admin.containers.columns.author', 'Author'),
    enableSorting: true,
  },
  {
    id: 'isPublic',
    accessorKey: 'isPublic',
    header: () => t('admin.containers.columns.isPublic', 'Public'),
    enableSorting: true,
  },
  {
    id: 'itemCount',
    accessorKey: 'itemCount',
    header: () => t('admin.containers.columns.itemCount', 'Items'),
    enableSorting: true,
  },
  {
    id: 'createdAt',
    accessorKey: 'createdAt',
    header: () => t('admin.containers.columns.createdAt', 'Created'),
    enableSorting: true,
  },
  {
    id: 'actions',
    header: () => t('admin.containers.columns.actions', 'Actions'),
    enableSorting: false,
    meta: {
      pinned: 'right',
    },
  },
])

// Global filter function
const globalFilterFn = (row: IAdminContainer, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    row.type.toLowerCase().includes(query) ||
    (row.authorName?.toLowerCase().includes(query) ?? false)
  )
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
        :icon="Package"
        :label="t('admin.containers.title', 'Containers Management')"
        :description="t('admin.containers.subtitle', 'View and manage all containers')"
      />

      <!-- Table -->
      <DataTable
        :loading="loading"
        :columns="columns"
        :data="containers"
        :search-placeholder="t('admin.containers.search', 'Search containers...')"
        :global-filter-fn="globalFilterFn"
        :enable-sorting="true"
        :enable-filtering="true"
        :enable-pagination="true"
        :initial-page-size="20"
      >
        <template #name="{ row }">
          <RouterLink
            :to="GearRoutePath.ContainerDetailById(row.original.id)"
            class="font-medium hover:text-primary hover:underline transition-colors"
          >
            {{ row.original.name }}
          </RouterLink>
        </template>

        <template #type="{ row }">
          <span class="text-muted-foreground">{{ row.original.type }}</span>
        </template>

        <template #authorName="{ row }">
          <span v-if="row.original.authorName" class="text-muted-foreground">
            {{ row.original.authorName }}
          </span>
          <span v-else class="text-muted-foreground">-</span>
        </template>

        <template #isPublic="{ row }">
          <Badge v-if="row.original.isPublic" variant="default">
            {{ t('admin.containers.public', 'Public') }}
          </Badge>
          <Badge v-else variant="secondary">
            {{ t('admin.containers.private', 'Private') }}
          </Badge>
        </template>

        <template #itemCount="{ row }">
          <span class="text-muted-foreground">{{ row.original.itemCount ?? 0 }}</span>
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
            @click="deleteContainer(row.original.id)"
          >
            <Trash2 class="size-4" />
          </Button>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :colspan="columns.length"
            :title="t('admin.containers.empty', 'No containers found')"
            :description="t('admin.containers.emptyDescription', 'No containers match your search criteria.')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>
