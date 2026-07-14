<script setup lang="ts">
import { Send } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

const input = defineModel<string>({ required: true })

const { isLoading, isStreaming, canSubmit = true } = defineProps<{
  isLoading?: boolean
  isStreaming?: boolean
  canSubmit?: boolean
}>()

const emit = defineEmits<{
  submit: []
}>()

const { t } = useI18n()

const handleSubmit = () => {
  if (!canSubmit) return
  emit('submit')
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <div class="sticky bottom-0 shrink-0 bg-gradient-to-t from-surface-canvas via-surface-canvas/95 to-transparent px-3 pb-4 pt-3 sm:px-4">
    <form
      class="shadow-composer mx-auto flex w-full max-w-3xl items-end gap-2 rounded-3xl border border-hairline bg-surface-raised/90 p-2 backdrop-blur-md transition-[box-shadow,border-color] focus-within:border-ring/40"
      @submit.prevent="handleSubmit"
    >
      <Textarea
        v-model="input"
        :placeholder="t('workspace.chat.placeholder')"
        :disabled="isLoading"
        rows="2"
        class="min-w-0 flex-1 resize-none border-0 bg-transparent shadow-none focus-visible:ring-0 dark:bg-transparent"
        :aria-label="t('workspace.chat.placeholder')"
        @keydown="handleKeydown"
      />
      <Button
        type="submit"
        class="shrink-0 rounded-xl"
        :loading="isStreaming"
        :disabled="isLoading || !input.trim() || !canSubmit"
      >
        <Send class="size-4" />
        <span class="hidden sm:inline">{{ t('workspace.chat.send') }}</span>
      </Button>
    </form>
  </div>
</template>
