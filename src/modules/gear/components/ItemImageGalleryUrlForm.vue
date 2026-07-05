<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { useItemImage } from '@/modules/gear/composables/useItemImage'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IItemImage } from '../types/itemImage.types'
import type { TUUID } from '@/shared/types/base.type'

const { t } = useI18n()
const { handleError } = useHandleError()
const { uploadImageFromUrl: uploadImageFromUrlWithUpdate } = useItemImage()

const images = defineModel<IItemImage[]>('images', { required: true })
const imageLoadErrors = defineModel<Set<TUUID>>('imageLoadErrors', { required: true })

const { itemId } = defineProps<{
  itemId: TUUID
}>()

const imageUrl = ref('')
const hostOption = ref<'local' | 'external'>('local') // Default: host locally (download and store)
const isSubmittingUrl = ref(false)
const urlInputRef = ref<InstanceType<typeof Input> | null>(null)

const emit = defineEmits<{
  hide: []
}>()

onMounted(async () => {
  await nextTick()
  // Focus the input when component is mounted (when form is shown)
  const inputElement = urlInputRef.value?.$el
  if (inputElement && inputElement instanceof HTMLInputElement) {
    inputElement.focus()
  }
})

async function handleAddFromUrl() {
  const url = imageUrl.value.trim()
  if (!url) {
    toast.error(t('gear.fileUpload.imageGallery.messages.urlRequired'))
    return
  }

  try {
    // Basic URL validation

    new URL(url)
  } catch {
    toast.error(t('gear.fileUpload.imageGallery.messages.urlInvalid'))
    return
  }

  try {
    isSubmittingUrl.value = true
    const hasPrimary = images.value.some(img => img.isPrimary)
    const hostLocally = hostOption.value === 'local'
    // Use composable that updates both API and Pinia store
    const newImage = await uploadImageFromUrlWithUpdate(itemId, url, !hasPrimary, hostLocally)
    images.value.push(newImage)
    imageLoadErrors.value.delete(newImage.id)
    toast.success(t('gear.fileUpload.imageGallery.messages.uploadSuccess'))
    imageUrl.value = ''
    hostOption.value = 'local' // Reset to default
    emit('hide')
  } catch (error: unknown) {
    handleError(error, { fallbackMessage: t('gear.fileUpload.imageGallery.messages.uploadFailed') })
  } finally {
    isSubmittingUrl.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-3 rounded-lg border bg-muted/40 p-3">
    <Input
      ref="urlInputRef"
      :model-value="imageUrl"
      :placeholder="t('gear.fileUpload.imageGallery.urlPlaceholder')"
      type="url"
      autocomplete="off"
      class="w-full"
      @update:model-value="value => (imageUrl = (value as string))"
    />
    <div class="flex flex-col gap-2">
      <Label class="text-sm font-medium">
        {{ t('gear.fileUpload.imageGallery.hostOption') }}
      </Label>
      <RadioGroup v-model="hostOption" class="flex gap-4">
        <div class="flex items-center gap-2">
          <RadioGroupItem id="host-locally" value="local" />
          <Label for="host-locally" class="text-sm font-normal cursor-pointer">
            {{ t('gear.fileUpload.imageGallery.hostLocally') }}
          </Label>
        </div>
        <div class="flex items-center gap-2">
          <RadioGroupItem id="host-externally" value="external" />
          <Label for="host-externally" class="text-sm font-normal cursor-pointer">
            {{ t('gear.fileUpload.imageGallery.hostExternally') }}
          </Label>
        </div>
      </RadioGroup>
    </div>
    <div class="flex gap-2 justify-end pt-2">
      <Button
        variant="outline"
        size="sm"
        :disabled="isSubmittingUrl"
        @click="emit('hide')"
      >
        {{ t('common.cancel', 'Cancel') }}
      </Button>
      <Button
        size="sm"
        :disabled="isSubmittingUrl"
        @click="handleAddFromUrl"
      >
        {{ t('gear.fileUpload.imageGallery.addFromUrl') }}
      </Button>
    </div>
  </div>
</template>
