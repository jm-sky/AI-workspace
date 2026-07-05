import { computed, type Reactive } from 'vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import type { IGearItemV2 } from '../types/gear.types.v2'

export const useIsContainerOwner = (container: Reactive<IGearItemV2>, defaultValue: boolean) => {
  const { user, isAuthenticated } = useAuth()

  const isOwner = computed(() => {
    if (!isAuthenticated.value || !user.value || !container) {
      return false
    }
    // For public containers, check authorId
    if (container.authorId) {
      return container.authorId === user.value.id
    }
    // For private containers (no authorId), if we can access the container,
    // it means we own it (backend handles authorization)
    // For localStorage, all containers are considered owned by current user
    return defaultValue
  })

  return isOwner
}
