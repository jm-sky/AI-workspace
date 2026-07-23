<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import type { IChatAttachment } from '@/modules/workspace/types/attachments'

defineProps<{
  attachment: IChatAttachment
}>()

const emit = defineEmits<{
  remove: []
  preview: []
}>()

const { t } = useI18n()

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<template>
  <div class="relative flex items-center gap-2 rounded-xl border border-hairline bg-surface-canvas p-1.5 pr-8">
    <button
      type="button"
      class="size-12 shrink-0 overflow-hidden rounded-lg bg-muted"
      :aria-label="t('workspace.attachments.preview')"
      @click="emit('preview')"
    >
      <img
        v-if="attachment.previewUrl || attachment.kind === 'image'"
        :src="attachment.previewUrl"
        :alt="attachment.originalFilename"
        class="size-full object-cover"
      >
    </button>
    <div class="min-w-0">
      <p class="truncate text-xs font-medium">
        {{ attachment.originalFilename }}
      </p>
      <p class="text-[11px] text-muted-foreground">
        {{ formatSize(attachment.sizeBytes) }}
      </p>
    </div>
    <Button
      type="button"
      variant="ghost"
      size="icon"
      class="absolute right-0.5 top-0.5 size-7"
      :aria-label="t('workspace.attachments.remove')"
      @click="emit('remove')"
    >
      <X class="size-3.5" />
    </Button>
  </div>
</template>
