<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { itemImageApiService } from '@/modules/gear/services/itemImageApiService'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IGearItemV2 } from '../types/gear.types.v2'
import type { IItemImage } from '../types/itemImage.types'
import ContainerItemImageCard from './ContainerItemImageCard.vue'

const props = defineProps<{
  items: IGearItemV2[]
  containerId: string
  editable: boolean
  showItemImages?: boolean | null
}>()

const emit = defineEmits<{
  hide: []
}>()

const { t } = useI18n()
const { handleError } = useHandleError()

function handleHide() {
  emit('hide')
}

interface ItemWithImage {
  item: IGearItemV2
  image: IItemImage | null
}

const itemsWithImages = ref<ItemWithImage[]>([])
const isLoading = ref(false)
const imageLoadErrors = ref<Set<string>>(new Set())

// Get image for item: only primary image
async function getItemImage(itemId: string): Promise<IItemImage | null> {
  try {
    const images = await itemImageApiService.getImages(itemId)
    if (images.length === 0) return null

    // Only return primary image
    const primaryImage = images.find(img => img.isPrimary)
    return primaryImage ?? null
  } catch (error) {
    console.error(`Failed to load images for item ${itemId}:`, error)
    imageLoadErrors.value.add(itemId)
    return null
  }
}

// Filter items that have primary images, sort by order, and limit to 12
const itemsToShow = computed(() => {
  if (!props.showItemImages) {
    return []
  }

  // Return all items - we'll filter by primary image in loadImages
  return props.items.toSorted((a, b) => {
    // Sort by orderIndex (lower numbers first), then by name if orderIndex is the same
    const orderA = a.orderIndex ?? 0
    const orderB = b.orderIndex ?? 0
    if (orderA !== orderB) {
      return orderA - orderB
    }
    return a.name.localeCompare(b.name)
  })
})

async function loadImages() {
  if (!props.showItemImages || itemsToShow.value.length === 0) {
    itemsWithImages.value = []
    return
  }

  try {
    isLoading.value = true
    imageLoadErrors.value.clear()

    // Load images for all items in parallel
    const results = await Promise.all(
      itemsToShow.value.map(async (item) => {
        const image = await getItemImage(item.id)
        return { item, image }
      }),
    )

    // Filter out items without primary images and limit to 12
    itemsWithImages.value = results
      .filter(result => result.image !== null)
      .slice(0, 12)
  } catch (error) {
    console.error('Failed to load container images:', error)
    handleError(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadImages()
})

// Watch for changes in items - only track IDs and length to avoid deep watching
// This prevents reloading images when item properties change (name, category, etc.)
watch(() => props.items.map(i => i.id).join(','), () => {
  loadImages()
})
</script>

<template>
  <div v-if="showItemImages && itemsToShow.length > 0" class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold">
        {{ t('gear.container.itemImages.title', 'Item Images') }}
      </h3>
      <Button
        v-if="editable"
        v-tooltip.bottom="t('gear.container.hideItemImages', 'Hide item images')"
        :aria-label="t('gear.container.hideItemImages', 'Hide item images')"
        variant="ghost"
        size="sm"
        @click="handleHide"
      >
        <X class="size-4" />
      </Button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="flex flex-wrap gap-4">
      <div
        v-for="i in Math.min(itemsToShow.length, 12)"
        :key="i"
        class="w-full md:w-[calc(25%-1rem)] h-48 animate-pulse rounded-lg bg-muted"
      />
    </div>

    <!-- Image gallery -->
    <div v-else class="flex flex-wrap gap-4">
      <ContainerItemImageCard
        v-for="itemWithImage in itemsWithImages"
        :key="itemWithImage.item.id"
        :item="itemWithImage.item"
        :image="itemWithImage.image"
        :container-id="containerId"
        :has-error="imageLoadErrors.has(itemWithImage.item.id)"
      />
    </div>
  </div>
</template>

