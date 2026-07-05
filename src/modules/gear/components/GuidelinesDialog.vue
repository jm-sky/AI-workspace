<script setup lang="ts">
import { Check, Copy } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { guidelinesTemplate } from '../services/markdownImportService'

defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { t } = useI18n()
const copied = ref(false)

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(guidelinesTemplate)
    copied.value = true
    toast.success(t('gear.export.guidelinesCopied', 'Guidelines copied to clipboard'))
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error copying guidelines:', error)
  }
}

const handleOpenChange = (value: boolean) => {
  emit('update:open', value)
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="min-w-full md:min-w-2xl max-w-screen md:max-w-4xl max-h-[80vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.export.guidelines', 'Guidelines') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.export.guidelinesDescription', 'Formatting guidelines for AI when generating or updating gear lists') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex-1 max-w-[calc(100vw-2rem)] md:max-w-full overflow-auto">
        <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto">{{ guidelinesTemplate }}</pre>
      </div>

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button class="flex-1" variant="outline" @click="handleOpenChange(false)">
          {{ t('common.close') }}
        </Button>
        <Button class="flex-1" @click="handleCopy">
          <Copy v-if="!copied" class="size-4" />
          <Check v-else class="size-4" />
          {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

