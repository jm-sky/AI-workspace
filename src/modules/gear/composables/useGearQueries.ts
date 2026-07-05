/**
 * TanStack Query hooks for gear data fetching
 * 
 * Provides reactive data fetching with automatic caching, refetching, and loading states.
 * 
 * @module gear/composables/queries
 */

import { useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/vue-query'
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { gearItemApiServiceV2 } from '../services/gearItemApiServiceV2'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { gearQueryKeys } from '../utils/queryKeys'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Fetch all root containers
 * 
 * Use for ContainersListPage - fetches only top-level containers without children.
 */
export function useContainers(options?: Partial<UseQueryOptions<IGearItemV2[]>>) {
  const store = useGearStoreV2()
  
  return useQuery({
    queryKey: gearQueryKeys.itemsFiltered({ itemType: 'container', parentItemId: null }),
    queryFn: async () => {
      const containers = await gearItemApiServiceV2.getItems({ 
        itemType: 'container', 
        parentItemId: null 
      })
      // Update store with fetched containers
      store.upsertItems(containers)
      return containers
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  })
}

/**
 * Fetch a single container by ID
 * 
 * @param id - Container ID (can be ref or getter)
 * @param options - Additional query options
 */
export function useContainer(
  id: MaybeRefOrGetter<TUUID | undefined>,
  options?: Partial<UseQueryOptions<IGearItemV2 | undefined>>
) {
  const store = useGearStoreV2()
  
  return useQuery({
    queryKey: computed(() => {
      const containerId = toValue(id)
      return containerId ? gearQueryKeys.container(containerId) : ['disabled']
    }),
    queryFn: async () => {
      const containerId = toValue(id)
      if (!containerId) return undefined
      
      const container = await gearItemApiServiceV2.getItemById(containerId)
      if (container) {
        store.upsertItem(container)
      }
      return container
    },
    enabled: computed(() => !!toValue(id)),
    staleTime: 5 * 60 * 1000, // 5 minutes
    placeholderData: computed(() => {
      const containerId = toValue(id)
      return containerId ? store.getItemById(containerId) : undefined
    }),
    ...options,
  })
}

/**
 * Fetch children of a container
 * 
 * @param parentId - Parent container ID (can be ref or getter)
 * @param options - Additional query options
 */
export function useContainerChildren(
  parentId: MaybeRefOrGetter<TUUID | undefined>,
  options?: Partial<UseQueryOptions<IGearItemV2[]>>
) {
  const store = useGearStoreV2()
  
  return useQuery({
    queryKey: computed(() => {
      const parent = toValue(parentId)
      return parent ? gearQueryKeys.children(parent) : ['disabled']
    }),
    queryFn: async () => {
      const parent = toValue(parentId)
      if (!parent) return []
      
      const children = await gearItemApiServiceV2.getChildren(parent)
      store.upsertItems(children)
      return children
    },
    enabled: computed(() => !!toValue(parentId)),
    staleTime: 5 * 60 * 1000, // 5 minutes
    placeholderData: computed(() => {
      const parent = toValue(parentId)
      return parent ? store.getChildrenOfItem(parent) : []
    }),
    ...options,
  })
}

/**
 * Fetch container with all its children in parallel
 * 
 * Optimized for ContainerDetailPage - fetches both container and children
 * in parallel for better performance.
 * 
 * @param id - Container ID (can be ref or getter)
 */
export function useContainerWithChildren(id: MaybeRefOrGetter<TUUID | undefined>) {
  const containerQuery = useContainer(id)
  const childrenQuery = useContainerChildren(id)
  
  return {
    container: containerQuery.data,
    children: childrenQuery.data,
    isLoading: computed(() => containerQuery.isLoading.value || childrenQuery.isLoading.value),
    isError: computed(() => containerQuery.isError.value || childrenQuery.isError.value),
    error: computed(() => containerQuery.error.value || childrenQuery.error.value),
  }
}

/**
 * Fetch all containers with their children for statistics
 * 
 * Use for ContainersListPage when statistics (weight, readiness) are needed.
 * Fetches all containers first, then fetches children for each container in parallel.
 */
export function useContainersWithChildren(options?: Partial<UseQueryOptions<IGearItemV2[]>>) {
  const store = useGearStoreV2()
  const queryClient = useQueryClient()
  
  // First fetch all containers
  const containersQuery = useContainers(options)
  
  // When containers are loaded, prefetch children for each container
  const containers = computed(() => containersQuery.data.value ?? [])
  
  // Prefetch children for all containers (runs in background)
  containers.value.forEach(container => {
    queryClient.prefetchQuery({
      queryKey: gearQueryKeys.children(container.id),
      queryFn: async () => {
        const children = await gearItemApiServiceV2.getChildren(container.id)
        store.upsertItems(children)
        return children
      },
      staleTime: 5 * 60 * 1000,
    })
  })
  
  return containersQuery
}
