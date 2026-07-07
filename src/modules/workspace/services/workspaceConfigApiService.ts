import { apiClient } from '@/shared/services/apiClient'
import type { IEffectiveWorkspaceConfig } from '@/modules/workspace/types/workspaceConfig'

export async function getEffectiveWorkspaceConfig(): Promise<IEffectiveWorkspaceConfig> {
  const response = await apiClient.get<IEffectiveWorkspaceConfig>('/workspace/config/effective')
  return response.data
}

export async function setUserDefaultModel(modelId: string): Promise<void> {
  await apiClient.put('/workspace/config/user/default_model', {
    key: 'default_model',
    value: modelId,
  })
}
