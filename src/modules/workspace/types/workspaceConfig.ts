export interface IEffectiveWorkspaceConfig {
  allowedModels: string[]
  defaultModel: string | null
  maxTokens: number | null
  ragEnabled: boolean
  toolsEnabled: boolean
}

export interface IAiModel {
  id: string
  name: string
  provider: string
  description?: string | null
  context_length: number
  cost_per_1m_input: number
  cost_per_1m_output: number
  recommended: boolean
}

export interface IAiModelsResponse {
  models: IAiModel[]
}
