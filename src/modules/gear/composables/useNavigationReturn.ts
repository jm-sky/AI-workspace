import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { GearRoutePath } from '../routes'
import { createNavigationQuery, getFrom, getReturnTo } from '../utils/navigationParams'

export function useNavigationReturn(containerId: string, itemId?: string) {
  const route = useRoute()
  const router = useRouter()

  const returnTo = computed(() => getReturnTo(route))
  const from = computed(() => getFrom(route))

  function navigateBack() {
    const returnToValue = returnTo.value
    const fromValue = from.value

    if (returnToValue === 'detail' && itemId) {
      router.push({
        path: GearRoutePath.ItemDetailById(containerId, itemId),
        query: createNavigationQuery(undefined, fromValue),
      })
    } else if (returnToValue === 'shopping') {
      router.push(GearRoutePath.ShoppingPlanning)
    } else {
      router.push(GearRoutePath.ContainerDetailById(containerId))
    }
  }

  async function navigateBackAndClean() {
    const returnToValue = returnTo.value
    const fromValue = from.value

    if (returnToValue === 'detail' && itemId) {
      // Preserve 'from' parameter when navigating back to ItemDetails
      // This ensures the back button in ItemHeader works correctly
      await router.push({
        path: GearRoutePath.ItemDetailById(containerId, itemId),
        query: createNavigationQuery(undefined, fromValue),
      })
    } else if (returnToValue === 'shopping') {
      await router.push(GearRoutePath.ShoppingPlanning)
    } else {
      await router.push({
        path: GearRoutePath.ContainerDetailById(containerId),
        query: {},
      })
    }
  }

  return {
    returnTo,
    from,
    navigateBack,
    navigateBackAndClean,
  }
}

