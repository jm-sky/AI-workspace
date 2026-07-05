import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { IAiHistoryItem } from '../types/history'
import { useAiStore } from '../store/useAiStore'
import { useAiHistory } from './useAiHistory'

// Mock aiApiService
vi.mock('../services/aiApiService', () => ({
  aiApiService: {
    getHistory: vi.fn(),
    getHistoryDetail: vi.fn(),
    deleteHistoryItem: vi.fn(),
    clearHistory: vi.fn(),
  },
}))

describe('useAiHistory', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('getHistoryItemById', () => {
    it('should find history item by id', () => {
      const store = useAiStore()
      const { getHistoryItemById } = useAiHistory()

      const mockHistoryItem: IAiHistoryItem = {
        id: 'history-1',
        operationType: 'chat',
        finalPrompt: 'Test prompt',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1'],
        createdAt: '2024-01-01T00:00:00Z',
      }

      store.history = [mockHistoryItem]

      const found = getHistoryItemById('history-1')
      expect(found).toEqual(mockHistoryItem)
    })

    it('should return undefined if item not found', () => {
      const store = useAiStore()
      const { getHistoryItemById } = useAiHistory()

      store.history = []

      const found = getHistoryItemById('non-existent')
      expect(found).toBeUndefined()
    })
  })

  describe('history filtering by containerIds', () => {
    it('should filter history items by containerIds', () => {
      const store = useAiStore()
      const { history } = useAiHistory()

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

      store.history = mockHistoryItems

      // Filter by container-1
      const filtered = history.value.filter(item => 
        item.containerIds?.includes('container-1')
      )

      expect(filtered).toHaveLength(2)
      expect(filtered[0]?.id).toBe('history-1')
      expect(filtered[1]?.id).toBe('history-3')
    })

    it('should handle history items without containerIds', () => {
      const store = useAiStore()
      const { history } = useAiHistory()

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
          containerIds: ['container-1'],
          createdAt: '2024-01-02T00:00:00Z',
        },
      ]

      store.history = mockHistoryItems

      // Filter by container-1
      const filtered = history.value.filter(item => 
        item.containerIds?.includes('container-1')
      )

      expect(filtered).toHaveLength(1)
      expect(filtered[0]?.id).toBe('history-2')
    })
  })

  describe('selectHistoryItem', () => {
    it('should select history item', () => {
      const { selectHistoryItem, selectedHistoryItem } = useAiHistory()

      const mockHistoryItem: IAiHistoryItem = {
        id: 'history-1',
        operationType: 'chat',
        finalPrompt: 'Test prompt',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1'],
        createdAt: '2024-01-01T00:00:00Z',
      }

      selectHistoryItem(mockHistoryItem)
      expect(selectedHistoryItem.value).toEqual(mockHistoryItem)
    })

    it('should clear selection when null is passed', () => {
      const { selectHistoryItem, selectedHistoryItem } = useAiHistory()

      const mockHistoryItem: IAiHistoryItem = {
        id: 'history-1',
        operationType: 'chat',
        finalPrompt: 'Test prompt',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1'],
        createdAt: '2024-01-01T00:00:00Z',
      }

      selectHistoryItem(mockHistoryItem)
      selectHistoryItem(null)
      expect(selectedHistoryItem.value).toBeNull()
    })
  })
})

