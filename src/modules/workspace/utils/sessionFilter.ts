import type { IAgentRunSummary } from '@/modules/workspace/types/agent'

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
