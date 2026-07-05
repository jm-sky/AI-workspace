<script setup lang="ts">
import { AlertCircle, Save, X } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import type { IGearItemV2 } from '../types/gear.types.v2'

const props = defineProps<{
  pendingItems: IGearItemV2[]
  loading?: boolean
}>()

const emit = defineEmits<{
  save: [items: IGearItemV2[]]
  cancel: []
}>()

const { t } = useI18n()

const itemCount = computed(() => props.pendingItems.length)

function handleSave() {
  emit('save', props.pendingItems)
}

function handleCancel() {
  emit('cancel')
}
</script>

<template>
  <Alert
    v-if="pendingItems.length > 0"
    variant="info"
    class="mb-4"
  >
    <AlertCircle />
    <AlertTitle>
      {{ t('gear.sorting.unsavedChanges', 'Unsaved sorting changes') }}
    </AlertTitle>
    <AlertDescription>
      {{ t('gear.sorting.unsavedChangesDescription', { count: itemCount }, `You have reordered ${itemCount} item(s). Save changes to update the order in the database?`) }}
    </AlertDescription>
    <div class="flex gap-2 mt-3">
      <Button
        size="sm"
        :disabled="loading"
        @click="handleSave"
      >
        <Save class="size-4" />
        {{ t('common.save', 'Save') }}
      </Button>
      <Button
        size="sm"
        variant="outline"
        :disabled="loading"
        @click="handleCancel"
      >
        <X class="size-4" />
        {{ t('common.cancel', 'Cancel') }}
      </Button>
    </div>
  </Alert>
</template>
