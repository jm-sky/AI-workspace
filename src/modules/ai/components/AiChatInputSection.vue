<script setup lang="ts">
import { SendIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import AiIncludeContainerDataButton from './AiIncludeContainerDataButton.vue'

const { t } = useI18n()

defineProps<{
  containerIds?: string[]
  isLoading?: boolean
}>()

const userMessage = defineModel<string>('userMessage', { required: true })
const includeContainerData = defineModel<boolean>('includeContainerData', { required: true })

const emit = defineEmits<{
  send: [message: string]
  toggleContextConfig: []
}>()

const handleSend = (): void => {
  emit('send', userMessage.value)
}

const handleKeyDown = (event: KeyboardEvent): void => {
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="border-t p-4">
    <!-- ChatGPT like input section -->
    <div class="border rounded-3xl bg-foreground/5 px-2 py-2">
      <div class="flex flex-col gap-1">
        <textarea
          v-model="userMessage"
          class="text-sm w-full resize-none px-2 py-3 rounded-lg focus-visible:outline-none focus-visible:ring-0"
          rows="1"
          :placeholder="t('ai.chat.placeholder')"
          @keydown="handleKeyDown"
        />
        <div class="flex flex-row items-center justify-between gap-2">
          <div class="flex flex-row gap-2 items-center">
            <!-- Actions -->
            <!-- Context toggle (only show when containerIds are provided) -->
            <AiIncludeContainerDataButton
              v-model:include-container-data="includeContainerData"
              @toggle-context-config="emit('toggleContextConfig')"
            />
          </div>
          <div class="flex flex-row gap-2 items-center justify-end">
            <Button
              v-tooltip.bottom="t('ai.chat.send')"
              :disabled="!userMessage.trim() || isLoading"
              size="icon"
              class="rounded-full"
              :aria-label="t('ai.chat.send')"
              @click="handleSend"
            >
              <SendIcon class="size-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <p class="text-xs text-muted-foreground mt-2">
      {{ t('ai.chat.sendHint') }}
    </p>
  </div>
</template>
