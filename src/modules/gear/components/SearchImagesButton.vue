<script setup lang="ts">
import { Search } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import { imageSearchApiService } from '../services/imageSearchApiService'

const { t } = useI18n()
const { handleError } = useHandleError()

const { itemId } = defineProps<{
  itemId: string
}>()

const isSearchingImages = ref(false)

const emit = defineEmits<{
  reload: []
}>()

// Handle image search
const handleSearchImages = async () => {
  try {
    isSearchingImages.value = true

    // Search for images
    const response = await imageSearchApiService.searchImages({
      itemId: itemId,
    })

    if (response.results.length === 0 || !response.results[0]) {
      toast.info(t('gear.imageSearch.noResults', 'No images found'))
      return
    }

    // For now, just download and add the first result
    // TODO: In future, show dialog to select image (check, it should be done already)
    const firstResult = response.results[0]
    await imageSearchApiService.downloadAndAddImage({
      itemId: itemId,
      imageUrl: firstResult.imageUrl,
      sourceUrl: firstResult.sourceUrl,
      sourceName: firstResult.sourceName,
      searchEngineId: firstResult.searchEngineId,
      isPrimary: false,
    })

    toast.success(t('gear.imageSearch.imageAdded', 'Image added successfully'))

    // Reload page to show new image
    emit('reload')
  } catch (error: unknown) {
    console.error('Failed to search images:', error)
    handleError(error)
  } finally {
    isSearchingImages.value = false
  }
}
</script>

<template>
  <Button
    :loading="isSearchingImages"
    variant="outline"
    size="sm"
    @click="handleSearchImages"
  >
    <Search class="size-4" />
    {{ isSearchingImages ? t('gear.imageSearch.searching', 'Searching...') : t('gear.imageSearch.searchImages', 'Search Images') }}
  </Button>
</template>
