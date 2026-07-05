import { describe, expect, it } from 'vitest'
import type { IAiHistoryItem } from '../types/history'

/**
 * Utility function to determine navigation target based on containerIds
 * This logic is used in AiHistoryPage for resume chat functionality
 */
function getNavigationTarget(item: IAiHistoryItem): { path: string; query: { restoreHistoryId: string } } {
  const containerIds = item.containerIds || (item.contextData ? Object.keys(item.contextData) : [])
  
  if (containerIds.length === 1) {
    // Single container - navigate to Container Detail Page
    return {
      path: `/gear/${containerIds[0]}`,
      query: { restoreHistoryId: item.id },
    }
  } else {
    // Multiple or no containers - navigate to Containers List Page
    return {
      path: '/gear',
      query: { restoreHistoryId: item.id },
    }
  }
}

describe('historyNavigation', () => {
  describe('getNavigationTarget', () => {
    it('should navigate to Container Detail when single containerId', () => {
      const item: IAiHistoryItem = {
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

      const target = getNavigationTarget(item)
      
      expect(target.path).toBe('/gear/container-1')
      expect(target.query.restoreHistoryId).toBe('history-1')
    })

    it('should navigate to Containers List when multiple containerIds', () => {
      const item: IAiHistoryItem = {
        id: 'history-2',
        operationType: 'chat',
        finalPrompt: 'Test prompt',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: ['container-1', 'container-2'],
        createdAt: '2024-01-01T00:00:00Z',
      }

      const target = getNavigationTarget(item)
      
      expect(target.path).toBe('/gear')
      expect(target.query.restoreHistoryId).toBe('history-2')
    })

    it('should navigate to Containers List when no containerIds', () => {
      const item: IAiHistoryItem = {
        id: 'history-3',
        operationType: 'chat',
        finalPrompt: 'Test prompt',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: undefined,
        createdAt: '2024-01-01T00:00:00Z',
      }

      const target = getNavigationTarget(item)
      
      expect(target.path).toBe('/gear')
      expect(target.query.restoreHistoryId).toBe('history-3')
    })

    it('should extract containerIds from contextData when containerIds is undefined', () => {
      const item: IAiHistoryItem = {
        id: 'history-4',
        operationType: 'chat',
        finalPrompt: 'Test prompt',
        responseData: {},
        model: 'openai/gpt-4o-mini',
        provider: 'openai',
        tokens: { input: 10, output: 20, total: 30 },
        cost: { input: 0, output: 0, total: 0.001 },
        usedOwnToken: false,
        containerIds: undefined,
        contextData: {
          'container-1': {},
          'container-2': {},
        },
        createdAt: '2024-01-01T00:00:00Z',
      }

      const target = getNavigationTarget(item)
      
      // Should navigate to Containers List because multiple containers extracted from contextData
      expect(target.path).toBe('/gear')
      expect(target.query.restoreHistoryId).toBe('history-4')
    })

    it('should extract single containerId from contextData when containerIds is undefined', () => {
      const item: IAiHistoryItem = {
        id: 'history-5',
        operationType: 'chat',
        finalPrompt: 'Test prompt',
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
      }

      const target = getNavigationTarget(item)
      
      // Should navigate to Container Detail because single container extracted from contextData
      expect(target.path).toBe('/gear/container-1')
      expect(target.query.restoreHistoryId).toBe('history-5')
    })
  })
})

