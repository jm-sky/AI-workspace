<script setup lang="ts">
import { isAxiosError } from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import FileDropZone from '@/components/ui/FileDropZone.vue'
import CatalogueItemImageCard from '@/modules/gear/components/catalogue/CatalogueItemImageCard.vue'
import CatalogueItemImageGalleryUrlForm from '@/modules/gear/components/catalogue/CatalogueItemImageGalleryUrlForm.vue'
import CatalogueItemImagePreviewOverlay from '@/modules/gear/components/catalogue/CatalogueItemImagePreviewOverlay.vue'
import ItemImageGalleryEmptyState from '@/modules/gear/components/ItemImageGalleryEmptyState.vue'
import { useCatalogueItemImage } from '@/modules/gear/composables/catalogue/useCatalogueItemImage'
import { catalogueItemImageApiService } from '@/modules/gear/services/catalogueItemImageApiService'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { ICatalogueItemImage } from '@/modules/gear/types/catalogueItemImage.types'
import type { TUUID } from '@/shared/types/base.type'

const props = defineProps<{
  catalogueItemId: TUUID
  editable: boolean
}>()

const { t } = useI18n()
const { handleError } = useHandleError()
const { deleteImage, togglePrimaryImage, uploadImage } = useCatalogueItemImage()

const images = ref<ICatalogueItemImage[]>([])
const draggedImages = ref<ICatalogueItemImage[]>([])
const isLoading = ref(false)
const isDragging = ref(false)
const draggedIndex = ref(-1)
const dragOverIndex = ref<number | null>(null)
const imageLoadErrors = ref<Set<TUUID>>(new Set())

const isPreviewOpen = ref<boolean>(false)
const previewIndex = ref<number>(0)

const showUrlInput = ref(false)

const sortedImages = computed(() => {
  const source = isDragging.value ? draggedImages.value : images.value
  return [...source].sort((a, b) => a.order - b.order)
})

async function loadImages() {
  try {
    isLoading.value = true
    images.value = await catalogueItemImageApiService.getImages(props.catalogueItemId)
    imageLoadErrors.value.clear()
  } catch (error: unknown) {
    console.error(error)
    handleError(error)
  } finally {
    isLoading.value = false
  }
}

function toggleUrlInput() {
  showUrlInput.value = !showUrlInput.value
}

async function handleFilesSelected(files: File[]) {
  if (files.length === 0) return
  await uploadImages(files)
}

function handleDropZoneError(message: string) {
  toast.error(message)
}

async function uploadImages(files: File[]) {
  if (files.length === 0) return

  try {
    isLoading.value = true
    const hasPrimary = images.value.some(img => img.isPrimary)
    const uploadedImages: ICatalogueItemImage[] = []
    const errors: string[] = []

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (!file) continue

      try {
        const isPrimary = !hasPrimary && i === 0
        const newImage = await uploadImage(props.catalogueItemId, file, isPrimary)
        uploadedImages.push(newImage)
        images.value.push(newImage)
      } catch (error: unknown) {
        const message = isAxiosError(error) ? error.response?.data?.detail : null
        const errorMessage = message ?? t('gear.fileUpload.imageGallery.messages.uploadFailed')
        errors.push(`${file.name}: ${errorMessage}`)
        console.error(`Failed to upload ${file.name}:`, error)
      }
    }

    if (uploadedImages.length > 0) {
      toast.success(
        uploadedImages.length === 1
          ? t('gear.fileUpload.imageGallery.messages.uploadSuccess')
          : t('gear.fileUpload.imageGallery.messages.uploadSuccessMultiple', { count: uploadedImages.length }),
      )
    }

    if (errors.length > 0) {
      toast.error(errors.join(', '))
    }
  } catch (error: unknown) {
    console.error(error)
    handleError(error)
  } finally {
    isLoading.value = false
  }
}

async function handleDeleteImage(imageId: TUUID) {
  if (!confirm(t('gear.fileUpload.imageGallery.confirmDelete'))) {
    return
  }

  try {
    await deleteImage(props.catalogueItemId, imageId)
    images.value = images.value.filter(img => img.id !== imageId)
    imageLoadErrors.value.delete(imageId)
    toast.success(t('gear.fileUpload.imageGallery.messages.deleteSuccess'))
  } catch (error: unknown) {
    console.error(error)
    handleError(error)
  }
}

async function handleTogglePrimary(imageId: TUUID) {
  try {
    const isPrimary = await togglePrimaryImage(props.catalogueItemId, imageId)
    images.value = images.value.map(img => ({
      ...img,
      isPrimary: img.id === imageId ? isPrimary : false,
    }))
    toast.success(isPrimary ? t('gear.fileUpload.imageGallery.messages.primarySuccess') : t('gear.fileUpload.imageGallery.messages.primaryUnset'))
  } catch (error: unknown) {
    console.error(error)
    handleError(error)
  }
}

const initialDragIndex = ref(-1)

function handleDragStart(index: number) {
  draggedIndex.value = index
  initialDragIndex.value = index
  const currentSorted = [...images.value].sort((a, b) => a.order - b.order)
  draggedImages.value = currentSorted
  isDragging.value = true
}

