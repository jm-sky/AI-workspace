/**
 * AI Model types
 */

export interface IAiModelPricing {
  input: number // per 1M tokens
  output: number // per 1M tokens
}

export interface IAiModel {
  id: string
  name: string
  provider: string
  context_window: number
  pricing: IAiModelPricing
  recommended_for: string[]
  description?: string
  available?: boolean
}

export interface IAiModelsResponse {
  models: IAiModel[]
}

