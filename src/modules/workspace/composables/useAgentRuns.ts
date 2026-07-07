import { computed, ref } from 'vue'
import { listAgentRuns } from '@/modules/workspace/services/agentApiService'
import { filterSessionsByQuery } from '@/modules/workspace/utils/sessionFilter'
import { getApiErrorMessage } from '@/shared/utils/apiError'
import type { IAgentRunSummary } from '@/modules/workspace/types/agent'

export function useAgentRuns() {
  const runs = ref<IAgentRunSummary[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  const filteredRuns = computed(() => filterSessionsByQuery(runs.value, searchQuery.value))

  const loadRuns = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await listAgentRuns({ limit: 50, offset: 0 })
      runs.value = response.runs
      total.value = response.total
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Failed to load sessions')
    } finally {
      isLoading.value = false
    }
  }

  return {
    runs,
    total,
    isLoading,
    error,
    searchQuery,
    filteredRuns,
    loadRuns,
  }
}
