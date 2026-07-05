/**
 * AI Models Composable
 * Handles AI model management
 */

import { computed } from 'vue'
import type { IAiModel } from '../types'
import { useAiStore } from '../store/useAiStore'

export function useAiModels() {
  const aiStore = useAiStore()

  const models = computed<IAiModel[]>(() => aiStore.availableModels)
  const selectedModel = computed<IAiModel | undefined>(() => aiStore.selectedModel)
  const isLoading = computed<boolean>(() => aiStore.isLoading)

  const loadModels = async (): Promise<void> => {
    await aiStore.loadModels()
  }

  const selectModel = async (modelId: string): Promise<void> => {
    await aiStore.updateSettings({ selectedModel: modelId })
  }

  const getModelById = (modelId: string): IAiModel | undefined => {
    return models.value.find(m => m.id === modelId)
  }

  const getRecommendedModels = (task: string): IAiModel[] => {
    return models.value.filter(m => m.recommended_for.includes(task))
  }

  return {
    models,
    selectedModel,
    isLoading,
    loadModels,
    selectModel,
    getModelById,
    getRecommendedModels,
  }
}

