<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { AlertTriangle, CheckCircle2, Clock, EyeOff, Flag, MoreHorizontal, XCircle } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { toast } from 'vue-sonner'
import DataTable from '@/components/data-table/DataTable.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import { useHandleError } from '@/shared/composables/useHandleError'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import { adminApiService } from '../services/adminApiService'
import type { ColumnDef } from '@tanstack/vue-table'
import type { IContentReport, ReportStatus } from '@/modules/gear/types/reports.types'

const { t } = useI18n()
const { handleError } = useHandleError()
const queryClient = useQueryClient()

const statusFilter = ref<ReportStatus | 'all'>('pending')
const limit = ref<number>(50)
const offset = ref<number>(0)

// TanStack Query for fetching reports
const { data: reportsData, isLoading: loading } = useQuery({
  queryKey: ['admin', 'reports', statusFilter, limit, offset],
  queryFn: () => adminApiService.getReports({
    status: statusFilter.value === 'all' ? undefined : statusFilter.value,
    limit: limit.value,
    offset: offset.value,
  }),
  staleTime: 30 * 1000, // 30 seconds
})

const reports = computed<IContentReport[]>(() => reportsData.value?.reports ?? [])

// Mutation for updating report status
const { mutateAsync: updateStatus } = useMutation({
  mutationFn: ({ reportId, status }: { reportId: string; status: ReportStatus }) =>
    adminApiService.updateReportStatus(reportId, { status }),
  onSuccess: () => {
    toast.success(t('admin.reports.updateSuccess', 'Report status updated'))
    queryClient.invalidateQueries({ queryKey: ['admin', 'reports'] })
  },
  onError: (error) => {
    handleError(error, { fallbackMessage: t('admin.reports.updateError', 'Failed to update report status') })
  },
})

// Update report status
async function updateReportStatus(reportId: string, newStatus: ReportStatus) {
  await updateStatus({ reportId, status: newStatus })
}

// Mutation for making container private
const { mutateAsync: makeContainerPrivate } = useMutation({
  mutationFn: (containerId: string) => adminApiService.updateContainer(containerId, { isPublic: false }),
  onSuccess: () => {
    toast.success(t('admin.reports.containerMadePrivate', 'Container made private'))
    queryClient.invalidateQueries({ queryKey: ['admin', 'reports'] })
  },
  onError: (error) => {
    handleError(error, { fallbackMessage: t('admin.reports.makePrivateError', 'Failed to make container private') })
  },
})

// Make container private
async function handleMakeContainerPrivate(containerId: string) {
  await makeContainerPrivate(containerId)
}

// Status badge variant mapping
const getStatusBadgeVariant = (status: ReportStatus): 'default' | 'secondary' | 'destructive' => {
  switch (status) {
    case 'action_taken':
      return 'destructive'
    case 'dismissed':
      return 'secondary'
    case 'pending':
      return 'default'
    case 'reviewed':
      return 'secondary'
    default:
      return 'secondary'
  }
}

// Status icon mapping
const getStatusIcon = (status: ReportStatus) => {
  switch (status) {
    case 'action_taken':
      return AlertTriangle
    case 'dismissed':
      return XCircle
    case 'pending':
      return Clock
    case 'reviewed':
      return CheckCircle2
    default:
      return Clock
  }
}

// Reason label mapping
const getReasonLabel = (reason: string): string => {
  return t(`gear.report.reasons.${reason}`, reason)
}

// Columns
const columns = computed<ColumnDef<IContentReport>[]>(() => [
  {
    id: 'containerId',
    accessorKey: 'containerId',
    header: () => t('admin.reports.columns.container', 'Container'),
    enableSorting: false,
  },
  {
    id: 'reporterUserId',
    accessorKey: 'reporterUserId',
    header: () => t('admin.reports.columns.reporter', 'Reporter'),
    enableSorting: false,
  },
  {
    id: 'reason',
    accessorKey: 'reason',
    header: () => t('admin.reports.columns.reason', 'Reason'),
    enableSorting: false,
  },
  {
    id: 'status',
    accessorKey: 'status',
    header: () => t('admin.reports.columns.status', 'Status'),
    enableSorting: false,
  },
  {
    id: 'createdAt',
    accessorKey: 'createdAt',
    header: () => t('admin.reports.columns.createdAt', 'Created'),
    enableSorting: false,
  },
  {
    id: 'actions',
    header: () => t('admin.reports.columns.actions', 'Actions'),
    enableSorting: false,
    meta: {
      pinned: 'right',
    },
  },
])

