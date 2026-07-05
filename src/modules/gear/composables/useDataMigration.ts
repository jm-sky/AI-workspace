// modules/gear/composables/useDataMigration.ts
import { useBackend } from '@/shared/composables/useBackend'
import { logger } from '@/shared/utils/logger'
import { hasLocalData, migrateLocalDataToAPI, shouldPromptForMigration } from '../services/dataMigrationService'

/**
 * Composable for data migration from localStorage to API
 *
 * Usage:
 * ```ts
 * const { checkAndMigrate, hasLocalData, shouldPrompt } = useDataMigration()
 *
 * // After login, check if migration is needed
 * if (shouldPrompt.value) {
 *   // Show UI prompt to user
 *   await checkAndMigrate()
 * }
 * ```
 */
export function useDataMigration() {
  const { shouldUseAPI } = useBackend()

  /**
   * Check if local data exists
   */
  const hasLocalDataToMigrate = () => hasLocalData()

  /**
   * Check if migration should be prompted
   */
  const shouldPrompt = () => shouldPromptForMigration()

  /**
   * Migrate local data to API
   * Only works when backend is enabled and user is authenticated
   */
  const checkAndMigrate = async (): Promise<void> => {
    if (!shouldUseAPI.value) {
      logger.warn('Cannot migrate: backend not enabled or user not authenticated')
      return
    }

    if (!hasLocalData()) {
      logger.info('No local data to migrate')
      return
    }

    try {
      await migrateLocalDataToAPI()
    } catch (error) {
      console.error('Migration failed:', error)
      throw error
    }
  }

  return {
    hasLocalDataToMigrate,
    shouldPrompt,
    checkAndMigrate,
  }
}

