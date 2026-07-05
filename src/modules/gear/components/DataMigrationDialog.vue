<script setup lang="ts">
import { CloudUpload, Database, Loader2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useHandleError } from '@/shared/composables/useHandleError'
import { useDataMigrationModal } from '../composables/useDataMigrationModal'
import { migrateLocalDataToAPI } from '../services/dataMigrationService'

const { t } = useI18n()
const { isOpen, close, handleSuccess, handleCancel } = useDataMigrationModal()
const { handleError } = useHandleError()
const isMigrating = ref(false)

const handleMigrate = async () => {
  isMigrating.value = true
  try {
    await migrateLocalDataToAPI()
    // Migration already updates the store, no need to refresh
    toast.success(t('gear.migration.success', 'Data migrated successfully!'))
    await handleSuccess()
  } catch (error) {
    console.error('Migration failed:', error)
    handleError(error, { fallbackMessage: t('gear.migration.error', 'Failed to migrate data. Please try again.') })
  } finally {
    isMigrating.value = false
  }
}

const handleSkip = () => {
  handleCancel()
}
</script>

<template>
  <Dialog :open="isOpen" @update:open="(open) => !open && close()">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Database class="size-5" />
          {{ t('gear.migration.title', 'Migrate Local Data?') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.migration.description', 'We found data stored locally. Would you like to migrate it to your account?') }}
        </DialogDescription>
      </DialogHeader>

      <div class="py-4 space-y-4">
        <div class="flex items-start gap-3 p-4 rounded-lg bg-muted/50">
          <CloudUpload class="size-5 mt-0.5 text-primary" />
          <div class="flex-1 space-y-1">
            <p class="text-sm font-medium">
              {{ t('gear.migration.benefits.title', 'Benefits of migration:') }}
            </p>
            <ul class="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              <li>{{ t('gear.migration.benefits.sync', 'Sync across all your devices') }}</li>
              <li>{{ t('gear.migration.benefits.backup', 'Automatic cloud backup') }}</li>
              <li>{{ t('gear.migration.benefits.access', 'Access from anywhere') }}</li>
            </ul>
          </div>
        </div>

        <div class="p-4 rounded-lg border border-border bg-background">
          <p class="text-sm text-muted-foreground">
            {{ t('gear.migration.note', 'Your local data will remain available even after migration. You can continue using the app offline.') }}
          </p>
        </div>
      </div>

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button
          type="button"
          variant="outline"
          class="sm:mr-auto"
          :disabled="isMigrating"
          @click="handleSkip"
        >
          {{ t('gear.migration.skip', 'Skip') }}
        </Button>
        <div class="flex gap-2">
          <Button
            type="button"
            variant="outline"
            :disabled="isMigrating"
            @click="close"
          >
            {{ t('common.cancel', 'Cancel') }}
          </Button>
          <Button
            type="button"
            :disabled="isMigrating"
            @click="handleMigrate"
          >
            <Loader2 v-if="isMigrating" class="size-4 animate-spin" />
            <CloudUpload v-else class="size-4" />
            {{ isMigrating ? t('gear.migration.migrating', 'Migrating...') : t('gear.migration.migrate', 'Migrate') }}
          </Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

