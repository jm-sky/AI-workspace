<script setup lang="ts">
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import { CheckCircle, Flag, XCircle } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { gearContainerApiService } from '../services/gearContainerApiService'
import ReportContentDialog from './ReportContentDialog.vue'

const props = defineProps<{
  containerId: string
}>()

const { t } = useI18n()
const queryClient = useQueryClient()
const { isAuthenticated } = useAuth()

const reportDialogOpen = ref<boolean>(false)

// Query to check if user has already reported this container
const { data: reportStatus } = useQuery({
  queryKey: ['report-status', props.containerId],
  queryFn: () => gearContainerApiService.getReportStatus(props.containerId),
  enabled: isAuthenticated,
  staleTime: 5 * 60 * 1000, // 5 minutes
})

const hasReported = computed<boolean>(() => reportStatus.value?.hasReported ?? false)

const tooltipText = computed<string>(() =>
  hasReported.value ? t('gear.report.clickToWithdraw') : t('gear.report.report')
)

const handleReportStatusChange = () => {
  queryClient.invalidateQueries({ queryKey: ['report-status', props.containerId] })
}
</script>

<template>
  <template v-if="isAuthenticated">
    <Button
      v-tooltip.bottom="tooltipText"
      variant="outline"
      size="sm"
      class="group"
      @click="reportDialogOpen = true"
    >
      <Flag class="size-4" />
      <span class="hidden sm:inline">{{ t('gear.report.report') }}</span>
      <CheckCircle v-if="hasReported" class="size-4 group-hover:hidden" />
      <XCircle v-if="hasReported" class="size-4 hidden group-hover:block" />
    </Button>

    <ReportContentDialog
      v-model:open="reportDialogOpen"
      :container-id="containerId"
      :has-reported="hasReported"
      @reported="handleReportStatusChange"
      @withdrawn="handleReportStatusChange"
    />
  </template>
</template>

