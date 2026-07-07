import { inject, type InjectionKey, onMounted, provide, type Ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useAgentRuns } from '@/modules/workspace/composables/useAgentRuns'

export interface IChatSessionNavDeps {
  activeRunId: Ref<string | null | undefined>
  loadRun: (runId: string) => Promise<void>
  clearChat: () => void
}

export interface IChatSessionNavContext {
  runsLoading: Ref<boolean>
  runsError: Ref<string | null>
  searchQuery: Ref<string>
  filteredRuns: ReturnType<typeof useAgentRuns>['filteredRuns']
  activeRunId: Ref<string | null | undefined>
  selectRun: (runId: string) => Promise<void>
  newChat: () => Promise<void>
  refreshRuns: () => Promise<void>
  setRunQuery: (runId?: string) => Promise<void>
}

const CHAT_SESSION_KEY: InjectionKey<IChatSessionNavContext> = Symbol('chatSession')

export function useChatSessionNav(deps: IChatSessionNavDeps): IChatSessionNavContext {
  const { t } = useI18n()
  const route = useRoute()
  const router = useRouter()

  const {
    isLoading: runsLoading,
    error: runsError,
    searchQuery,
    filteredRuns,
    loadRuns,
  } = useAgentRuns()

  const setActiveRunQuery = async (runId?: string) => {
    await router.replace({
      path: route.path,
      query: runId ? { run: runId } : {},
    })
  }

  const loadRunFromRoute = async (runId: string) => {
    try {
      await deps.loadRun(runId)
    } catch {
      toast.error(t('workspace.sessions.loadError'))
    }
  }

  const selectRun = async (runId: string) => {
    await loadRunFromRoute(runId)
    await setActiveRunQuery(runId)
  }

  const newChat = async () => {
    deps.clearChat()
    await setActiveRunQuery()
  }

  const refreshRuns = async () => {
    await loadRuns()
  }

  onMounted(async () => {
    await loadRuns()
    const runId = typeof route.query.run === 'string' ? route.query.run : null
    if (runId) {
      await loadRunFromRoute(runId)
    }
  })

  watch(
    () => route.query.run,
    async (runId) => {
      if (typeof runId === 'string' && runId !== deps.activeRunId.value) {
        await loadRunFromRoute(runId)
      }
    },
  )

  const context: IChatSessionNavContext = {
    runsLoading,
    runsError,
    searchQuery,
    filteredRuns,
    activeRunId: deps.activeRunId,
    selectRun,
    newChat,
    refreshRuns,
    setRunQuery: setActiveRunQuery,
  }

  provide(CHAT_SESSION_KEY, context)

  return context
}

export function useChatSessionNavContext(): IChatSessionNavContext {
  const context = inject(CHAT_SESSION_KEY)
  if (!context) {
    throw new Error('useChatSessionNavContext must be used within a page that calls useChatSessionNav')
  }
  return context
}
