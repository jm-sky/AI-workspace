<!--
  AI Chat History Sidebar Component
  Displays filtered history for chat context
-->
<script setup lang="ts">
import { History } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import type { IAiHistoryItem } from '../types/history'
import { useAiHistory } from '../composables/useAiHistory'

const { t } = useI18n()
const router = useRouter()
const { history, isLoading, loadHistory } = useAiHistory()

const props = defineProps<{
  containerIds?: string[]
}>()

const emit = defineEmits<{
  restore: [item: IAiHistoryItem]
}>()

// Load chat history filtered by operation type and container_ids
onMounted(async () => {
  await loadHistory({
    operationType: 'chat',
    limit: 50,
    offset: 0,
  })
})

// Filter history by container_ids if provided
const filteredHistory = computed(() => {
  let filtered = history.value

  // Filter by container_ids if provided
  if (props.containerIds && props.containerIds.length > 0) {
    filtered = filtered.filter(item => {
      const itemContainerIds = item.containerIds || (item.contextData ? Object.keys(item.contextData) : [])
      // Check if any container_id from props matches item's container_ids
      return props.containerIds?.some(id => itemContainerIds.includes(id)) ?? false
    })
  }

  return filtered
})

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const preview = (prompt: string): string => {
  if (!prompt) return t('ai.chat.history.empty')
  return prompt.length > 100
    ? prompt.substring(0, 100) + '...'
    : prompt
}

const handleRestore = (item: IAiHistoryItem): void => {
  emit('restore', item)
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-4 border-b">
      <History class="size-4" />
      <h3 class="font-semibold">
        {{ t('ai.chat.history.title') }}
      </h3>
    </div>

    <!-- History List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="text-sm text-muted-foreground">
          {{ t('common.loading') }}
        </div>
      </div>

      <div v-else-if="filteredHistory.length === 0" class="flex flex-col items-center justify-center py-12 text-center px-4">
        <div class="text-sm text-muted-foreground">
          {{ t('ai.chat.history.empty') }}
        </div>
      </div>

      <div v-else class="p-2 space-y-2">
        <div
          v-for="item in filteredHistory"
          :key="item.id"
          class="p-3 rounded-md border hover:bg-accent cursor-pointer transition-colors"
          @click="handleRestore(item)"
        >
          <div class="text-xs text-muted-foreground mb-1">
            {{ formatDate(item.createdAt) }}
          </div>
          <div class="text-sm line-clamp-2">
            {{ preview(item.finalPrompt) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="p-4 border-t">
      <Button
        variant="outline"
        size="sm"
        class="w-full"
        @click="router.push({ path: '/ai/history' })"
      >
        {{ t('ai.history.viewAll') }}
      </Button>
    </div>
  </div>
</template>

