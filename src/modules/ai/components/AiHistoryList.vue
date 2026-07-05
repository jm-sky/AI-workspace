<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IAiHistoryItem } from '../types/history'
import AiHistoryItem from './AiHistoryItem.vue'

const { t } = useI18n()

const props = defineProps<{
  items: IAiHistoryItem[]
  loading?: boolean
}>()

const emit = defineEmits<{
  restore: [item: IAiHistoryItem]
  delete: [id: string]
  viewDetails: [item: IAiHistoryItem]
}>()

const isEmpty = computed(() => !props.loading && props.items.length === 0)
</script>

<template>
  <div class="space-y-4">
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-sm text-muted-foreground">
        {{ t('common.loading') }}
      </div>
    </div>

    <div v-else-if="isEmpty" class="flex flex-col items-center justify-center py-12 text-center">
      <div class="text-sm text-muted-foreground">
        {{ t('ai.history.empty') }}
      </div>
    </div>

    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <AiHistoryItem
        v-for="item in items"
        :key="item.id"
        :item
        @restore="emit('restore', $event)"
        @delete="emit('delete', $event)"
        @view-details="emit('viewDetails', $event)"
      />
    </div>
  </div>
</template>

