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
import ItemFormFields from '../ItemFormFields.vue'

const { t } = useI18n()

const { loading } = defineProps<{
  loading: boolean
}>()

const open = defineModel<boolean>('open', { required: true })

const emit = defineEmits<{
  submit: []
  cancel: []
}>()
</script>

<template>
  <Dialog :open>
    <DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{{ t('gear.shopping.addItem', 'Add') }}</DialogTitle>
        <DialogDescription>
          {{ t('gear.shopping.addItemDescription', 'Add a new item to your shopping list') }}
        </DialogDescription>
      </DialogHeader>
      <form @submit="emit('submit')">
        <ItemFormFields
          :item="undefined"
          :loading="loading"
          @cancel="emit('cancel')"
        />
        <DialogFooter>
          <Button
            variant="outline"
            type="button"
            @click="emit('cancel')"
          >
            {{ t('gear.actions.cancel', 'Cancel') }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
