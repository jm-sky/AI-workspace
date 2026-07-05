import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export interface SearchPaginationUrlConfig {
  /**
   * Default page size
   */
  defaultPageSize?: number
  /**
   * Query parameter name for search (default: 'search')
   */
  searchParam?: string
  /**
   * Query parameter name for page (default: 'page')
   */
  pageParam?: string
  /**
   * Query parameter name for page size (default: 'pageSize')
   */
  pageSizeParam?: string
  /**
   * Keys to preserve in URL (like navigation params: returnTo, from)
   */
  preserveKeys?: string[]
}

/**
 * Composable for managing search and pagination state synchronized with URL
 */
export function useSearchPaginationUrl(config: SearchPaginationUrlConfig = {}) {
  const route = useRoute()
  const router = useRouter()

  const {
    defaultPageSize = 10,
    searchParam = 'search',
    pageParam = 'page',
    pageSizeParam = 'pageSize',
    preserveKeys = [],
  } = config

  // Parse URL query params
  const parseUrl = () => {
    const search = typeof route.query[searchParam] === 'string' ? route.query[searchParam] : ''
    const page = typeof route.query[pageParam] === 'string' ? parseInt(route.query[pageParam], 10) : 1
    const pageSize = typeof route.query[pageSizeParam] === 'string' ? parseInt(route.query[pageSizeParam], 10) : defaultPageSize

    return {
      search,
      page: isNaN(page) || page < 1 ? 1 : page,
      pageSize: isNaN(pageSize) || pageSize < 1 ? defaultPageSize : pageSize,
    }
  }

  // Initialize state from URL
  const urlParams = parseUrl()
  const search = ref<string>(urlParams.search)
  const page = ref<number>(urlParams.page)
  const pageSize = ref<number>(urlParams.pageSize)

  // Flag to prevent infinite loops
  let isUpdatingFromUrl = false

  // Sync state from URL
  const syncFromUrl = () => {
    if (isUpdatingFromUrl) return

    const urlParams = parseUrl()
    
    isUpdatingFromUrl = true
    search.value = urlParams.search
    page.value = urlParams.page
    pageSize.value = urlParams.pageSize
    
    nextTick(() => {
      isUpdatingFromUrl = false
    })
  }

  // Build query object from current state
  const buildQuery = () => {
    const query: Record<string, string | undefined> = {}

    // Add search
    if (search.value) {
      query[searchParam] = search.value
    }

    // Add page (only if > 1)
    if (page.value > 1) {
      query[pageParam] = String(page.value)
    }

    // Add page size (only if different from default)
    if (pageSize.value !== defaultPageSize) {
      query[pageSizeParam] = String(pageSize.value)
    }

    // Preserve navigation params
    preserveKeys.forEach((key) => {
      if (route.query[key] !== undefined) {
        query[key] = String(route.query[key])
      }
    })

    return query
  }

  // Update URL when state changes
  const stateWatchStopHandle = watch(
    [search, page, pageSize],
    () => {
      if (isUpdatingFromUrl) return

      const newQuery = buildQuery()
      router.replace({ query: newQuery }).catch(() => {
        // Ignore navigation errors
      })
    },
    { deep: true },
  )

  // Watch URL changes (browser back/forward, refresh, navigation)
  const urlWatchStopHandle = watch(
    () => route.query,
    () => {
      syncFromUrl()
    },
    { immediate: true, deep: true },
  )

  // Also watch route path changes to handle navigation back to this page
  const routePathWatchStopHandle = watch(
    () => route.path,
    () => {
      // Small delay to ensure route.query is updated
      nextTick(() => {
        syncFromUrl()
      })
    },
  )

  // Cleanup
  onBeforeUnmount(() => {
    stateWatchStopHandle()
    urlWatchStopHandle()
    routePathWatchStopHandle()
  })

  return {
    search,
    page,
    pageSize,
  }
}