function handleDragEnter(event: DragEvent, index: number) {
  event.preventDefault()
  if (draggedIndex.value === index || draggedIndex.value === -1) {
    return
  }
  dragOverIndex.value = index
}

function handleDragLeave(event: DragEvent, index: number) {
  const relatedTarget = event.relatedTarget as HTMLElement | null
  const currentTarget = event.currentTarget as HTMLElement | null

  if (currentTarget && relatedTarget && !currentTarget.contains(relatedTarget)) {
    if (dragOverIndex.value === index) {
      dragOverIndex.value = null
    }
  }
}

function handleDragOver(event: DragEvent, index: number) {
  event.preventDefault()
  if (draggedIndex.value === index || draggedIndex.value === -1) {
    return
  }

  if (dragOverIndex.value !== index) {
    dragOverIndex.value = index
  }

  const newOrder = [...draggedImages.value]
  const draggedItem = newOrder[draggedIndex.value]
  if (!draggedItem) return

  newOrder.splice(draggedIndex.value, 1)
  newOrder.splice(index, 0, draggedItem)

  draggedImages.value = newOrder
  draggedIndex.value = index
}

async function handleDragEnd() {
  isDragging.value = false
  dragOverIndex.value = null

  if (draggedIndex.value === -1 || initialDragIndex.value === -1) {
    draggedIndex.value = -1
    initialDragIndex.value = -1
    draggedImages.value = []
    return
  }

  const originalOrder = [...images.value].sort((a, b) => a.order - b.order).map(img => img.id)
  const newOrder = draggedImages.value.map(img => img.id)
  const orderChangedByIds = JSON.stringify(originalOrder) !== JSON.stringify(newOrder)

  if (!orderChangedByIds) {
    draggedIndex.value = -1
    initialDragIndex.value = -1
    draggedImages.value = []
    return
  }

  const finalOrder = draggedImages.value.map((img, index) => ({ id: img.id, order: index }))

  try {
    await catalogueItemImageApiService.reorderImages(props.catalogueItemId, finalOrder)
    images.value = draggedImages.value.map((img, index) => ({ ...img, order: index }))
    toast.success(t('gear.fileUpload.imageGallery.messages.reorderSuccess'))
  } catch (error: unknown) {
    console.error(error)
    handleError(error)
    await loadImages()
  } finally {
    draggedIndex.value = -1
    initialDragIndex.value = -1
    draggedImages.value = []
  }
}

function handleImageError(imageId: TUUID) {
  imageLoadErrors.value.add(imageId)
}

function handleImagePreview(imageId: TUUID) {
  const index = sortedImages.value.findIndex(img => img.id === imageId)
  if (index === -1) return
  previewIndex.value = index
  isPreviewOpen.value = true
}

onMounted(() => {
  loadImages()
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-row items-center justify-between gap-2">
      <h3 class="text-lg font-semibold">
        {{ t('gear.fileUpload.imageGallery.title') }}
      </h3>
      <div class="flex flex-row gap-2 items-center justify-end">
        <Button
          v-if="editable"
          size="sm"
          variant="outline"
          :disabled="isLoading"
          @click="toggleUrlInput"
        >
          {{ t('gear.fileUpload.imageGallery.addFromUrl') }}
        </Button>
      </div>
    </div>

    <CatalogueItemImageGalleryUrlForm
      v-if="editable && showUrlInput"
      v-model:images="images"
      v-model:image-load-errors="imageLoadErrors"
      :catalogue-item-id="catalogueItemId"
      @hide="toggleUrlInput"
    />

    <div v-if="isLoading && images.length === 0" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      <div
        v-for="i in 4"
        :key="i"
        class="h-48 animate-pulse rounded-lg bg-muted"
      />
    </div>

    <div v-else class="flex flex-wrap gap-4">
      <ItemImageGalleryEmptyState v-if="images.length === 0" />

      <CatalogueItemImageCard
        v-for="(image, index) in sortedImages"
        :key="image.id"
        :image
        :index
        :editable
        :has-error="imageLoadErrors.has(image.id)"
        :is-drag-over="isDragging && dragOverIndex === index"
        :is-dragging="isDragging && draggedIndex === index"
        class="w-full md:w-[calc(25%-1rem)]"
        @dragend="handleDragEnd"
        @dragenter="handleDragEnter"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @dragstart="handleDragStart"
        @preview="handleImagePreview"
        @toggle-primary="handleTogglePrimary"
        @delete="handleDeleteImage"
        @image-error="handleImageError"
      />

      <FileDropZone
        v-if="editable"
        :disabled="isLoading"
        :max-files="10"
        accept="image/jpeg,image/png,image/webp,image/gif"
        class="min-h-32 flex-1"
        @error="handleDropZoneError"
        @files-selected="handleFilesSelected"
      />
    </div>

    <CatalogueItemImagePreviewOverlay
      v-if="sortedImages.length > 0"
      v-model:open="isPreviewOpen"
      v-model:index="previewIndex"
      :images="sortedImages"
    />
  </div>
</template>

