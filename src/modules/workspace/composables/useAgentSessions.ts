import { computed, ref } from 'vue'
import { listAgentSessions } from '@/modules/workspace/services/agentApiService'
import { filterAgentSessionsByQuery } from '@/modules/workspace/utils/sessionFilter'
import { getApiErrorMessage } from '@/shared/utils/apiError'
import type { IAgentSessionSummary } from '@/modules/workspace/types/agent'

export function useAgentSessions() {
  const sessions = ref<IAgentSessionSummary[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  const filteredSessions = computed(() =>
    filterAgentSessionsByQuery(sessions.value, searchQuery.value),
  )

  const loadSessions = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await listAgentSessions({ limit: 50, offset: 0 })
      sessions.value = response.sessions
      total.value = response.total
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Failed to load sessions')
    } finally {
      isLoading.value = false
    }
  }

  return {
    sessions,
    total,
    isLoading,
    error,
    searchQuery,
    filteredSessions,
    loadSessions,
  }
}
