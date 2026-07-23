<script setup lang="ts">
import { toRef } from 'vue'
import { useThinkingStatus } from '@/modules/workspace/composables/useThinkingStatus'
import type { IAgentStreamStepEvent } from '@/modules/workspace/types/agent'

const props = defineProps<{
  steps: IAgentStreamStepEvent[]
  isActive?: boolean
}>()

const { statusLabel } = useThinkingStatus(
  toRef(props, 'steps'),
  toRef(() => props.isActive ?? true),
)
</script>

<template>
  <div class="mr-auto flex max-w-[85%] items-center gap-3 rounded-2xl border border-hairline bg-surface-raised/70 px-3 py-2.5 shadow-soft backdrop-blur-sm">
    <div class="flex items-center gap-1" aria-hidden="true">
      <span
        class="size-2 rounded-full bg-muted-foreground/70 animate-bounce"
        style="animation-delay: 0ms"
      />
      <span
        class="size-2 rounded-full bg-muted-foreground/70 animate-bounce"
        style="animation-delay: 150ms"
      />
      <span
        class="size-2 rounded-full bg-muted-foreground/70 animate-bounce"
        style="animation-delay: 300ms"
      />
    </div>
    <span class="text-sm text-muted-foreground">{{ statusLabel }}</span>
  </div>
</template>
