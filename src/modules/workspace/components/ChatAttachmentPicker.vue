<script setup lang="ts">
import { Paperclip } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'

defineProps<{
  accept: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  pick: [files: FileList]
}>()

const { t } = useI18n()
const fileInput = ref<HTMLInputElement | null>(null)

const openPicker = () => {
  fileInput.value?.click()
}

const onChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files?.length) {
    emit('pick', input.files)
    input.value = ''
  }
}
</script>

<template>
  <div>
    <input
      ref="fileInput"
      type="file"
      class="sr-only"
      :accept="accept"
      multiple
      :disabled="disabled"
      @change="onChange"
    >
    <Button
      type="button"
      variant="ghost"
      size="icon"
      class="shrink-0 rounded-xl"
      :disabled="disabled"
      :title="t('workspace.attachments.attach')"
      :aria-label="t('workspace.attachments.attach')"
      @click="openPicker"
    >
      <Paperclip class="size-4" />
    </Button>
  </div>
</template>
