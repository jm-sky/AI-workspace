<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import { Input } from '@/components/ui/input'
import { useCatalogueItemImage } from '@/modules/gear/composables/catalogue/useCatalogueItemImage'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { ICatalogueItemImage } from '@/modules/gear/types/catalogueItemImage.types'
import type { TUUID } from '@/shared/types/base.type'

const { t } = useI18n()
const { handleError } = useHandleError()
const { uploadImageFromUrl } = useCatalogueItemImage()

const images = defineModel<ICatalogueItemImage[]>('images', { required: true })
const imageLoadErrors = defineModel<Set<TUUID>>('imageLoadErrors', { required: true })

const { catalogueItemId } = defineProps<{
  catalogueItemId: TUUID
}>()

const imageUrl = ref('')
const isSubmittingUrl = ref(false)
const urlInputRef = ref<InstanceType<typeof Input> | null>(null)

const emit = defineEmits<{
  hide: []
}>()

onMounted(async () => {
  await nextTick()
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
    new URL(url)
  } catch {
    toast.error(t('gear.fileUpload.imageGallery.messages.urlInvalid'))
    return
  }

  try {
    isSubmittingUrl.value = true
    const hasPrimary = images.value.some(img => img.isPrimary)
    // SECURITY: catalogue images from URL are stored as external URLs (no server-side fetching)
    const newImage = await uploadImageFromUrl(catalogueItemId, url, !hasPrimary, false)
    images.value.push(newImage)
    imageLoadErrors.value.delete(newImage.id)
    toast.success(t('gear.fileUpload.imageGallery.messages.uploadSuccess'))
    imageUrl.value = ''
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

