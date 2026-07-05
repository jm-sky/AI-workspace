<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useBackend } from '@/shared/composables/useBackend'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import { config } from '@/shared/config/config'
import type { IGearItemV2 } from '../types/gear.types.v2'
import ItemHeader from '../components/ItemHeader.vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import ItemPromotionCard from '../components/promotion/ItemPromotionCard.vue'
import SearchImagesButton from '../components/SearchImagesButton.vue'
import { useExpiration } from '../composables/useExpiration'
import { useFormattedItemPriceV2 } from '../composables/useFormattedItemPriceV2'
import { useFormattedItemWeightV2 } from '../composables/useFormattedItemWeightV2'
import { useGearV2 } from '../composables/useGearV2'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { getFrom } from '../utils/navigationParams'
import { calculateExpirationDate, formatShelfLife } from '../utils/shelfLife'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const ItemImageGallery = defineAsyncComponent(() => import('../components/ItemImageGallery.vue'))

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const storeV2 = useGearStoreV2()
const { shouldUseAPI } = useBackend()
const { user, isAuthenticated } = useAuth()
const { setTitle } = usePageTitle()
const { deleteItem, updateItem } = useGearV2()

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string
const item = ref<IGearItemV2 | null>(null)
const container = ref<IGearItemV2 | null>(null)
const isLoading = ref(true)
const imageGalleryRef = ref<InstanceType<typeof ItemImageGallery> | null>(null)

// Set dynamic page title
watchEffect(() => {
  if (item.value?.name) {
    setTitle('gear.pages.itemDetail', { name: item.value.name })
  }
})

const { isExpired, isExpiringSoon } = useExpiration(item)

// Check if user is admin
const isAdmin = computed(() => user.value?.isAdmin ?? false)

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

const loadItem = async () => {
  try {
    // Load from V2 store
    const containerData = storeV2.getItemById(containerId)
    container.value = containerData ?? null
    const foundItem = storeV2.getItemById(itemId)

    if (!foundItem) {
      toast.error(t('common.error'))
      router.push(GearRoutePath.ContainerDetailById(containerId))
      return
    }

    item.value = foundItem
  } catch (error) {
    console.error('Failed to load item:', error)
    toast.error(t('common.error'))
    router.push(GearRoutePath.ContainerDetailById(containerId))
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadItem()
})

// Callback to refresh item after catalogue operations
const handleItemUpdated = async () => {
  // After catalogue operations, item is refreshed in store
  try {
    // Try to get item from refreshed store
    const refreshedItem = storeV2.getItemById(itemId)
    const refreshedContainer = storeV2.getItemById(containerId)

    if (refreshedItem) {
      item.value = refreshedItem
      container.value = refreshedContainer ?? null
      // Reload images in gallery
      imageGalleryRef.value?.reload()
      return
    }
    // Fallback to reloading
    await loadItem()
    // Reload images in gallery
    imageGalleryRef.value?.reload()
  } catch (error) {
    console.error('Failed to refresh item:', error)
    // Fallback to reloading
    await loadItem()
    // Reload images in gallery
    imageGalleryRef.value?.reload()
  }
}

// Handle item deletion
const handleDeleteItem = async () => {
  if (!item.value) return

  if (!confirm(t('gear.item.deleteConfirm'))) {
    return
  }

  try {
    await deleteItem(item.value.id)
    toast.success(t('common.success'))

    // Navigate back to the appropriate page
    const from = getFrom(route)
    if (from === 'all-items') {
      router.push(GearRoutePath.AllItems)
    } else {
      router.push(GearRoutePath.ContainerDetailById(containerId))
    }
  } catch (error) {
    console.error('Failed to delete item:', error)
    toast.error(t('common.error'))
  }
}

const { formattedWeight } = useFormattedItemWeightV2(item)
const { formattedPrice } = useFormattedItemPriceV2(item)

// Check if there are any details to display
const hasDetails = computed<boolean>(() => {
  if (!item.value) return false
  return !!(
    item.value.brand
    || item.value.color
    || item.value.expirationDate
    || item.value.shelfLife
    || item.value.url
    || item.value.notes
  )
})

// Extract domain from URL
const getUrlDomain = (url: string): string => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

const urlDomain = computed<string>(() => {
  if (!item.value?.url) return ''
  return getUrlDomain(item.value.url)
})

