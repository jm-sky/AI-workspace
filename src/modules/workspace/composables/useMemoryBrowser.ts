import { computed, ref } from 'vue'
import {
  createMemory,
  deleteMemory,
  listMemories,
  searchMemories,
} from '@/modules/workspace/services/memoryApiService'
import { getApiErrorMessage } from '@/shared/utils/apiError'
import type { IMemoryEntry, MemoryScope } from '@/modules/workspace/types/memory'

export function useMemoryBrowser() {
  const entries = ref<IMemoryEntry[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')
  const scopeFilter = ref<MemoryScope | 'all'>('all')
  const semanticResults = ref<IMemoryEntry[]>([])
  const isSemanticSearch = ref(false)

  const displayedEntries = computed(() => {
    if (isSemanticSearch.value) {
      return semanticResults.value
    }
    return entries.value
  })

  const loadEntries = async () => {
    isLoading.value = true
    error.value = null
    isSemanticSearch.value = false
    try {
      const response = await listMemories({
        scope: scopeFilter.value === 'all' ? undefined : scopeFilter.value,
        search: searchQuery.value.trim() || undefined,
        limit: 100,
        offset: 0,
      })
      entries.value = response.entries
      total.value = response.total
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Failed to load memories')
    } finally {
      isLoading.value = false
    }
  }

  const runSemanticSearch = async () => {
    const query = searchQuery.value.trim()
    if (!query) {
      await loadEntries()
      return
    }

    isLoading.value = true
    error.value = null
    try {
      semanticResults.value = await searchMemories({
        query,
        scope: scopeFilter.value === 'all' ? undefined : scopeFilter.value,
        limit: 20,
      })
      isSemanticSearch.value = true
      total.value = semanticResults.value.length
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Search failed')
    } finally {
      isLoading.value = false
    }
  }

  const addMemory = async (content: string, scope: MemoryScope = 'user') => {
    isSaving.value = true
    error.value = null
    try {
      await createMemory({ content, scope })
      await loadEntries()
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Failed to save memory')
      throw err
    } finally {
      isSaving.value = false
    }
  }

  const removeMemory = async (entryId: string) => {
    error.value = null
    try {
      await deleteMemory(entryId)
      entries.value = entries.value.filter((entry) => entry.id !== entryId)
      semanticResults.value = semanticResults.value.filter((entry) => entry.id !== entryId)
      total.value = Math.max(0, total.value - 1)
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Failed to delete memory')
      throw err
    }
  }

  return {
    entries,
    total,
    isLoading,
    isSaving,
    error,
    searchQuery,
    scopeFilter,
    displayedEntries,
    isSemanticSearch,
    loadEntries,
    runSemanticSearch,
    addMemory,
    removeMemory,
  }
}
