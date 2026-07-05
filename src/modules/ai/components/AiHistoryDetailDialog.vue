<script setup lang="ts">
import { Clock, MessageSquare, Trash2 } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import type { IAiHistoryItem } from '../types/history'
import AiCostDisplay from './AiCostDisplay.vue'

const { t } = useI18n()

const props = defineProps<{
  open: boolean
  item: IAiHistoryItem | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  restore: [item: IAiHistoryItem]
  delete: [id: string]
}>()

const formattedDate = computed(() => {
  if (!props.item) return ''
  const date = new Date(props.item.createdAt)
  return date.toLocaleString()
})

const handleClose = (): void => {
  emit('update:open', false)
}

const handleRestore = (): void => {
  if (props.item) {
    emit('restore', props.item)
    handleClose()
  }
}

const handleDelete = (): void => {
  if (props.item) {
    emit('delete', props.item.id)
    handleClose()
  }
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleClose">
    <DialogContent class="max-w-3xl">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <MessageSquare class="size-5" />
          {{ t('ai.history.details') }}
        </DialogTitle>
        <DialogDescription>
          {{ formattedDate }}
        </DialogDescription>
      </DialogHeader>

      <div v-if="item" class="space-y-6 max-h-[80vh] overflow-y-auto -mx-4 px-4">
        <!-- Metadata -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <div class="text-sm font-medium mb-1">
              {{ t('ai.history.model') }}
            </div>
            <div class="text-sm text-muted-foreground">
              {{ item.model }}
            </div>
          </div>
          <div>
            <div class="text-sm font-medium mb-1">
              {{ t('ai.history.provider') }}
            </div>
            <div class="text-sm text-muted-foreground">
              {{ item.provider }}
            </div>
          </div>
          <div v-if="item.operationType">
            <div class="text-sm font-medium mb-1">
              {{ t('ai.history.operationType') }}
            </div>
            <Badge variant="outline" class="text-xs">
              {{ t(`ai.history.operationTypes.${item.operationType}`) }}
            </Badge>
          </div>
          <div v-if="item.durationMs">
            <div class="text-sm font-medium mb-1">
              {{ t('ai.history.duration') }}
            </div>
            <div class="text-sm text-muted-foreground flex items-center gap-1">
              <Clock class="size-3" />
              {{ item.durationMs }}ms
            </div>
          </div>
        </div>

        <!-- Cost and Tokens -->
        <div>
          <div class="text-sm font-medium mb-2">
            {{ t('ai.cost.cost') }} & {{ t('ai.cost.tokens') }}
          </div>
          <AiCostDisplay
            :tokens="item.tokens"
            :cost="item.cost"
          />
        </div>

        <!-- Final Prompt -->
        <div>
          <div class="text-sm font-medium mb-2">
            Final Prompt
          </div>
          <div class="p-3 bg-muted rounded-md text-sm font-mono whitespace-pre-wrap wrap-break-word">
            {{ item.finalPrompt }}
          </div>
        </div>

        <!-- Context Data -->
        <div v-if="item.contextData && Object.keys(item.contextData).length > 0">
          <div class="text-sm font-medium mb-2">
            Context Data
          </div>
          <div class="p-3 bg-muted rounded-md text-sm">
            <pre class="whitespace-pre-wrap wrap-break-word">{{ JSON.stringify(item.contextData, null, 2) }}</pre>
          </div>
        </div>

        <!-- Response Data -->
        <div>
          <div class="text-sm font-medium mb-2">
            Response Data
          </div>
          <div class="p-3 bg-muted rounded-md text-sm">
            <pre class="whitespace-pre-wrap wrap-break-word">{{ JSON.stringify(item.responseData, null, 2) }}</pre>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-2 pt-4 border-t">
        <Button
          variant="outline"
          @click="handleRestore"
        >
          {{ t('ai.history.restore') }}
        </Button>
        <Button
          variant="destructive"
          @click="handleDelete"
        >
          <Trash2 class="size-4" />
          {{ t('ai.history.delete') }}
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>

