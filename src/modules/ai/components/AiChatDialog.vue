<!--
  AI Chat Dialog Component
  Dialog wrapper for AI chat interface
-->
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Dialog, DialogContent, DialogDescription } from '@/components/ui/dialog'
import AiChatWindow from './AiChatWindow.vue'

const { t } = useI18n()

const props = defineProps<{
  open: boolean
  context?: {
    container_ids?: string[]
    fields?: string[]
  }
  restoreHistoryId?: string | null
}>()

const emits = defineEmits<{
  'update:open': [value: boolean]
}>()

const handleOpenChange = (value: boolean): void => {
  emits('update:open', value)
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleOpenChange">
    <DialogContent
      class="sm:max-w-4xl h-[85vh] flex flex-col p-0"
      :show-close-button="false"
    >
      <DialogDescription class="sr-only">
        {{ t('ai.chat.description') }}
      </DialogDescription>
      <AiChatWindow
        :container-ids="props.context?.container_ids"
        :restore-history-id="props.restoreHistoryId"
        @close="handleOpenChange(false)"
      />
    </DialogContent>
  </Dialog>
</template>

