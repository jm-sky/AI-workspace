import { apiClient } from '@/shared/services/apiClient'
import type {
  IMemoryCreateRequest,
  IMemoryEntry,
  IMemoryListResponse,
  IMemorySearchRequest,
  IMemoryUpdateRequest,
  MemoryScope,
} from '@/modules/workspace/types/memory'

export async function listMemories(params?: {
  scope?: MemoryScope
  agentKey?: string
  sessionId?: string
  search?: string
  limit?: number
  offset?: number
}): Promise<IMemoryListResponse> {
  const response = await apiClient.get<IMemoryListResponse>('/memory', { params })
  return response.data
}

export async function searchMemories(
  request: IMemorySearchRequest,
): Promise<IMemoryEntry[]> {
  const response = await apiClient.post<IMemoryEntry[]>('/memory/search', request)
  return response.data
}

export async function createMemory(
  request: IMemoryCreateRequest,
): Promise<IMemoryEntry> {
  const response = await apiClient.post<IMemoryEntry>('/memory', request)
  return response.data
}

export async function updateMemory(
  entryId: string,
  request: IMemoryUpdateRequest,
): Promise<IMemoryEntry> {
  const response = await apiClient.patch<IMemoryEntry>(`/memory/${entryId}`, request)
  return response.data
}

export async function deleteMemory(entryId: string): Promise<void> {
  await apiClient.delete(`/memory/${entryId}`)
}
