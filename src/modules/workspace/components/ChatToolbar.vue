<script setup lang="ts">
import { ScrollText } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import WorkspaceModelSelector from '@/modules/workspace/components/WorkspaceModelSelector.vue'
import { useWorkspaceModels } from '@/modules/workspace/composables/useWorkspaceModels'
import type { IAgentRun } from '@/modules/workspace/types/agent'

const { activeRun, stepCount, auditOpen } = defineProps<{
  activeRun?: IAgentRun | null
  stepCount?: number
  auditOpen?: boolean
}>()

const emit = defineEmits<{
  openAudit: []
}>()

const { t } = useI18n()
const { selectedModel } = useWorkspaceModels()

const displayModelName = computed(() => activeRun?.model ?? selectedModel.value?.name ?? '—')

const auditDisabled = computed(() => !activeRun && (stepCount ?? 0) === 0)
</script>

<template>
  <div class="flex shrink-0 flex-wrap items-center justify-between gap-2">
    <div class="flex min-w-0 flex-wrap items-center gap-2">
      <WorkspaceModelSelector />
      <Badge variant="secondary" class="max-w-48 truncate">
        {{ t('workspace.model.current', { name: displayModelName }) }}
      </Badge>
    </div>

    <Button
      variant="outline"
      size="sm"
      :disabled="auditDisabled"
      :class="auditOpen ? 'bg-accent' : ''"
      @click="emit('openAudit')"
    >
      <ScrollText class="size-4" />
      {{ t('workspace.audit.open') }}
      <Badge
        v-if="(stepCount ?? 0) > 0"
        variant="outline"
        class="ml-1"
      >
        {{ stepCount }}
      </Badge>
    </Button>
  </div>
</template>
