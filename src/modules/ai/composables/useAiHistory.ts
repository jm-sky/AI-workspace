/**
 * AI History Composable
 * Handles AI history management
 */

import { computed, ref } from 'vue'
import type { IAiHistoryItem, IAiHistoryQuery } from '../types'
import { useAiStore } from '../store/useAiStore'

export function useAiHistory() {
  const aiStore = useAiStore()
  const selectedHistoryItem = ref<IAiHistoryItem | null>(null)

  const history = computed<IAiHistoryItem[]>(() => aiStore.history)
  const historyTotal = computed<number>(() => aiStore.historyTotal)
  const isLoading = computed<boolean>(() => aiStore.isLoading)

  const loadHistory = async (query?: IAiHistoryQuery): Promise<void> => {
    await aiStore.loadHistory(query)
  }

  const deleteHistoryItem = async (id: string): Promise<void> => {
    await aiStore.deleteHistoryItem(id)
    if (selectedHistoryItem.value?.id === id) {
      selectedHistoryItem.value = null
    }
  }

  const clearHistory = async (): Promise<void> => {
    await aiStore.clearHistory()
    selectedHistoryItem.value = null
  }

  const selectHistoryItem = (item: IAiHistoryItem | null): void => {
    selectedHistoryItem.value = item
  }

  const getHistoryItemById = (id: string): IAiHistoryItem | undefined => {
    return history.value.find(item => item.id === id)
  }

  return {
    history,
    historyTotal,
    selectedHistoryItem,
    isLoading,
    loadHistory,
    deleteHistoryItem,
    clearHistory,
    selectHistoryItem,
    getHistoryItemById,
  }
}

