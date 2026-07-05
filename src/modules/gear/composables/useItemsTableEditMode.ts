import { ref, watch } from 'vue'
import { ITEMS_TABLE_EDIT_MODE_KEY } from '@/shared/config/config'

// Singleton state - shared across all components
let editModeState: ReturnType<typeof ref<boolean>> | null = null

function loadEditMode(): boolean {
  try {
    const stored = localStorage.getItem(ITEMS_TABLE_EDIT_MODE_KEY)
    return stored === 'true'
  } catch (error) {
    console.error('Error loading edit mode from storage:', error)
    return false
  }
}

/**
 * Composable for managing items table edit mode state
 * Persists edit mode preference in localStorage
 * Uses singleton pattern to share state across all components
 */
export function useItemsTableEditMode() {
  // Initialize singleton state if not exists
  if (!editModeState) {
    editModeState = ref<boolean>(loadEditMode())

    // Save to localStorage when editMode changes
    watch(
      editModeState,
      (newValue) => {
        try {
          localStorage.setItem(ITEMS_TABLE_EDIT_MODE_KEY, String(newValue))
        } catch (error) {
          console.error('Error saving edit mode to storage:', error)
        }
      },
      { immediate: false },
    )
  }

  function toggleEditMode() {
    if (editModeState) {
      editModeState.value = !editModeState.value
    }
  }

  return {
    editMode: editModeState,
    toggleEditMode,
  }
}

