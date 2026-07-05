import { computed } from 'vue'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useUserStore } from '@/modules/user/store/useUserStore'
import { usePermissions } from '@/shared/composables/usePermissions'
import { config } from '@/shared/config/config'

export const useAi = () => {
  const isEnabled = computed(() => config.features.ai.enabled)
  const { isAuthenticated } = useAuth()
  const { isPremium, isAdmin, isOwner } = usePermissions()
  const aiStore = useAiStore()
  const userStore = useUserStore()

  const canUseAi = computed<boolean>(() => {
    if (!isEnabled.value || !isAuthenticated.value) {
      return false
    }

    // Premium, Admin, or Owner can always use AI
    if (isPremium.value || isAdmin.value || isOwner.value) {
      return true
    }

    // Regular user: prioritize user features (from /me endpoint), fall back to store settings
    const userFeatures = userStore.user?.features
    const hasOwnTokenFromFeatures = userFeatures?.ai?.limit === null

    // Store settings may not be loaded yet during app initialization
    const hasOwnTokenFromStore = aiStore.settings?.hasToken ?? false

    return hasOwnTokenFromFeatures || hasOwnTokenFromStore
  })

  return {
    canUseAi,
  }
}
