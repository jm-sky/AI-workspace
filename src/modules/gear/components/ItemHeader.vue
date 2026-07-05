<script setup lang="ts">
import { ArrowLeftIcon, PencilIcon } from 'lucide-vue-next'
import { computed, defineAsyncComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { IGearItemV2 } from '../types/gear.types.v2'
import CategoryIcon from '../components/CategoryIcon.vue'
import ItemHeaderName from '../components/ItemHeaderName.vue'
import ItemStatusBadge from '../components/ItemStatusBadge.vue'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { useExpiration } from '../composables/useExpiration'
import { GearRoutePath } from '../routes'
import { createNavigationQuery, getFrom } from '../utils/navigationParams'
import ItemPriorityBadge from './badges/ItemPriorityBadge.vue'
import FromCatalogueBadge from './catalogue/FromCatalogueBadge.vue'
import ItemHeaderActions from './ItemHeaderActions.vue'

// Lazy load dialog to reduce initial bundle size
const MatchWithCatalogueDialog = defineAsyncComponent(() => import('./catalogue/MatchWithCatalogueDialog.vue'))

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { getCategoryLabel } = useCategoryLabel()

const { containerId, itemId, item } = defineProps<{
  containerId: string
  itemId: string
  item: IGearItemV2
}>()

const emit = defineEmits<{
  itemUpdated: []
  delete: []
}>()

const { isExpired, isExpiringSoon } = useExpiration(item)

const matchDialogOpen = ref(false)

const backTo = computed<string>(() => {
  const from = getFrom(route)
  if (from === 'all-items') {
    return GearRoutePath.AllItems
  }
  return GearRoutePath.ContainerDetailById(containerId)
})

const handleBack = () => {
  router.push(backTo.value)
}

const handleEdit = () => {
  const from = getFrom(route)
  router.push({
    path: GearRoutePath.ItemEditById(containerId, itemId),
    query: createNavigationQuery('detail', from),
  })
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-4">
      <Button
        variant="ghost"
        size="sm"
        @click="handleBack"
      >
        <ArrowLeftIcon class="size-4" />
        {{ t('common.back') }}
      </Button>

      <div class="flex items-center justify-end gap-2">
        <Button size="sm" @click="handleEdit">
          <PencilIcon class="size-4" />
          {{ t('common.edit') }}
        </Button>

        <ItemHeaderActions
          v-model:match-dialog-open="matchDialogOpen"
          :item="item"
          @item-updated="emit('itemUpdated')"
          @delete="emit('delete')"
        />
      </div>
    </div>

    <!-- Match with Catalogue Dialog -->
    <MatchWithCatalogueDialog
      v-model:open="matchDialogOpen"
      :item
      @item-updated="emit('itemUpdated')"
    />

    <div class="flex flex-col gap-2">
      <ItemHeaderName :item />
      <div class="flex flex-wrap items-center gap-2">
        <Badge v-if="item.category" variant="outline" class="flex items-center gap-2">
          <CategoryIcon :category="item.category" :size="14" />
          {{ getCategoryLabel(item.category) }}
        </Badge>
        <ItemPriorityBadge v-if="item.priority" :priority="item.priority" />
        <ItemStatusBadge v-if="item.status" :status="item.status" />
        <Badge v-if="isExpired" variant="destructive" class="text-xs">
          {{ t('gear.item.expiration.expired') }}
        </Badge>
        <Badge v-if="isExpiringSoon" variant="outline" class="text-xs border-yellow-600 text-yellow-600">
          {{ t('gear.item.expiration.expiringSoon') }}
        </Badge>
        <Badge v-if="item.wearable" variant="outline" class="text-xs">
          {{ t('gear.item.wearable') }}
        </Badge>
        <Badge v-if="item.consumable" variant="outline" class="text-xs">
          {{ t('gear.item.consumable') }}
        </Badge>
        <FromCatalogueBadge
          v-if="item.catalogueItemId"
          :catalogue-item-id="item.catalogueItemId"
        />
      </div>
    </div>
  </div>
</template>
