<script setup lang="ts">
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import ItemImagePreviewOverlayButton from './ItemImagePreviewOverlayButton.vue'
import type { IItemImage } from '@/modules/gear/types/itemImage.types'

const { images } = defineProps<{
  images: IItemImage[]
}>()

const { t } = useI18n()

const open = defineModel<boolean>('open', { required: true })
const index = defineModel<number>('index', { required: true })

const activeImage = computed<IItemImage | null>(() => {
  if (!images.length) return null

  const safeIndex = Math.min(Math.max(index.value, 0), images.length - 1)
  return images[safeIndex] ?? null
})

const closePreview = () => open.value = false

function showNext() {
  if (!images.length) return

  index.value = (index.value + 1) % images.length
}

function showPrevious() {
  if (!images.length) return

  index.value = (index.value - 1 + images.length) % images.length
}
</script>

<template>
  <Teleport to="body">
    <transition name="fade">
      <div
        v-if="open && activeImage"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        @click.self="closePreview"
      >
        <div class="flex h-full w-full max-w-5xl flex-col px-4 py-6 sm:px-6">
          <div class="mb-4 flex items-center justify-between text-sm text-muted-foreground">
            <span class="truncate">
              {{ activeImage.fileName }}
            </span>
            <span v-if="images.length > 1" class="shrink-0">
              {{ index + 1 }} / {{ images.length }}
            </span>
          </div>

          <div class="relative flex flex-1 items-center justify-center">
            <ItemImagePreviewOverlayButton
              v-if="images.length > 1"
              class="left-2 sm:left-4"
              :aria-label="t('gear.fileUpload.imageGallery.previousImage', 'Previous image')"
              @click.stop="showPrevious"
            >
              <ChevronLeft class="size-5" />
            </ItemImagePreviewOverlayButton>

            <img
              :src="activeImage.url"
              :alt="activeImage.fileName"
              class="max-h-[80vh] max-w-full rounded-md border border-border object-contain shadow-xl"
            />

            <ItemImagePreviewOverlayButton
              v-if="images.length > 1"
              class="right-2 sm:right-4"
              :aria-label="t('gear.fileUpload.imageGallery.nextImage', 'Next image')"
              @click.stop="showNext"
            >
              <ChevronRight class="size-5" />
            </ItemImagePreviewOverlayButton>
          </div>

          <div class="mt-4 flex items-center justify-end gap-2">
            <Button
              size="sm"
              variant="secondary"
              @click="closePreview"
            >
              {{ t('common.close') }}
            </Button>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>


