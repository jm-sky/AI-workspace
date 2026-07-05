<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const { t } = useI18n()

const open = defineModel<boolean>('open', { required: true })

defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
}>()

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  open.value = false
}
</script>

<template>
  <Dialog :open="open" @update:open="(value) => { open = value }">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.settings.ai.apiToken.confirmRemove.title') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.settings.ai.apiToken.confirmRemove.description') }}
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button
          variant="outline"
          :disabled="loading"
          @click="handleCancel"
        >
          {{ t('common.cancel') }}
        </Button>
        <Button
          variant="destructive"
          :disabled="loading"
          :loading="loading"
          @click="handleConfirm"
        >
          {{ t('common.delete') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

