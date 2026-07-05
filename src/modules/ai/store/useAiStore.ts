/**
 * AI Store
 * Manages AI-related state (settings, models, history)
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type {
  IAiHistoryItem,
  IAiModel,
  IAiSettings,
  IAiUpdateSettings,
  LoadHistoryParams,
} from '../types'
import { aiApiService } from '../services/aiApiService'

export const useAiStore = defineStore('ai', () => {
  // State
  const settings = ref<IAiSettings | null>(null)
  const availableModels = ref<IAiModel[]>([])
  const history = ref<IAiHistoryItem[]>([])
  const historyTotal = ref(0)
  const isLoading = ref(false)

  // Computed
  const selectedModel = computed<IAiModel | undefined>(() =>
    availableModels.value.find(m => m.id === settings.value?.selectedModel),
  )

  const hasOwnToken = computed<boolean>(() => settings.value?.hasToken ?? false)

  const monthlyUsage = computed(() => ({
    tokens: settings.value?.monthlyTokensUsed ?? 0,
    cost: settings.value?.monthlyCostUsed ?? 0,
    tokenLimit: settings.value?.monthlyTokenLimit,
    costLimit: settings.value?.monthlyCostLimit,
  }))

  // Actions
  const loadSettings = async (): Promise<void> => {
    isLoading.value = true
    try {
      settings.value = await aiApiService.getSettings()
    } finally {
      isLoading.value = false
    }
  }

  const updateSettings = async (updates: IAiUpdateSettings): Promise<void> => {
    isLoading.value = true
    try {
      settings.value = await aiApiService.updateSettings(updates)
    } finally {
      isLoading.value = false
    }
  }

  const loadModels = async (): Promise<void> => {
    isLoading.value = true
    try {
      const response = await aiApiService.getModels()
      availableModels.value = response.models
    } finally {
      isLoading.value = false
    }
  }

  const setApiToken = async (token: string): Promise<void> => {
    await aiApiService.setApiToken({ apiToken: token })
    await loadSettings()
  }

  const removeApiToken = async (): Promise<void> => {
    await aiApiService.removeApiToken()
    // Force refresh to ensure we get updated data
    isLoading.value = true
    try {
      settings.value = await aiApiService.getSettings(true)
    } finally {
      isLoading.value = false
    }
  }

  const loadHistory = async (params?: LoadHistoryParams): Promise<void> => {
    isLoading.value = true
    try {
      const response = await aiApiService.getHistory(params)
      history.value = response.items
      historyTotal.value = response.total
    } finally {
      isLoading.value = false
    }
  }

  const deleteHistoryItem = async (id: string): Promise<void> => {
    await aiApiService.deleteHistoryItem(id)
    history.value = history.value.filter(item => item.id !== id)
  }

  const clearHistory = async (): Promise<void> => {
    await aiApiService.clearHistory()
    history.value = []
  }

  return {
    // State
    settings,
    availableModels,
    history,
    historyTotal,
    isLoading,

    // Computed
    selectedModel,
    hasOwnToken,
    monthlyUsage,

    // Actions
    loadSettings,
    updateSettings,
    loadModels,
    setApiToken,
    removeApiToken,
    loadHistory,
    deleteHistoryItem,
    clearHistory,
  }
})


