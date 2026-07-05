import { beforeEach, describe, expect, it } from 'vitest'
import type { IAiHistoryItem } from '../types/history'

/**
 * Test filtering logic used in AiChatHistorySidebar component
 * This tests the computed property logic without mounting the component
 */
function filterHistoryByContainerIds(
  history: IAiHistoryItem[],
  containerIds?: string[],
): IAiHistoryItem[] {
  let filtered = history

  // Filter by container_ids if provided
  if (containerIds && containerIds.length > 0) {
    filtered = filtered.filter(item => {
      const itemContainerIds = item.containerIds || (item.contextData ? Object.keys(item.contextData) : [])
      // Check if any container_id from props matches item's container_ids
      return containerIds?.some(id => itemContainerIds.includes(id)) ?? false
    })
  }

  return filtered
}

describe('AiChatHistorySidebar - Filtering Logic', () => {
  beforeEach(() => {
    // Setup
  })

  it('should filter history by containerIds', () => {
    const mockHistoryItems: IAiHistoryItem[] = [
      {
        id: 'history-1',
        operationType: 'chat',
        finalPrompt: 'Test prompt 1',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1'],
        createdAt: '2024-01-01T00:00:00Z',
      },
      {
        id: 'history-2',
        operationType: 'chat',
        finalPrompt: 'Test prompt 2',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-2'],
        createdAt: '2024-01-02T00:00:00Z',
      },
      {
        id: 'history-3',
        operationType: 'chat',
        finalPrompt: 'Test prompt 3',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1', 'container-2'],
        createdAt: '2024-01-03T00:00:00Z',
      },
    ]

    const filtered = filterHistoryByContainerIds(mockHistoryItems, ['container-1'])

    expect(filtered).toHaveLength(2)
    expect(filtered[0]?.id).toBe('history-1')
    expect(filtered[1]?.id).toBe('history-3')
  })

  it('should return all history when containerIds is undefined', () => {
    const mockHistoryItems: IAiHistoryItem[] = [
      {
        id: 'history-1',
        operationType: 'chat',
        finalPrompt: 'Test prompt 1',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1'],
        createdAt: '2024-01-01T00:00:00Z',
      },
      {
        id: 'history-2',
        operationType: 'chat',
        finalPrompt: 'Test prompt 2',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-2'],
        createdAt: '2024-01-02T00:00:00Z',
      },
    ]

    const filtered = filterHistoryByContainerIds(mockHistoryItems, undefined)

    expect(filtered).toHaveLength(2)
  })

  it('should return empty array when no matching containerIds', () => {
    const mockHistoryItems: IAiHistoryItem[] = [
      {
        id: 'history-1',
        operationType: 'chat',
        finalPrompt: 'Test prompt 1',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1'],
        createdAt: '2024-01-01T00:00:00Z',
      },
    ]

    const filtered = filterHistoryByContainerIds(mockHistoryItems, ['container-999'])

    expect(filtered).toHaveLength(0)
  })

  it('should extract containerIds from contextData when containerIds is undefined', () => {
    const mockHistoryItems: IAiHistoryItem[] = [
      {
        id: 'history-1',
        operationType: 'chat',
        finalPrompt: 'Test prompt 1',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: undefined,
        contextData: {
          'container-1': {},
        },
        createdAt: '2024-01-01T00:00:00Z',
      },
    ]

    const filtered = filterHistoryByContainerIds(mockHistoryItems, ['container-1'])

    expect(filtered).toHaveLength(1)
    expect(filtered[0]?.id).toBe('history-1')
  })
})

