import { apiClient } from '@/shared/services/apiClient'
import type { IAiModelsResponse } from '@/modules/workspace/types/workspaceConfig'

export async function listAiModels(): Promise<IAiModelsResponse> {
  const response = await apiClient.get<IAiModelsResponse>('/ai/models')
  return response.data
}
