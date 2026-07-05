<script setup lang="ts">
import { ImageIcon, Link, LoaderCircle, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { type RouteLocationRaw, RouterLink } from 'vue-router'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import Dialog from '@/components/ui/dialog/Dialog.vue'
import DialogContent from '@/components/ui/dialog/DialogContent.vue'
import DropdownMenu from '@/components/ui/dropdown-menu/DropdownMenu.vue'
import DropdownMenuContent from '@/components/ui/dropdown-menu/DropdownMenuContent.vue'
import DropdownMenuItem from '@/components/ui/dropdown-menu/DropdownMenuItem.vue'
import DropdownMenuTrigger from '@/components/ui/dropdown-menu/DropdownMenuTrigger.vue'
import ImageWithLoadingState from '@/components/ui/image/ImageWithLoadingState.vue'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useItemImage } from '@/modules/gear/composables/useItemImage'
import { GearRoutePath } from '@/modules/gear/routes'
import { itemImageApiService } from '@/modules/gear/services/itemImageApiService'
import { useGearStoreV2 } from '@/modules/gear/store/useGearStoreV2'
import { createNavigationQuery } from '@/modules/gear/utils/navigationParams'
import { useHandleError } from '@/shared/composables/useHandleError'
import { config } from '@/shared/config/config'

const props = defineProps<{
  itemId: string
  primaryImageUrl?: string | null
  containerId?: string
  publicMode?: boolean
}>()

const emit = defineEmits<{
  imageUpdated: []
}>()

const { t } = useI18n()
const { handleError } = useHandleError()
const { user, isAuthenticated } = useAuth()
const store = useGearStoreV2()
const { uploadImage: uploadImageWithUpdate, uploadImageFromUrl: uploadImageFromUrlWithUpdate, deleteImage: deleteImageWithUpdate } = useItemImage()

const isUploading = ref(false)
const isDeleting = ref(false)
const fileInput = ref<HTMLInputElement>()
const contextMenuOpen = ref(false)
const urlDialogOpen = ref(false)
const imageUrl = ref('')
const isSubmittingUrl = ref(false)

// Get container to check ownership
const container = computed(() => {
  if (!props.containerId) return undefined
  return store.getItemById(props.containerId)
})

// Check if user is admin
const isAdmin = computed(() => {
  return user.value?.isAdmin ?? false
})

// Check if user is owner of the container
const isOwner = computed(() => {
  if (!isAuthenticated.value || !user.value || !container.value) {
    return false
  }
  // For public containers, check authorId
  if (container.value.authorId) {
    return container.value.authorId === user.value.id
  }
  // For private containers (no authorId), if we can access the container,
  // it means we own it (backend handles authorization)
  // For localStorage, all containers are considered owned by current user
  return true
})

// Check if user can manage images (admin AND owner)
const canManageImages = computed(() => {
  return isAdmin.value && isOwner.value
})

const routeTo = computed<RouteLocationRaw | undefined>(() => {
  if (!props.primaryImageUrl || !props.containerId) return undefined

  if (props.publicMode) {
    return GearRoutePath.PublicItemDetailById(props.containerId, props.itemId)
  }
  return {
    path: GearRoutePath.ItemDetailById(props.containerId, props.itemId),
    query: createNavigationQuery(undefined, 'container'),
  }
})

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // Validate file size (from config: 20 MB for regular users, 50 MB for admins)
  const maxFileSize = isAdmin.value ? config.storage.maxFileSizeAdmin : config.storage.maxFileSize
  if (file.size > maxFileSize) {
    toast.error(t('fileUpload.errors.fileTooLarge', {
      name: file.name,
      size: (maxFileSize / 1024 / 1024).toFixed(1),
    }))
    // Reset input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    return
  }

  // Reset input
  if (fileInput.value) {
    fileInput.value.value = ''
  }

  await uploadImage(file)
}

async function uploadImage(file: File) {
  if (!canManageImages.value || isUploading.value) return

  try {
    isUploading.value = true
    // Use composable that updates both API and Pinia store
    await uploadImageWithUpdate(props.itemId, file, true)
    toast.success(t('gear.itemsTable.imageCell.uploadSuccess'))
    emit('imageUpdated')
  } catch (error: unknown) {
    console.error('Failed to upload image', error)
    handleError(error)
  } finally {
    isUploading.value = false
  }
}

function handleImageClick() {
  if (!canManageImages.value || props.primaryImageUrl) return
  fileInput.value?.click()
}

async function handleDeleteImage() {
  if (!props.primaryImageUrl || !canManageImages.value) return

  if (!confirm(t('gear.itemsTable.imageCell.confirmDelete'))) {
    return
  }

  try {
    isDeleting.value = true
    // Get images to find the primary one
    const images = await itemImageApiService.getImages(props.itemId)
    const primaryImage = images.find(img => img.isPrimary)
    if (primaryImage) {
      // Use composable that updates both API and Pinia store
      await deleteImageWithUpdate(props.itemId, primaryImage.id)
      toast.success(t('gear.itemsTable.imageCell.deleteSuccess'))
      emit('imageUpdated')
    }
  } catch (error: unknown) {
    console.error('Failed to delete image', error)
    handleError(error)
  } finally {
    isDeleting.value = false
  }
}

