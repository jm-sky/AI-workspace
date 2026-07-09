import type {
  IAgentRunSummary,
  IAgentSessionSummary,
} from '@/modules/workspace/types/agent'

export function filterSessionsByQuery(
  runs: IAgentRunSummary[],
  query: string,
): IAgentRunSummary[] {
  const normalized = query.trim().toLowerCase()
  if (!normalized) return runs

  return runs.filter((run) => {
    const haystack = [
      run.inputMessage,
      run.outputMessage ?? '',
      run.agentKey,
      run.id,
    ].join(' ').toLowerCase()

    return haystack.includes(normalized)
  })
}

export function filterAgentSessionsByQuery(
  sessions: IAgentSessionSummary[],
  query: string,
): IAgentSessionSummary[] {
  const normalized = query.trim().toLowerCase()
  if (!normalized) return sessions

  return sessions.filter((session) => {
    const haystack = [session.title ?? '', session.agentKey, session.id]
      .join(' ')
      .toLowerCase()

    return haystack.includes(normalized)
  })
}
