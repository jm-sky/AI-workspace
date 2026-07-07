<script setup lang="ts">
import { Copy } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import type { IAgentStreamStepEvent } from '@/modules/workspace/types/agent'

const { steps, runId, isStreaming, expanded } = defineProps<{
  steps: IAgentStreamStepEvent[]
  runId?: string | null
  isStreaming?: boolean
  expanded?: boolean
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

const stepDetails = (step: IAgentStreamStepEvent): string | null => {
  if (step.type === 'tool_call' && step.arguments) {
    return JSON.stringify(step.arguments, null, 2)
  }
  if (step.type === 'tool_result' && step.result) {
    return JSON.stringify(step.result, null, 2)
  }
  return null
}

const hasSteps = computed(() => steps.length > 0)
const activeStepIndex = computed(() => (isStreaming ? steps.length - 1 : -1))
</script>

<template>
  <div v-if="hasSteps || runId" class="text-sm">
    <div
      v-if="!expanded"
      class="mb-2 flex items-center justify-between gap-2"
    >
      <span class="font-medium text-muted-foreground">
        {{ t('workspace.audit.title') }}
      </span>
      <Button
        v-if="runId"
        variant="outline"
        size="sm"
        @click="emit('copyRun')"
      >
        <Copy class="size-4" />
        {{ t('workspace.audit.copyRun') }}
      </Button>
    </div>
    <ol
      :class="[
        'space-y-2 font-mono text-xs',
        expanded ? '' : 'max-h-48 overflow-y-auto',
      ]"
    >
      <li
        v-for="(step, index) in steps"
        :key="index"
        :class="[
          'rounded-md border p-2',
          index === activeStepIndex ? 'border-primary/50 bg-primary/5' : 'border-transparent bg-muted/40',
        ]"
      >
        <div class="text-muted-foreground">
          {{ step.stepIndex ?? index }}. {{ stepLabel(step) }}
        </div>
        <pre
          v-if="expanded && stepDetails(step)"
          class="mt-2 max-h-48 overflow-auto whitespace-pre-wrap break-all text-[11px] text-foreground/80"
        >{{ stepDetails(step) }}</pre>
      </li>
    </ol>
  </div>
</template>
