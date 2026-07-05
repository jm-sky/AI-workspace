<script setup lang="ts">
import { BookIcon, ImageIcon, Link2Off, MoreHorizontalIcon, MoveIcon, Sparkles, ThumbsUp } from 'lucide-vue-next'
import { computed, defineAsyncComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useCatalogue } from '../composables/catalogue/useCatalogue'
import { useItemPromotion } from '../composables/promotion/useItemPromotion'
import { useGearMutations } from '../composables/useGearMutations'
import { getActionIcon } from '../utils/actionIcons'
import MoveItemDialog from './MoveItemDialog.vue'

// Lazy load dialog to reduce initial bundle size
const UpdateFromCatalogueDialog = defineAsyncComponent(() => import('./catalogue/UpdateFromCatalogueDialog.vue'))

const { t } = useI18n()
const { user } = useAuth()
const { fetchImagesFromCatalogue, unlinkItemFromCatalogue, isFetchingImages, isUnlinking } = useCatalogue()
const { moveItem } = useGearMutations()
const { addToCatalogue, isAddingToCatalogue } = useItemPromotion(computed(() => item.id))

const matchDialogOpen = defineModel<boolean>('matchDialogOpen', { default: false })
const updateDialogOpen = ref(false)
const moveDialogOpen = ref(false)

const { item } = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  itemUpdated: []
  delete: []
}>()

const DeleteIcon = getActionIcon('delete')

const isAdmin = computed(() => user.value?.isAdmin ?? false)

const handleAddToCatalogue = async () => {
  try {
    await addToCatalogue()
    emit('itemUpdated')
  } catch (error) {
    console.error('Failed to add item to catalogue:', error)
  }
}

const handleMatchWithCatalogue = () => {
  matchDialogOpen.value = true
}

const handleUpdateFromCatalogue = () => {
  if (!item.catalogueItemId) return
  updateDialogOpen.value = true
}

const handleFetchImagesFromCatalogue = async () => {
  if (!item.catalogueItemId) return

  // Show loading toast
  const loadingToast = toast.loading(
    t('gear.fileUpload.imageGallery.messages.fetchingImages', 'Fetching images...'),
  )

  try {
    // Mutacja już odświeża kontener w store, ale musimy odświeżyć item w ItemDetailPage
    // Mutacja zwraca zaktualizowany item, więc możemy go użyć bezpośrednio
    await fetchImagesFromCatalogue(item.id)
    toast.success(t('gear.catalogue.fetchedImagesFromCatalogue'), {
      id: loadingToast,
    })
    // Emit itemUpdated, aby ItemDetailPage odświeżył dane
    emit('itemUpdated')
  } catch (error) {
    console.error('Failed to fetch images from catalogue:', error)
    toast.error(t('common.error'), {
      id: loadingToast,
    })
  }
}

const handleUnlinkFromCatalogue = async () => {
  if (!item.catalogueItemId) return

  try {
    await unlinkItemFromCatalogue(item.id)
    toast.success(t('gear.catalogue.unlinkedSuccess'))
    emit('itemUpdated')
  } catch (error) {
    console.error('Failed to unlink item from catalogue:', error)
    toast.error(t('common.error'))
  }
}

const handleMoveItem = () => {
  moveDialogOpen.value = true
}

const handleMoveConfirm = async (targetContainerId: string) => {
  try {
    await moveItem(item.id, targetContainerId)
    toast.success(t('gear.actions.moved') ?? 'Item moved successfully')
    emit('itemUpdated')
  } catch (error) {
    console.error('Failed to move item:', error)
    toast.error(t('common.error'))
  }
}

const isCatalogueActionLoading = computed(() => isFetchingImages.value || isUnlinking.value)

const isLinkedToCatalogue = computed(() => !!item.catalogueItemId)
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button size="sm" variant="ghost">
        <MoreHorizontalIcon class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem
        v-if="!isLinkedToCatalogue"
        :disabled="isCatalogueActionLoading"
        @click="handleMatchWithCatalogue"
      >
        <Sparkles class="size-4" />
        {{ t('gear.catalogue.matchWithCatalogue') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="isLinkedToCatalogue"
        :disabled="isCatalogueActionLoading"
        @click="handleUpdateFromCatalogue"
      >
        <BookIcon class="size-4" />
        {{ t('gear.catalogue.updateFromCatalogue') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="isLinkedToCatalogue"
        :disabled="isCatalogueActionLoading"
        @click="handleFetchImagesFromCatalogue"
      >
        <ImageIcon class="size-4" />
        {{ t('gear.catalogue.fetchImagesFromCatalogue') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="isLinkedToCatalogue"
        :disabled="isCatalogueActionLoading"
        @click="handleUnlinkFromCatalogue"
      >
        <Link2Off class="size-4" />
        {{ t('gear.catalogue.unlinkFromCatalogue') }}
      </DropdownMenuItem>
      <!-- Admin: Add to catalogue (bypass threshold) -->
      <DropdownMenuItem
        v-if="isAdmin && !item.catalogueItemId"
        :disabled="isAddingToCatalogue"
        @click="handleAddToCatalogue"
      >
        <ThumbsUp class="size-4" />
        {{ t('gear.promotion.addToCatalogueAdmin') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem @click="handleMoveItem">
        <MoveIcon class="size-4" />
        {{ t('gear.actions.move') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem
        class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
        @click="emit('delete')"
      >
        <DeleteIcon class="size-4 mr-2" />
        {{ t('gear.actions.delete') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>

  <!-- Update from Catalogue Dialog -->
  <UpdateFromCatalogueDialog
    v-model:open="updateDialogOpen"
    :item
    @item-updated="emit('itemUpdated')"
  />

  <!-- Move Item Dialog -->
  <MoveItemDialog
    v-model:open="moveDialogOpen"
    :item-id="item.id"
    :current-container-id="item.parentItemId ?? ''"
    @move="handleMoveConfirm"
  />
</template>
