<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
import ItemPriorityBadge from '../components/badges/ItemPriorityBadge.vue'
import CategoryIcon from '../components/CategoryIcon.vue'
import ItemStatusBadge from '../components/ItemStatusBadge.vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import ItemPromotionCard from '../components/promotion/ItemPromotionCard.vue'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { useExpiration } from '../composables/useExpiration'
import { useFormattedItemPriceV2 } from '../composables/useFormattedItemPriceV2'
import { useFormattedItemWeightV2 } from '../composables/useFormattedItemWeightV2'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { getCategoryLabel } = useCategoryLabel()
const storeV2 = useGearStoreV2()

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string
const item = ref<IGearItemV2 | null>(null)
const isLoading = ref(true)

const { isExpired, isExpiringSoon } = useExpiration(item)

const loadItem = async () => {
  try {
    // Try to load from V2 store first
    const foundItem = storeV2.getItemById(itemId)

    if (!foundItem) {
      toast.error(t('common.error'))
      router.push(GearRoutePath.PublicContainerDetailById(containerId))
      return
    }

    item.value = foundItem
  } catch (error) {
    console.error('Failed to load public item:', error)
    toast.error(t('common.error'))
    router.push(GearRoutePath.PublicContainers)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadItem()
})

const handleBack = () => {
  router.push(GearRoutePath.PublicContainerDetailById(containerId))
}

const { formattedWeight } = useFormattedItemWeightV2(item)
const { formattedPrice } = useFormattedItemPriceV2(item)

// Check if there are any details to display
const hasDetails = computed<boolean>(() => {
  if (!item.value) return false
  return !!(
    item.value.brand ||
    item.value.color ||
    item.value.expirationDate ||
    item.value.url ||
    item.value.notes
  )
})
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-12 bg-muted rounded animate-pulse" />
      <div class="h-64 bg-muted rounded animate-pulse" />
    </div>

    <div v-else-if="item" class="space-y-6 w-full max-w-full overflow-hidden">
      <!-- Header -->
      <div class="space-y-4">
        <Button variant="ghost" size="sm" @click="handleBack">
          <ArrowLeft class="size-4" />
          {{ t('common.back') }}
        </Button>

        <div>
          <h1 class="text-2xl sm:text-3xl font-bold mb-2 wrap-break-word" :class="{ 'text-destructive': isExpired, 'text-yellow-600': isExpiringSoon }">
            {{ item.name }}
          </h1>
          <div class="flex items-center gap-2 flex-wrap">
            <Badge v-if="item.category" variant="outline" class="flex items-center gap-2">
              <CategoryIcon :category="item.category" :size="14" />
              {{ getCategoryLabel(item.category) }}
            </Badge>
            <ItemPriorityBadge v-if="item.priority" :priority="item.priority" />
            <ItemStatusBadge v-if="item.status" :status="item.status" />
            <Badge v-if="isExpired" variant="destructive" class="text-xs">
              {{ t('gear.item.expiration.expired') }}
            </Badge>
            <Badge v-if="isExpiringSoon" variant="outline" class="text-xs text-yellow-600 border-yellow-600">
              {{ t('gear.item.expiration.expiringSoon') }}
            </Badge>
            <Badge v-if="item.wearable" variant="outline" class="text-xs">
              {{ t('gear.item.wearable') }}
            </Badge>
            <Badge v-if="item.consumable" variant="outline" class="text-xs">
              {{ t('gear.item.consumable') }}
            </Badge>
          </div>
        </div>
      </div>

      <!-- Main Info -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.item.quantity') }}
          </div>
          <div class="text-2xl font-bold">
            {{ item.quantity }}
          </div>
        </div>
        <div class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.container.totalWeight') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedWeight }}
          </div>
        </div>
        <div v-if="item.price != null" class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.item.price') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedPrice }}
          </div>
        </div>
        <div v-if="item.quality" class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.item.quality') }}
          </div>
          <div class="text-2xl font-bold">
            {{ t(`gear.item.qualities.${item.quality}`) }}
          </div>
        </div>
      </div>

      <!-- Details -->
      <div class="bg-card rounded-lg border p-6 space-y-4">
        <h2 class="text-lg font-semibold">
          {{ t('gear.item.details') }}
        </h2>

        <template v-if="hasDetails">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div v-if="item.brand">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.brand') }}
              </div>
              <div class="font-medium">
                {{ item.brand }}
              </div>
            </div>
            <div v-if="item.color">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.color') }}
              </div>
              <div class="flex items-center gap-2">
                <div
                  class="size-4 rounded-full shrink-0 border border-border"
                  :style="{
                    backgroundColor: getColorHex(item.color) ?? DEFAULT_COLOR,
                  }"
                />
                <span class="font-medium">{{ item.color }}</span>
              </div>
            </div>
            <div v-if="item.expirationDate">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.expirationDate') }}
              </div>
              <div class="font-medium" :class="{ 'text-destructive': isExpired, 'text-yellow-600': isExpiringSoon }">
                {{ new Date(item.expirationDate).toLocaleDateString() }}
              </div>
            </div>
            <div v-if="item.url">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.url') }}
              </div>
              <div>
                <a
                  :href="item.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:underline font-medium"
                >
                  {{ t('gear.item.openLink') }}
                </a>
              </div>
            </div>
          </div>

          <div v-if="item.notes" class="pt-4 border-t">
            <div class="text-sm text-muted-foreground mb-2">
              {{ t('gear.item.notes') }}
            </div>
            <MarkdownRenderer
              :content="item.notes"
              class="text-sm"
            />
          </div>
        </template>

        <template v-else>
          <div class="text-center py-8 text-muted-foreground">
            <p class="text-sm">
              {{ t('gear.item.noDetails') }}
            </p>
          </div>
        </template>
      </div>

      <!-- Promotion Card (only for items not already in catalogue) -->
      <ItemPromotionCard
        v-if="!item.catalogueItemId"
        :item-id="itemId"
      />
    </div>
  </AuthenticatedLayout>
</template>

