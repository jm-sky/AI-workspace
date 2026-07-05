import { ref } from 'vue'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '../types/gear.types.v2'
import { useGearV2 } from './useGearV2'

/**
 * Composable for inline item editing (V2)
 * Handles save on blur and Enter
 */
export function useInlineItemEditingV2(item: IGearItemV2) {
  const { updateItem } = useGearV2()
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Save function
  async function save(updates: IUpdateGearItemV2Dto): Promise<IGearItemV2 | null> {
    isLoading.value = true
    error.value = null

    try {
      const updated = await updateItem(item.id, updates)
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Failed to update item')
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    save, // Save function for blur and Enter
  }
}
