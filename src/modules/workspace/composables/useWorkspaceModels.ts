import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed, ref, watch } from 'vue'
import { listAiModels } from '@/modules/workspace/services/aiModelsApiService'
import {
  getEffectiveWorkspaceConfig,
  setUserDefaultModel,
} from '@/modules/workspace/services/workspaceConfigApiService'
import type { IAiModel } from '@/modules/workspace/types/workspaceConfig'

export const workspaceModelsQueryKeys = {
  all: ['workspace-models'] as const,
  config: () => [...workspaceModelsQueryKeys.all, 'config'] as const,
  catalog: () => [...workspaceModelsQueryKeys.all, 'catalog'] as const,
}

const selectedModelId = ref<string | null>(null)

export function useWorkspaceModels() {
  const queryClient = useQueryClient()

  const configQuery = useQuery({
    queryKey: workspaceModelsQueryKeys.config(),
    queryFn: getEffectiveWorkspaceConfig,
    staleTime: 5 * 60 * 1000,
  })

  const catalogQuery = useQuery({
    queryKey: workspaceModelsQueryKeys.catalog(),
    queryFn: listAiModels,
    staleTime: 30 * 60 * 1000,
  })

  const allowedModels = computed<IAiModel[]>(() => {
    const allowed = configQuery.data.value?.allowedModels ?? []
    const catalog = catalogQuery.data.value?.models ?? []
    if (allowed.length === 0) return catalog
    const allowedSet = new Set(allowed)
    return catalog.filter((model) => allowedSet.has(model.id))
  })

  const pickDefaultModelId = (models: IAiModel[], defaultModel?: string | null): string | null => {
    if (models.length === 0) return null
    if (defaultModel && models.some((m) => m.id === defaultModel)) {
      return defaultModel
    }
    const recommended = models.find((m) => m.recommended)
    return recommended?.id ?? models[0]?.id ?? null
  }

  watch(
    [() => configQuery.data.value?.defaultModel, allowedModels],
    ([defaultModel, models]) => {
      if (selectedModelId.value && models.some((m) => m.id === selectedModelId.value)) {
        return
      }
      selectedModelId.value = pickDefaultModelId(models, defaultModel)
    },
    { immediate: true },
  )

  const selectedModel = computed<IAiModel | undefined>(() =>
    allowedModels.value.find((m) => m.id === selectedModelId.value),
  )

  const hasValidModel = computed(() => !!selectedModel.value)

  const selectModelMutation = useMutation({
    mutationFn: (modelId: string) => setUserDefaultModel(modelId),
    onSuccess: async (_data, modelId) => {
      selectedModelId.value = modelId
      await queryClient.invalidateQueries({ queryKey: workspaceModelsQueryKeys.config() })
    },
  })

  const selectModel = async (modelId: string) => {
    selectedModelId.value = modelId
    await selectModelMutation.mutateAsync(modelId)
  }

  const getSelectedModelId = () => selectedModelId.value ?? undefined

  return {
    allowedModels,
    selectedModel,
    selectedModelId,
    configQuery,
    catalogQuery,
    isLoading: computed(() => configQuery.isLoading.value || catalogQuery.isLoading.value),
    isUpdating: computed(() => selectModelMutation.isPending.value),
    selectModel,
    getSelectedModelId,
    hasValidModel,
  }
}
