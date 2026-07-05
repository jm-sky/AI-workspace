<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { UPDATE_FROM_CATALOGUE_FIELDS_KEY } from '@/shared/config/config'
import type { IGearItemV2 } from '../../types/gear.types.v2'
import { useCatalogue } from '../../composables/catalogue/useCatalogue'

const { t } = useI18n()
const { updateItemFromCatalogue, isUpdatingFromCatalogue } = useCatalogue()

const open = defineModel<boolean>('open', { default: false })

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  itemUpdated: []
}>()

type FieldKey = 'name' | 'description' | 'weight' | 'weightUnit' | 'price' | 'currency' | 'brand' | 'color' | 'category' | 'quality' | 'url'

// Available fields that can be updated from catalogue
const availableFields = computed(() => [
  { key: 'name' as FieldKey, label: t('gear.item.name') },
  { key: 'description' as FieldKey, label: t('gear.catalogue.description') },
  { key: 'weight' as FieldKey, label: t('gear.catalogue.weightWithUnit') },
  { key: 'price' as FieldKey, label: t('gear.catalogue.priceWithCurrency') },
  { key: 'brand' as FieldKey, label: t('gear.item.brand') },
  { key: 'color' as FieldKey, label: t('gear.item.color') },
  { key: 'category' as FieldKey, label: t('gear.item.category') },
  { key: 'quality' as FieldKey, label: t('gear.item.quality') },
  { key: 'url' as FieldKey, label: t('gear.item.url') },
])

// Load selected fields from localStorage
const loadSelectedFields = (): FieldKey[] => {
  try {
    const stored = localStorage.getItem(UPDATE_FROM_CATALOGUE_FIELDS_KEY)
    if (stored) {
      const parsed = JSON.parse(stored) as FieldKey[]
      // Validate that all fields are valid
      const validFields: FieldKey[] = ['name', 'description', 'weight', 'weightUnit', 'price', 'currency', 'brand', 'color', 'category', 'quality', 'url']
      return parsed.filter(field => validFields.includes(field))
    }
  } catch (error) {
    console.error('Failed to load selected fields from localStorage:', error)
  }
  // Default: weight (with unit), price (with currency), color, brand, quality, url
  return ['weight', 'weightUnit', 'price', 'currency', 'color', 'brand', 'quality', 'url']
}

// Save selected fields to localStorage
const saveSelectedFields = (fields: FieldKey[]) => {
  try {
    localStorage.setItem(UPDATE_FROM_CATALOGUE_FIELDS_KEY, JSON.stringify(fields))
  } catch (error) {
    console.error('Failed to save selected fields to localStorage:', error)
  }
}

const selectedFields = ref<FieldKey[]>(loadSelectedFields())

// Update localStorage when selection changes
const toggleField = (fieldKey: FieldKey) => {
  if (selectedFields.value.includes(fieldKey)) {
    selectedFields.value = selectedFields.value.filter(f => f !== fieldKey)
  } else {
    selectedFields.value = [...selectedFields.value, fieldKey]
  }
  saveSelectedFields(selectedFields.value)
}

const handleConfirm = async () => {
  if (selectedFields.value.length === 0) {
    return
  }

  try {
    await updateItemFromCatalogue(props.item.id, selectedFields.value)
    toast.success(t('gear.catalogue.updatedFromCatalogue'))
    emit('itemUpdated')
    open.value = false
  } catch (error) {
    console.error('Failed to update item from catalogue:', error)
    toast.error(t('common.error'))
  }
}

const canSubmit = computed<boolean>(() => {
  return selectedFields.value.length > 0 && !isUpdatingFromCatalogue.value
})
</script>

<template>
  <Dialog :open="open" @update:open="open = $event">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.catalogue.updateFromCatalogue') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.catalogue.selectFieldsToUpdate') }}
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-3 py-4">
        <div
          v-for="field in availableFields"
          :key="field.key"
          class="flex items-center space-x-2"
        >
          <Checkbox
            :id="`field-${field.key}`"
            :checked="selectedFields.includes(field.key)"
            @update:checked="toggleField(field.key)"
          />
          <Label
            :for="`field-${field.key}`"
            class="cursor-pointer text-sm font-normal"
          >
            {{ field.label }}
          </Label>
        </div>
      </div>

      <DialogFooter>
        <Button
          variant="outline"
          :disabled="isUpdatingFromCatalogue"
          @click="open = false"
        >
          {{ t('gear.actions.cancel') }}
        </Button>
        <Button
          :disabled="!canSubmit"
          :loading="isUpdatingFromCatalogue"
          @click="handleConfirm"
        >
          {{ t('gear.catalogue.update') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
