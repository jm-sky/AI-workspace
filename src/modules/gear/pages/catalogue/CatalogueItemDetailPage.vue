<script setup lang="ts">
import { ImageIcon, MoreHorizontal } from 'lucide-vue-next'
import { computed, defineAsyncComponent, ref, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import { Badge } from '@/components/ui/badge'
import Button from '@/components/ui/button/Button.vue'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CatalogueShopCard from '@/modules/gear/components/catalogue/CatalogueShopCard.vue'
import MarkdownRenderer from '@/modules/gear/components/MarkdownRenderer.vue'
import { useCatalogue } from '@/modules/gear/composables/catalogue/useCatalogue'
import { useCategoryLabel } from '@/modules/gear/composables/useCategoryLabel'
import { usePriceTierLabel } from '@/modules/gear/composables/usePriceTierLabel'
import { GearRoutePath } from '@/modules/gear/routes'
import { getActionIcon } from '@/modules/gear/utils/actionIcons'
import { getCategoryIcon } from '@/modules/gear/utils/categoryIcons'
import { DEFAULT_COLOR, getColorHex } from '@/modules/gear/utils/suggestedValues'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import { usePermissions } from '@/shared/composables/usePermissions'
import { COLOR_TEXT_CLASSES } from '../../utils/containerColors'

// Lazy load dialog to reduce initial bundle size
const AddCatalogueItemToContainerDialog = defineAsyncComponent(() => import('@/modules/gear/components/catalogue/AddCatalogueItemToContainerDialog.vue'))

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { setTitle } = usePageTitle()
const { getCategoryLabel } = useCategoryLabel()
const { getPriceTierLabel } = usePriceTierLabel()

const catalogueItemId = route.params.id as string
const { deleteCatalogueItem, getCatalogueItem, isDeleting } = useCatalogue()
const { canAccessAdminPanel, user } = usePermissions()

const {
  data: item,
  isLoading,
  error,
} = getCatalogueItem(catalogueItemId)

const showAddDialog = ref(false)
const showActions = computed<boolean>(() => {
  // Backend: creator OR admin/owner can update/delete
  return !!(
    canAccessAdminPanel.value
    || (user.value?.id && item.value?.createdBy && user.value.id === item.value.createdBy)
  )
})

const EditIcon = getActionIcon('edit')
const DeleteIcon = getActionIcon('delete')

// Set dynamic page title
watchEffect(() => {
  if (item.value?.name) {
    setTitle('gear.catalogue.itemDetail', { name: item.value.name })
  }
})

// Handle error
watchEffect(() => {
  if (error.value) {
    toast.error(t('common.error'))
    router.push(GearRoutePath.CatalogueBrowser)
  }
})

// Computed properties
const categoryLabel = computed(() => {
  if (!item.value) return ''
  return getCategoryLabel(item.value.category)
})

const categoryIcon = computed(() => {
  if (!item.value) return undefined
  return getCategoryIcon(item.value.category)
})

const priceTierLabel = computed(() => {
  if (!item.value?.priceTier) return null
  return getPriceTierLabel(item.value.priceTier)
})

const qualityLabel = computed(() => {
  if (!item.value?.quality) return null
  return t(`gear.item.qualities.${item.value.quality}`)
})

// Check if there are any details to display
const hasDetails = computed<boolean>(() => {
  if (!item.value) return false
  return !!(
    item.value.brand
    || item.value.model
    || item.value.color
    || item.value.url
    || item.value.description
    || item.value.weight
  )
})

// Check if there are shops to display
const hasShops = computed<boolean>(() => {
  return !!(item.value?.shops && item.value.shops.length > 0)
})

// Extract domain from URL with ellipsis if there's a path
const getUrlDisplay = (url: string): string => {
  try {
    const urlObj = new URL(url)
    const domain = urlObj.hostname.replace(/^www\./, '')
    const hasPath = urlObj.pathname !== '/' || urlObj.search || urlObj.hash
    return hasPath ? `${domain}/...` : domain
  } catch {
    return url
  }
}

const urlDisplay = computed<string>(() => {
  if (!item.value?.url) return ''
  return getUrlDisplay(item.value.url)
})

// Display creator name or "User" for created by
const createdByDisplay = computed<string>(() => {
  if (!item.value?.createdBy) return ''
  // If creator name is available (public profile), show it
  if (item.value.creatorName) {
    return item.value.creatorName
  }
  // Otherwise show "User" (private profile)
  return t('gear.catalogue.user')
})

const goBack = () => {
  router.push(GearRoutePath.CatalogueBrowser)
}

const handleAddToContainer = () => {
  showAddDialog.value = true
}

const handleEdit = () => {
  router.push(GearRoutePath.CatalogueItemEditById(catalogueItemId))
}

const handleDelete = async () => {
  if (!confirm(t('gear.catalogue.deleteConfirm'))) {
    return
  }

  try {
    await deleteCatalogueItem(catalogueItemId)
    toast.success(t('common.success'))
    router.push(GearRoutePath.CatalogueManage)
  } catch (error) {
    console.error('Failed to delete catalogue item:', error)
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
      <CommonPageHeader
        :icon="categoryIcon"
        :label="item.name"
        :icon-class="COLOR_TEXT_CLASSES[item.color ?? 'default']"
        with-back-button
        @back="goBack"
      >
        <template #top-actions>
          <div class="flex items-center gap-2">
            <Button size="sm" @click="handleAddToContainer">
              {{ t('gear.catalogue.addToContainer') }}
            </Button>

            <DropdownMenu v-if="showActions">
              <DropdownMenuTrigger as-child>
                <Button size="sm" variant="ghost" :aria-label="t('gear.actions.moreActions')">
                  <MoreHorizontal class="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem @click="handleEdit">
                  <EditIcon class="size-4 mr-2" />
                  {{ t('gear.actions.edit') }}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
                  :disabled="isDeleting"
                  @click="handleDelete"
                >
                  <DeleteIcon class="size-4 mr-2" />
                  {{ t('gear.actions.delete') }}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </template>
      </CommonPageHeader>

      <!-- Badges -->
      <div class="flex flex-wrap gap-2">
        <Badge variant="secondary">
          {{ categoryLabel }}
        </Badge>
        <Badge v-if="item.brand" variant="outline">
          {{ t('gear.catalogue.brand') }}: {{ item.brand }}
        </Badge>
        <Badge v-if="priceTierLabel" variant="outline">
          {{ t('gear.catalogue.priceTier') }}: {{ priceTierLabel }}
        </Badge>
        <Badge v-if="qualityLabel" variant="outline">
          {{ t('gear.catalogue.quality') }}: {{ qualityLabel }}
        </Badge>
        <Badge v-if="!item.isActive" variant="destructive">
          {{ t('gear.catalogue.isActive') }}: {{ item.isActive }}
        </Badge>
      </div>

      <!-- Details and Primary Image Side by Side -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <!-- Details -->
        <div class="space-y-4 rounded-lg border bg-card p-6">
          <h2 class="text-lg font-semibold">
            {{ t('gear.item.details') }}
          </h2>

          <template v-if="hasDetails">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div v-if="item.model">
                <div class="mb-1 text-sm text-muted-foreground">
                  {{ t('gear.catalogue.model') }}
                </div>
                <div class="font-medium">
                  {{ item.model }}
                </div>
              </div>
              <div v-if="item.weight">
                <div class="mb-1 text-sm text-muted-foreground">
                  {{ t('gear.item.weight') }}
                </div>
                <div class="font-medium">
                  {{ item.weight }}{{ item.weightUnit }}
                </div>
              </div>
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
                    {{ urlDisplay }}
                  </a>
                </div>
              </div>
              <div v-if="item.createdBy">
                <div class="mb-1 text-sm text-muted-foreground">
                  {{ t('gear.catalogue.createdBy') }}
                </div>
                <div class="font-medium">
                  {{ createdByDisplay }}
                </div>
              </div>
            </div>

            <div v-if="item.description" class="border-t pt-4">
              <div class="mb-2 text-sm text-muted-foreground">
                {{ t('gear.container.description') }}
              </div>
              <MarkdownRenderer :content="item.description" class="text-sm" />
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

        <!-- Primary Image -->
        <div class="flex items-center justify-center overflow-hidden rounded-lg border" :class="item.primaryImageUrl ? 'bg-white' : 'bg-muted'">
          <img
            v-if="item.primaryImageUrl"
            :src="item.primaryImageUrl"
            :alt="item.name"
            class="max-h-96 w-full object-contain"
          />
          <ImageIcon
            v-else
            class="size-20 w-full opacity-50"
          />
        </div>
      </div>

      <!-- Shops -->
      <div v-if="hasShops" class="rounded-lg border bg-card p-6">
        <h2 class="mb-4 text-lg font-semibold">
          {{ t('gear.catalogue.shopsTitle') }}
        </h2>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <CatalogueShopCard
            v-for="(shop, index) in item.shops"
            :key="index"
            :shop="shop"
            :item-name="item.name"
            :item-created-at="item.createdAt"
          />
        </div>
      </div>

      <!-- Metadata -->
      <div class="rounded-lg border bg-card p-6">
        <h2 class="mb-4 text-lg font-semibold">
          {{ t('gear.catalogue.metadata') }}
        </h2>
        <div class="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
          <div>
            <span class="text-muted-foreground">{{ t('gear.catalogue.metadataCreated') }}:</span>
            <span class="ml-2 font-medium">{{ new Date(item.createdAt).toLocaleString() }}</span>
          </div>
          <div>
            <span class="text-muted-foreground">{{ t('gear.catalogue.metadataUpdated') }}:</span>
            <span class="ml-2 font-medium">{{ new Date(item.updatedAt).toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add to Container Dialog -->
    <AddCatalogueItemToContainerDialog
      v-if="item"
      :open="showAddDialog"
      :catalogue-item="item"
      @update:open="showAddDialog = $event"
    />
  </AuthenticatedLayout>
</template>
