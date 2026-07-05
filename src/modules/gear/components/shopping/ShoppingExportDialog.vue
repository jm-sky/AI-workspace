<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const { t } = useI18n()

const { markdownContent } = defineProps<{
  markdownContent: string
}>()

const open = defineModel<boolean>('open', { required: true })

const emit = defineEmits<{
  copy: []
}>()
</script>

<template>
  <Dialog :open>
    <DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{{ t('gear.shopping.exportMarkdown', 'Export Markdown') }}</DialogTitle>
        <DialogDescription>
          {{ t('gear.shopping.exportDescription', 'Copy the markdown content below') }}
        </DialogDescription>
      </DialogHeader>
      <div class="space-y-4">
        <pre class="p-4 bg-muted rounded-lg text-sm overflow-x-auto whitespace-pre-wrap">{{ markdownContent }}</pre>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="open = false">
          {{ t('gear.actions.cancel', 'Cancel') }}
        </Button>
        <Button @click="emit('copy')">
          {{ t('gear.shopping.copyMarkdown', 'Copy to Clipboard') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
