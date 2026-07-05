/**
 * AI Settings types
 */

export interface IAiSettings {
  id: string
  userId: string
  useOwnToken: boolean
  hasToken: boolean
  selectedModel: string
  contextFields: Record<string, unknown>
  maxTokens: number | null
  temperature: number
  monthlyTokensUsed: number
  monthlyCostUsed: number
  monthlyTokenLimit?: number
  monthlyCostLimit?: number
  createdAt: string
  updatedAt: string
}

export interface IAiUpdateSettings {
  selectedModel?: string
  contextFields?: Record<string, unknown>
  maxTokens?: number
  temperature?: number
}

export interface IAiSetTokenRequest {
  apiToken: string
}

export interface IAiSetTokenResponse {
  success: boolean
  message: string
}