function handleContextMenu(event: MouseEvent) {
  if (!canManageImages.value) return
  event.preventDefault()
  contextMenuOpen.value = true
}

function openUrlDialog() {
  imageUrl.value = ''
  urlDialogOpen.value = true
  contextMenuOpen.value = false
}

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
    // Check if there's already a primary image
    const images = await itemImageApiService.getImages(props.itemId)
    const hasPrimary = images.some(img => img.isPrimary)
    // Use composable that updates both API and Pinia store
    await uploadImageFromUrlWithUpdate(props.itemId, url, !hasPrimary)
    toast.success(t('gear.fileUpload.imageGallery.messages.uploadSuccess'))
    urlDialogOpen.value = false
    imageUrl.value = ''
    emit('imageUpdated')
  } catch (error: unknown) {
    handleError(error, { fallbackMessage: t('gear.fileUpload.imageGallery.messages.uploadFailed') })
  } finally {
    isSubmittingUrl.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center">
    <!-- Hidden file input -->
    <input
      v-if="canManageImages"
      ref="fileInput"
      type="file"
      accept="image/*"
      class="hidden"
      @change="handleFileSelect"
    />

    <!-- Image thumbnail with context menu -->
    <DropdownMenu v-if="primaryImageUrl && canManageImages" v-model:open="contextMenuOpen">
      <div
        class="-my-1 group block rounded-md overflow-hidden"
        @contextmenu="handleContextMenu"
      >
        <DropdownMenuTrigger as-child>
          <component
            :is="routeTo ? RouterLink : 'button'"
            :to="routeTo"
            class="block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <ImageWithLoadingState
              :src="primaryImageUrl"
              :alt="`Image for item ${itemId}`"
              class="size-12 group-hover:border-primary/50 transition-colors"
              :image-class="[
                'size-full object-cover',
                { 'animate-pulse': isDeleting }
              ]"
            />
          </component>
        </DropdownMenuTrigger>
      </div>
      <DropdownMenuContent>
        <DropdownMenuItem
          variant="destructive"
          @select="handleDeleteImage"
        >
          <Trash2 class="size-4" />
          {{ t('gear.itemsTable.imageCell.deleteImage') }}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>

    <!-- Image thumbnail without context menu (read-only) -->
    <component
      :is="routeTo ? RouterLink : 'button'"
      v-else-if="primaryImageUrl"
      :to="routeTo"
      class="-my-1 group block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md overflow-hidden"
    >
      <ImageWithLoadingState
        :src="primaryImageUrl"
        :alt="`Image for item ${itemId}`"
        class="size-12 group-hover:border-primary/50 transition-colors"
        :image-class="[
          'size-full object-cover',
          { 'animate-pulse': isDeleting }
        ]"
      />
    </component>

    <!-- No image - clickable if can manage -->
    <DropdownMenu v-else-if="canManageImages" v-model:open="contextMenuOpen">
      <DropdownMenuTrigger as-child>
        <button
          type="button"
          class="flex items-center justify-center size-10 text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          @contextmenu="handleContextMenu"
        >
          <LoaderCircle v-if="isUploading || isSubmittingUrl" class="size-4 animate-spin" />
          <ImageIcon v-else class="size-4" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem @select="handleImageClick">
          <ImageIcon class="size-4" />
          {{ t('gear.itemsTable.imageCell.uploadFromFile') }}
        </DropdownMenuItem>
        <DropdownMenuItem @select="openUrlDialog">
          <Link class="size-4" />
          {{ t('gear.itemsTable.imageCell.uploadFromUrl') }}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>

    <!-- No image - not clickable -->
    <span v-else class="flex items-center justify-center size-10 text-muted-foreground">
      <ImageIcon class="size-4" />
    </span>

    <!-- URL upload dialog -->
    <Dialog v-model:open="urlDialogOpen">
      <DialogContent>
        <div class="space-y-4">
          <div>
            <h3 class="text-lg font-semibold">
              {{ t('gear.itemsTable.imageCell.addImageFromUrl') }}
            </h3>
            <p class="text-sm text-muted-foreground">
              {{ t('gear.itemsTable.imageCell.addImageFromUrlDescription') }}
            </p>
          </div>
          <div class="space-y-2">
            <Input
              v-model="imageUrl"
              :placeholder="t('gear.fileUpload.imageGallery.urlPlaceholder')"
              type="url"
              autocomplete="off"
              @keyup.enter="handleAddFromUrl"
            />
          </div>
          <div class="flex justify-end gap-2">
            <Button
              variant="outline"
              :disabled="isSubmittingUrl"
              @click="urlDialogOpen = false"
            >
              {{ t('common.cancel') }}
            </Button>
            <Button
              :disabled="isSubmittingUrl || !imageUrl.trim()"
              @click="handleAddFromUrl"
            >
              {{ t('gear.fileUpload.imageGallery.addFromUrl') }}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>