// Handle set expiration date from shelf life
const handleSetExpirationDate = async () => {
  if (!item.value?.shelfLife) {
    toast.error(t('gear.item.shelfLife'))
    return
  }

  try {
    const expirationDate = calculateExpirationDate(item.value.shelfLife)
    await updateItem(item.value.id, { expirationDate })
    toast.success(t('common.success'))
    await loadItem()
  } catch (error) {
    console.error('Failed to set expiration date:', error)
    toast.error(t('common.error'))
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-12 animate-pulse rounded bg-muted" />
      <div class="h-64 animate-pulse rounded bg-muted" />
    </div>

    <div v-else-if="item" class="w-full max-w-full space-y-6">
      <!-- Header -->
      <ItemHeader
        :container-id
        :item-id
        :item
        @item-updated="handleItemUpdated"
        @delete="handleDeleteItem"
      />

      <!-- Main Info -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.item.quantity') }}
          </div>
          <div class="text-2xl font-bold">
            {{ item.quantity }}
          </div>
        </div>
        <div class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.container.totalWeight') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedWeight }}
          </div>
        </div>
        <div v-if="item.price != null" class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.item.price') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedPrice }}
          </div>
        </div>
        <div v-if="item.quality" class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.item.quality') }}
          </div>
          <div class="text-2xl font-bold">
            {{ t(`gear.item.qualities.${item.quality}`) }}
          </div>
        </div>
      </div>

      <!-- Details -->
      <div class="space-y-4 rounded-lg border bg-card p-6">
        <h2 class="text-lg font-semibold">
          {{ t('gear.item.details') }}
        </h2>

        <template v-if="hasDetails">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div v-if="item.brand">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.brand') }}
              </div>
              <div class="font-medium">
                {{ item.brand }}
              </div>
            </div>
            <div v-if="item.color">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.color') }}
              </div>
              <div class="flex items-center gap-2">
                <div
                  class="size-4 shrink-0 rounded-full border border-border"
                  :style="{
                    backgroundColor: getColorHex(item.color) ?? DEFAULT_COLOR,
                  }"
                />
                <span class="font-medium">{{ item.color }}</span>
              </div>
            </div>
            <div v-if="item.expirationDate">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.expirationDate') }}
              </div>
              <div class="font-medium" :class="{ 'text-destructive': isExpired, 'text-yellow-600': isExpiringSoon }">
                {{ new Date(item.expirationDate).toLocaleDateString() }}
              </div>
            </div>
            <div v-if="item.shelfLife">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.shelfLife') }}
              </div>
              <div class="flex items-center gap-2">
                <div class="font-medium">
                  {{ formatShelfLife(item.shelfLife) }}
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  @click="handleSetExpirationDate"
                >
                  {{ t('gear.actions.setExpirationDate') }}
                </Button>
              </div>
            </div>
            <div v-if="item.url">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.url') }}
              </div>
              <div>
                <a
                  :href="item.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="font-medium text-primary hover:underline"
                >
                  <span class="sm:hidden">{{ t('gear.item.openLink') }}</span>
                  <span class="hidden sm:inline">{{ urlDomain }}</span>
                </a>
              </div>
            </div>
          </div>

          <div v-if="item.notes" class="border-t pt-4">
            <div class="mb-2 text-sm text-muted-foreground">
              {{ t('gear.item.notes') }}
            </div>
            <MarkdownRenderer :content="item.notes" />
          </div>
        </template>

        <template v-else>
          <div class="py-4 text-center text-muted-foreground">
            <p class="text-sm">
              {{ t('gear.item.noDetails') }}
            </p>
          </div>
        </template>
      </div>

      <!-- Image Gallery -->
      <div class="rounded-lg border bg-card p-6">
        <ItemImageGallery
          ref="imageGalleryRef"
          :item-id="itemId"
          :editable="canManageImages"
        >
          <template #header-actions>
            <SearchImagesButton
              v-if="canManageImages && shouldUseAPI && config.features.imageSearch.enabled"
              :item-id="item.id"
              @reload="loadItem"
            />
          </template>
        </ItemImageGallery>
      </div>

      <!-- Promotion Card (only for public containers, only when using API) -->
      <ItemPromotionCard
        v-if="shouldUseAPI && container?.isPublic && !item.catalogueItemId"
        :item-id="itemId"
      />
    </div>
  </AuthenticatedLayout>
</template>
