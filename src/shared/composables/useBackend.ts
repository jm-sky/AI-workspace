// shared/composables/useBackend.ts
import { computed } from 'vue'
import { config } from '@/shared/config/config'
import { JWT_STORE_KEY } from '@/shared/config/config'

/**
 * Composable to check if backend is enabled and if user is authenticated
 * 
 * @example
 * ```ts
 * const { isBackendEnabled, backendUrl, isAuthenticated, shouldUseAPI } = useBackend()
 * 
 * if (shouldUseAPI.value) {
 *   // Use backend API (backend enabled AND user authenticated)
 *   await apiClient.post('/auth/login', credentials)
 * } else {
 *   // Use localStorage (offline mode or not authenticated)
 *   localStorage.setItem('user', JSON.stringify(user))
 * }
 * ```
 */
export function useBackend() {
  const isBackendEnabled = computed(() => config.backend.enabled)
  const backendUrl = computed(() => config.backend.baseUrl)
  
  /**
   * Check if user has authentication token
   * Simple check - just verifies token exists in localStorage
   */
  const isAuthenticated = computed(() => {
    return !!localStorage.getItem(JWT_STORE_KEY)
  })
  
  /**
   * Should use API: backend enabled AND user authenticated
   * This is the main check for hybrid services (localStorage vs API)
   */
  const shouldUseAPI = computed(() => {
    return isBackendEnabled.value && isAuthenticated.value
  })

  return {
    isBackendEnabled,
    backendUrl,
    isAuthenticated,
    shouldUseAPI,
  }
}

