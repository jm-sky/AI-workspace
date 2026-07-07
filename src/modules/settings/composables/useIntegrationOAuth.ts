import { ref } from 'vue'
import { integrationService } from '@/modules/settings/services/integrationService'
import type {
  IntegrationConnectRequest,
  IntegrationVisibilityScope,
} from '@/modules/settings/types/integration'

const INTEGRATION_OAUTH_STATE_KEY = 'integration_oauth_state'

export function useIntegrationOAuth() {
  const isPending = ref(false)
  const error = ref<Error | null>(null)

  const connect = async (payload: IntegrationConnectRequest) => {
    isPending.value = true
    error.value = null

    try {
      const response = await integrationService.getAuthUrl(payload)
      sessionStorage.setItem(INTEGRATION_OAUTH_STATE_KEY, response.state)
      window.location.href = response.authUrl
    }
    catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to start integration OAuth')
      isPending.value = false
    }
  }

  const getStoredState = (): string | null => {
    return sessionStorage.getItem(INTEGRATION_OAUTH_STATE_KEY)
  }

  const clearStoredState = () => {
    sessionStorage.removeItem(INTEGRATION_OAUTH_STATE_KEY)
  }

  return {
    clearStoredState,
    connect,
    error,
    getStoredState,
    isPending,
  }
}

export function defaultGithubScopes(): string[] {
  return ['read:user', 'repo']
}

export function visibilityLabelKey(scope: IntegrationVisibilityScope): string {
  return `settings.integrations.visibility.${scope}`
}
