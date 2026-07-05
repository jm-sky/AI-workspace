/**
 * Data Migration Modal Composable
 * 
 * Global state management for data migration dialog that appears
 * after first login when local data exists.
 * 
 * Usage:
 * - After login: `useDataMigrationModal().checkAndOpen()`
 * - In App.vue: `<DataMigrationDialog />`
 */

import { ref } from 'vue'
import { hasLocalData } from '../services/dataMigrationService'

interface MigrationModalCallbacks {
  onSuccess?: () => void | Promise<void>
  onCancel?: () => void
}

// Global state (singleton pattern)
const isMigrationModalOpen = ref(false)
const migrationModalCallbacks = ref<MigrationModalCallbacks>({})
const hasShownMigrationPrompt = ref(false)

export function useDataMigrationModal() {
  /**
   * Open migration modal
   * @param callbacks - Optional callbacks for success/cancel
   */
  const open = (callbacks?: MigrationModalCallbacks) => {
    isMigrationModalOpen.value = true
    migrationModalCallbacks.value = callbacks ?? {}
  }
  
  /**
   * Close migration modal
   */
  const close = () => {
    isMigrationModalOpen.value = false
    migrationModalCallbacks.value = {}
  }
  
  /**
   * Check if migration should be prompted and open modal
   * Only shows once per session
   */
  const checkAndOpen = (callbacks?: MigrationModalCallbacks) => {
    // Only show once per session
    if (hasShownMigrationPrompt.value) {
      return false
    }
    
    // Check if local data exists
    if (!hasLocalData()) {
      return false
    }
    
    hasShownMigrationPrompt.value = true
    open(callbacks)
    return true
  }
  
  /**
   * Reset the "has shown" flag (useful for testing)
   */
  const reset = () => {
    hasShownMigrationPrompt.value = false
    close()
  }
  
  /**
   * Handle successful migration
   */
  const handleSuccess = async () => {
    await migrationModalCallbacks.value.onSuccess?.()
    close()
  }
  
  /**
   * Handle modal cancellation
   */
  const handleCancel = () => {
    migrationModalCallbacks.value.onCancel?.()
    close()
  }
  
  return {
    isOpen: isMigrationModalOpen,
    open,
    close,
    checkAndOpen,
    reset,
    handleSuccess,
    handleCancel,
  }
}

