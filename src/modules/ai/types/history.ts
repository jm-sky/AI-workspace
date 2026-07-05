/**
 * AI History types
 */

import type { AiOperationType } from './chat'
import type { IAiCost, IAiTokenUsage } from './chat'

export interface IAiHistoryItem {
  id: string
  operationType: AiOperationType
  finalPrompt: string
  contextData?: Record<string, unknown>
  responseData: Record<string, unknown>
  model: string
  provider: string
  tokens: IAiTokenUsage
  cost: IAiCost
  durationMs?: number
  usedOwnToken: boolean
  containerIds?: string[]
  createdAt: string
}

export interface IAiHistoryListResponse {
  items: IAiHistoryItem[]
  total: number
  limit: number
  offset: number
}

export interface IAiHistoryDetail extends IAiHistoryItem {
  responsePreview?: string
  // Additional fields from backend API
  userId?: string
  promptTokens?: number
  completionTokens?: number
  totalTokens?: number
  costUsd?: number | null
  inputData?: {
    message?: string
    context?: Record<string, unknown>
    [key: string]: unknown
  }
  outputData?: {
    message?: string
    [key: string]: unknown
  }
  metadata?: {
    provider?: string
    durationMs?: number
    usedOwnToken?: boolean
    [key: string]: unknown
  } | null
}

export interface IAiHistoryQuery {
  limit?: number
  offset?: number
  operationType?: AiOperationType
}

export interface LoadHistoryParams {
  limit?: number
  offset?: number
  operationType?: AiOperationType
}
