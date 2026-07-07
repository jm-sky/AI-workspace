import { describe, expect, it } from 'vitest'
import { filterSessionsByQuery } from './sessionFilter'
import type { IAgentRunSummary } from '@/modules/workspace/types/agent'

const mockRuns: IAgentRunSummary[] = [
  {
    id: 'run-1',
    agentKey: 'jira-360',
    status: 'completed',
    inputMessage: 'IT-123 customer overview',
    outputMessage: 'Summary for IT-123',
    createdAt: '2026-07-07T10:00:00Z',
  },
  {
    id: 'run-2',
    agentKey: 'jira-360',
    status: 'completed',
    inputMessage: 'PROJ-99 status',
    outputMessage: 'Done',
    createdAt: '2026-07-07T11:00:00Z',
  },
]

describe('filterSessionsByQuery', () => {
  it('returns all runs when query is empty', () => {
    expect(filterSessionsByQuery(mockRuns, '')).toHaveLength(2)
    expect(filterSessionsByQuery(mockRuns, '   ')).toHaveLength(2)
  })

  it('filters by input message', () => {
    const filtered = filterSessionsByQuery(mockRuns, 'it-123')
    expect(filtered).toHaveLength(1)
    expect(filtered[0]?.id).toBe('run-1')
  })

  it('filters by output message and agent key', () => {
    expect(filterSessionsByQuery(mockRuns, 'proj-99')).toHaveLength(1)
    expect(filterSessionsByQuery(mockRuns, 'jira-360')).toHaveLength(2)
  })
})
