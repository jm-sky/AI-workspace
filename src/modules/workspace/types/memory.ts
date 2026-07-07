export type MemoryScope = 'session' | 'user' | 'agent'

export interface IMemoryEntry {
  id: string
  content: string
  scope: MemoryScope
  agentKey?: string | null
  sessionId?: string | null
  source: string
  metadata?: Record<string, unknown> | null
  similarity?: number | null
  createdAt: string
  updatedAt: string
}

export interface IMemoryListResponse {
  entries: IMemoryEntry[]
  total: number
}

export interface IMemoryCreateRequest {
  content: string
  scope?: MemoryScope
  agentKey?: string
  sessionId?: string
}

export interface IMemorySearchRequest {
  query: string
  scope?: MemoryScope
  agentKey?: string
  sessionId?: string
  limit?: number
}
