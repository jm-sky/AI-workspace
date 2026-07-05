<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CatalogueItemImageCardControls from './CatalogueItemImageCardControls.vue'
import type { ICatalogueItemImage } from '@/modules/gear/types/catalogueItemImage.types'
import type { TUUID } from '@/shared/types/base.type'

const props = defineProps<{
  image: ICatalogueItemImage
  index: number
  editable: boolean
  hasError: boolean
  isDragOver?: boolean
  isDragging?: boolean
}>()

const emit = defineEmits<{
  dragstart: [index: number]
  dragenter: [event: DragEvent, index: number]
  dragover: [event: DragEvent, index: number]
  dragleave: [event: DragEvent, index: number]
  dragend: []
  preview: [imageId: TUUID]
  togglePrimary: [imageId: TUUID]
  delete: [imageId: TUUID]
  imageError: [imageId: TUUID]
}>()

const { t } = useI18n()

function handleDragStart() {
  emit('dragstart', props.index)
}

function handleDragEnter(event: DragEvent) {
  emit('dragenter', event, props.index)
}

function handleDragOver(event: DragEvent) {
  emit('dragover', event, props.index)
}

function handleDragLeave(event: DragEvent) {
  const relatedTarget = event.relatedTarget as HTMLElement | null
  const currentTarget = event.currentTarget as HTMLElement | null

  if (currentTarget && relatedTarget && !currentTarget.contains(relatedTarget)) {
    emit('dragleave', event, props.index)
  }
}

function handleDragEnd() {
  emit('dragend')
}

function handleClick() {
  emit('preview', props.image.id)
}

function handleImageError() {
  emit('imageError', props.image.id)
}
</script>

<template>
  <div
    :draggable="editable"
    :class="[
      'group relative rounded-lg transition-all overflow-hidden cursor-pointer',
      isDragOver && 'outline-2 outline-dashed outline-offset-2 outline-primary',
      isDragging && 'opacity-50',
    ]"
    :style="isDragging ? { pointerEvents: 'auto' } : undefined"
    @dragend="handleDragEnd"
    @dragenter="handleDragEnter"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @dragstart="handleDragStart"
    @click="handleClick"
  >
    <div
      v-if="hasError"
      :class="isDragging ? 'pointer-events-none' : ''"
      class="flex h-48 items-center justify-center rounded-lg bg-muted"
    >
      <div class="text-center text-sm text-muted-foreground">
        <p>{{ t('common.error') }}</p>
        <p class="text-xs">
          {{ image.fileName }}
        </p>
      </div>
    </div>
    <img
      v-else
      :alt="image.fileName"
      :src="image.url"
      :class="isDragging ? 'pointer-events-none' : ''"
      class="size-full h-48 border border-border rounded-lg object-cover scale-100 group-hover:scale-105 transition-transform duration-300 shadow-md/5"
      @error="handleImageError"
    />

    <CatalogueItemImageCardControls
      v-if="editable"
      :class="isDragging ? 'pointer-events-none' : ''"
      :image
      @toggle-primary="emit('togglePrimary', $event)"
      @delete="emit('delete', $event)"
    />

    <div
      v-if="image.isPrimary"
      class="absolute left-2 top-2 rounded bg-yellow-400/80 px-2 py-1 text-xs font-semibold text-black backdrop-blur-sm"
    >
      {{ t('gear.fileUpload.imageGallery.primary') }}
    </div>
  </div>
</template>

