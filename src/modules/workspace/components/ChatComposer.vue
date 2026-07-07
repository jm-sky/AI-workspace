<script setup lang="ts">
import { Send } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

const input = defineModel<string>({ required: true })

defineProps<{
  isLoading?: boolean
}>()

const emit = defineEmits<{
  submit: []
}>()

const { t } = useI18n()

const handleSubmit = () => {
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
  <div class="sticky bottom-0 shrink-0 border-t bg-background/95 p-3 backdrop-blur sm:p-4">
    <form class="flex items-end gap-2" @submit.prevent="handleSubmit">
      <Textarea
        v-model="input"
        :placeholder="t('workspace.chat.placeholder')"
        :disabled="isLoading"
        rows="2"
        class="min-w-0 flex-1 resize-none border bg-card shadow-sm"
        :aria-label="t('workspace.chat.placeholder')"
        @keydown="handleKeydown"
      />
      <Button
        type="submit"
        class="shrink-0"
        :disabled="isLoading || !input.trim()"
      >
        <Send class="size-4" />
        <span class="hidden sm:inline">{{ t('workspace.chat.send') }}</span>
      </Button>
    </form>
  </div>
</template>
