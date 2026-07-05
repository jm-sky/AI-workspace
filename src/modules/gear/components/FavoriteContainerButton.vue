<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearV2 } from '../composables/useGearV2'
import FavoriteStarIcon from './FavoriteStarIcon.vue'

const { t } = useI18n()
const { updateItem } = useGearV2()
const { handleError } = useHandleError()

const { container } = defineProps<{
  container: IGearItemV2
}>()

const handleToggleFavorite = async () => {
  try {
    const newFavoriteStatus = !container.favorite
    await updateItem(container.id, {
      favorite: newFavoriteStatus,
    })
    toast.success(
      newFavoriteStatus
        ? t('gear.container.favoriteAdded')
        : t('gear.container.favoriteRemoved'),
    )
  } catch (error) {
    console.error('Failed to update favorite status:', error)
    handleError(error)
  }
}
</script>

<template>
  <Button
    v-tooltip.bottom="container.favorite ? t('gear.container.removeFavorite') : t('gear.container.addFavorite')"
    variant="ghost"
    size="sm"
    :aria-label="container.favorite ? t('gear.container.removeFavorite') : t('gear.container.addFavorite')"
    @click.stop="handleToggleFavorite"
  >
    <FavoriteStarIcon :favorite="container.favorite ?? false" />
  </Button>
</template>
