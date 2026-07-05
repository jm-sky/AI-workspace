/**
 * AI Chat types
 */

export type AiOperationType = 'chat' | 'classify' | 'analyze' | 'generate'

export type AiActionType = 'create_item' | 'update_item' | 'delete_item' | 'create_container' | 'update_container' | 'None'

export interface IAiChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  tokens?: IAiTokenUsage
  cost?: IAiCost
  created_at?: string
}

export interface IAiTokenUsage {
  input: number
  output: number
  total: number
}

export interface IAiCost {
  input: number
  output: number
  total: number
}

export interface IAiStructuredData {
  action: AiActionType
  items?: IAiStructuredItem[]
  container_id?: string
  updates?: Record<string, unknown>
}

export interface IAiStructuredItem {
  id?: string // For update_item
  name?: string // For create_item
  category?: string
  weight?: number
  quantity?: number
  price?: number
  url?: string
  notes?: string
  brand?: string
  color?: string
  quality?: string
  wearable?: boolean
  consumable?: boolean
  updates?: Record<string, unknown> // For update_item
}

export interface IAiChatHistoryMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface IAiChatRequest {
  message: string
  history?: IAiChatHistoryMessage[]
  context?: Record<string, unknown>
  model?: string
  max_tokens?: number
  temperature?: number
}

export interface IAiStructuredOutput {
  action: AiActionType | null
  data: Record<string, unknown>
}

export interface IAiChatResponse {
  message: string
  structured_output: IAiStructuredOutput | null
  tokens: {
    prompt: number
    completion: number
    total: number
  }
  cost: number | null
  model: string
  prompt?: string | null
}

