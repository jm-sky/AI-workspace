<script setup lang="ts">
import { RefreshCcw, X } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import SearchInput from '@/components/ui/input/SearchInput.vue'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { AiOperationType } from '../types/chat'

const { t } = useI18n()

defineProps<{
  loading?: boolean
}>()

const searchQuery = defineModel<string>('searchQuery', { default: '' })
const operationType = defineModel<AiOperationType | null>('operationType', { default: null })

const emit = defineEmits<{
  clearFilters: []
  refresh: []
}>()

const operationTypes: AiOperationType[] = ['chat', 'classify', 'analyze', 'generate']

const hasActiveFilters = computed(() => {
  return searchQuery.value !== '' || operationType.value !== null
})

const handleClearFilters = (): void => {
  searchQuery.value = ''
  operationType.value = null
  emit('clearFilters')
}
</script>

<template>
  <div class="flex flex-col md:flex-row items-center justify-between gap-4">
    <SearchInput
      id="history-search"
      v-model="searchQuery"
      name="history-search"
      :placeholder="t('ai.history.filters.search')"
      class="min-w-full md:min-w-96"
    />

    <div class="flex flex-row items-center justify-end gap-2">
      <Select v-model="operationType">
        <SelectTrigger id="operation-type-filter" class="min-w-32">
          <SelectValue :placeholder="t('ai.history.filters.all')" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem :value="null">
            {{ t('ai.history.filters.all') }}
          </SelectItem>
          <SelectItem v-for="type in operationTypes" :key="type" :value="type">
            {{ t(`ai.history.operationTypes.${type}`) }}
          </SelectItem>
        </SelectContent>
      </Select>

      <!-- Clear Filters Button -->
      <Button
        v-if="hasActiveFilters"
        variant="outline-destructive"
        size="sm"
        @click="handleClearFilters"
      >
        <X class="size-4" />
        {{ t('gear.catalogue.clearFilters') }}
      </Button>

      <Button
        variant="ghost"
        size="sm"
        :loading
        :aria-label="t('gear.filters.refresh', 'Refresh history')"
        @click="emit('refresh')"
      >
        <RefreshCcw v-if="!loading" class="size-4" />
      </Button>
    </div>
  </div>
</template>

