<script setup lang="ts">
import { ChevronDown, ChevronUp } from 'lucide-vue-next'
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import { usePermissions } from '@/shared/composables/usePermissions'
import type { IAiChatMessage } from '../types'

const { isAdmin } = usePermissions()

const show = defineModel<boolean>('show', { default: false })

const { message, debugPrompt } = defineProps<{
  message: IAiChatMessage
  debugPrompt?: string | null
  withButton?: boolean
}>()

const shouldShowDebug = computed<boolean>(() => {
  return message.role === 'assistant' && isAdmin.value && debugPrompt !== null && debugPrompt !== undefined
})
</script>

<template>
  <div v-if="shouldShowDebug" :class="withButton ? 'mt-3 border-t pt-2' : ''">
    <Button
      v-if="withButton"
      variant="ghost"
      size="sm"
      class="text-xs h-auto py-1"
      @click="show = !show"
    >
      Debug: Full Prompt
      <ChevronDown v-if="!show" class="size-3" />
      <ChevronUp v-if="show" class="size-3" />
    </Button>

    <div v-if="show" class="border mt-2 px-2 py-1 bg-foreground/5 rounded text-xs font-mono whitespace-pre-wrap overflow-x-auto">
      {{ debugPrompt }}
    </div>
  </div>
</template>
