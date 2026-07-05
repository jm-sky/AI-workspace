<script setup lang="ts">
import { Clock, MessageSquare, Trash2 } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Separator from '@/components/ui/separator/Separator.vue'
import type { IAiHistoryItem } from '../types/history'
import AiCostDisplay from './AiCostDisplay.vue'

const { t } = useI18n()

const props = defineProps<{
  item: IAiHistoryItem
}>()

const emit = defineEmits<{
  restore: [item: IAiHistoryItem]
  delete: [id: string]
  viewDetails: [item: IAiHistoryItem]
}>()

const formattedDate = computed(() => {
  const date = new Date(props.item.createdAt)
  return date.toLocaleString()
})

const promptTitle = computed(() => {
  const prompt = props.item.finalPrompt
  if (!prompt) return t('ai.history.noPreview')

  // Try to extract first sentence (up to 100 chars)
  const firstSentenceMatch = prompt.match(/^[^.!?\n]{1,100}[.!?]?/)
  if (firstSentenceMatch) {
    const firstSentence = firstSentenceMatch[0].trim()
    if (firstSentence.length <= 100) {
      return firstSentence
    }
  }

  // Fallback to first 100 chars
  return prompt.length > 100
    ? prompt.substring(0, 100).trim() + '...'
    : prompt.trim()
})

const promptPreview = computed(() => {
  const prompt = props.item.finalPrompt
  if (!prompt) return null

  // Show more of the prompt if it's longer than the title
  if (prompt.length > 100) {
    return prompt.substring(100).trim()
  }

  return null
})

const handleRestore = (): void => {
  emit('restore', props.item)
}

const handleDelete = (): void => {
  emit('delete', props.item.id)
}

const handleViewDetails = (): void => {
  emit('viewDetails', props.item)
}
</script>

<template>
  <Card class="hover:shadow-md transition-shadow">
    <CardHeader class="flex flex-col items-start justify-between gap-2">
      <div class="flex flex-row items-center gap-2">
        <MessageSquare class="size-4 text-muted-foreground" />
        <CardTitle class="text-base font-semibold line-clamp-1">
          {{ promptTitle }}
        </CardTitle>
      </div>
      <CardDescription class="text-xs text-muted-foreground">
        <div class="flex items-center gap-2 flex-wrap">
          <span>{{ item.model }}</span>
          <span class="text-muted-foreground/70">•</span>
          <span>{{ item.provider }}</span>
          <template v-if="item.durationMs">
            <span class="text-muted-foreground/70">•</span>
            <span class="flex items-center gap-1">
              <Clock class="size-3" />
              {{ item.durationMs }}ms
            </span>
          </template>
          <Badge v-if="item.operationType" variant="outline" class="text-xs">
            {{ t(`ai.history.operationTypes.${item.operationType}`) }}
          </Badge>
        </div>
      </CardDescription>
    </CardHeader>

    <CardContent class="pt-0 space-y-3">
      <!-- Extended Preview (if prompt is longer than title) -->
      <div v-if="promptPreview" class="text-sm text-muted-foreground line-clamp-2">
        {{ promptPreview }}
      </div>

      <!-- Cost and Tokens -->
      <AiCostDisplay
        :tokens="item.tokens"
        :cost="item.cost"
        class="text-xs"
      />

      <Separator class="my-4" />

      <!-- Actions -->
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <div class="text-xs text-muted-foreground">
          {{ formattedDate }}
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            @click="handleViewDetails"
          >
            {{ t('ai.history.details') }}
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="handleRestore"
          >
            {{ t('ai.history.restore') }}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            class="hover:text-destructive"
            @click="handleDelete"
          >
            <Trash2 class="size-4" />
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