// Global filter function
function globalFilterFn(row: IContentReport, query: string): boolean {
  const q = query.toLowerCase()
  return (
    row.containerId.toLowerCase().includes(q)
    || (row.containerName?.toLowerCase().includes(q) ?? false)
    || row.reporterUserId.toLowerCase().includes(q)
    || (row.reporterName?.toLowerCase().includes(q) ?? false)
    || row.reason.toLowerCase().includes(q)
    || getReasonLabel(row.reason).toLowerCase().includes(q)
    || (row.additionalInfo?.toLowerCase().includes(q) ?? false)
  )
}

// Reset offset when status filter changes
watch(statusFilter, () => {
  offset.value = 0
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="w-full max-w-full space-y-6">
      <!-- Header -->
      <CommonPageHeader
        :icon="Flag"
        :label="t('admin.reports.title', 'Content Reports')"
        :description="t('admin.reports.subtitle', 'Review and manage content reports')"
      />

      <!-- Table -->
      <DataTable
        :loading="loading"
        :columns="columns"
        :data="reports"
        :search-placeholder="t('admin.reports.search', 'Search reports...')"
        :global-filter-fn="globalFilterFn"
        :enable-sorting="false"
        :enable-filtering="true"
        :enable-pagination="true"
        :initial-page-size="20"
      >
        <template #toolbar-filters>
          <div class="flex items-center gap-2">
            <Label class="text-sm font-medium whitespace-nowrap">
              {{ t('admin.reports.filterByStatus', 'Filter by status') }}
            </Label>
            <Select v-model="statusFilter">
              <SelectTrigger class="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">
                  {{ t('admin.reports.status.all', 'All') }}
                </SelectItem>
                <SelectItem value="pending">
                  {{ t('admin.reports.status.pending', 'Pending') }}
                </SelectItem>
                <SelectItem value="reviewed">
                  {{ t('admin.reports.status.reviewed', 'Reviewed') }}
                </SelectItem>
                <SelectItem value="dismissed">
                  {{ t('admin.reports.status.dismissed', 'Dismissed') }}
                </SelectItem>
                <SelectItem value="action_taken">
                  {{ t('admin.reports.status.action_taken', 'Action Taken') }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </template>

        <template #containerId="{ row }">
          <RouterLink
            :to="GearRoutePath.ContainerDetailById(row.original.containerId)"
            class="font-medium transition-colors hover:text-primary hover:underline"
            target="_blank"
          >
            {{ row.original.containerName || row.original.containerId }}
          </RouterLink>
        </template>

        <template #reporterUserId="{ row }">
          <span class="text-sm text-muted-foreground">
            {{ row.original.reporterName || row.original.reporterUserId }}
          </span>
        </template>

        <template #reason="{ row }">
          <div class="flex flex-col gap-1">
            <span class="font-medium">{{ getReasonLabel(row.original.reason) }}</span>
            <span v-if="row.original.additionalInfo" class="text-xs text-muted-foreground">
              {{ row.original.additionalInfo }}
            </span>
          </div>
        </template>

        <template #status="{ row }">
          <Badge :variant="getStatusBadgeVariant(row.original.status)">
            <component :is="getStatusIcon(row.original.status)" class="mr-1 size-3" />
            {{ t(`admin.reports.status.${row.original.status}`, row.original.status) }}
          </Badge>
        </template>

        <template #createdAt="{ row }">
          <span class="text-sm text-muted-foreground">
            {{ smallDateTime(row.original.createdAt) }}
          </span>
        </template>

        <template #actions="{ row }">
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="sm">
                <MoreHorizontal class="size-4" />
                <span class="sr-only">{{ t('admin.reports.actions', 'Actions') }}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                v-if="row.original.status !== 'reviewed'"
                @click="updateReportStatus(row.original.id, 'reviewed')"
              >
                <CheckCircle2 class="size-4" />
                {{ t('admin.reports.markReviewed', 'Mark as Reviewed') }}
              </DropdownMenuItem>
              <DropdownMenuItem
                v-if="row.original.status !== 'dismissed'"
                @click="updateReportStatus(row.original.id, 'dismissed')"
              >
                <XCircle class="size-4" />
                {{ t('admin.reports.markDismissed', 'Mark as Dismissed') }}
              </DropdownMenuItem>
              <DropdownMenuItem
                v-if="row.original.status !== 'action_taken'"
                @click="updateReportStatus(row.original.id, 'action_taken')"
              >
                <AlertTriangle class="size-4" />
                {{ t('admin.reports.markActionTaken', 'Mark as Action Taken') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                @click="handleMakeContainerPrivate(row.original.containerId)"
              >
                <EyeOff class="size-4" />
                {{ t('admin.reports.makeContainerPrivate', 'Make Container Private') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :icon="Flag"
            :title="t('admin.reports.empty', 'No reports found')"
            :description="t('admin.reports.emptyDescription', 'There are no content reports matching your filters.')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>
