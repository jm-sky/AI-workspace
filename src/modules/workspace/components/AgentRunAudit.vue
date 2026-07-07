<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Copy } from 'lucide-vue-next'
import type { IAgentStreamStepEvent } from '@/modules/workspace/types/agent'

const { steps, runId } = defineProps<{
  steps: IAgentStreamStepEvent[]
  runId?: string | null
}>()

const emit = defineEmits<{
  copyRun: []
}>()

const { t } = useI18n()

const stepLabel = (step: IAgentStreamStepEvent): string => {
  if (step.type === 'tool_call') {
    return `${step.tool ?? 'tool'}(${JSON.stringify(step.arguments ?? {})})`
  }
  if (step.type === 'tool_result') {
    return `${step.tool ?? 'tool'} → ${JSON.stringify(step.result ?? {}).slice(0, 120)}`
  }
  if (step.type === 'model') {
    return `model (${step.finishReason ?? '…'})`
  }
  return step.type
}

const hasSteps = computed(() => steps.length > 0)
</script>

<template>
  <div v-if="hasSteps || runId" class="rounded-lg border bg-muted/30 p-3 text-sm">
    <div class="flex items-center justify-between gap-2 mb-2">
      <span class="font-medium text-muted-foreground">
        {{ t('workspace.audit.title', 'Run trace') }}
      </span>
      <Button
        v-if="runId"
        variant="outline"
        size="sm"
        @click="emit('copyRun')"
      >
        <Copy class="size-4" />
        {{ t('workspace.audit.copyRun', 'Copy run') }}
      </Button>
    </div>
    <ol class="space-y-1 font-mono text-xs max-h-48 overflow-y-auto">
      <li
        v-for="(step, index) in steps"
        :key="index"
        class="text-muted-foreground"
      >
        {{ step.stepIndex ?? index }}. {{ stepLabel(step) }}
      </li>
    </ol>
  </div>
</template>
