<script setup lang="ts">
import { CheckCircle2, Plus, Trash2 } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import type { IItemWithContainerId } from '../../types/shopping.types'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import { useExpiration } from '../../composables/useExpiration'
import { useFormattedItemPrice } from '../../composables/useFormattedItemPrice'
import { useFormattedItemWeight } from '../../composables/useFormattedItemWeight'
import { createItemEditPath } from '../../utils/navigationParams'
import ItemPriorityBadge from '../badges/ItemPriorityBadge.vue'
import CategoryIcon from '../CategoryIcon.vue'

const { t } = useI18n()

const { item, isInShoppingList } = defineProps<{
  item: IItemWithContainerId
  isInShoppingList: boolean
  isBeingPurchased?: boolean
}>()

const emit = defineEmits<{
  toggle: []
  purchase: []
}>()

const { getCategoryLabel } = useCategoryLabel()
const { formattedWeight } = useFormattedItemWeight(item, undefined, true)
const { formattedPrice } = useFormattedItemPrice(item, undefined, true)
const { isExpired, isExpiringSoon } = useExpiration(item)
</script>

<template>
  <div
    class="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
    :class="{ 'opacity-90 grayscale blur-[1px]': isBeingPurchased }"
  >
    <!-- Toggle button -->
    <Button
      :variant="isInShoppingList ? 'default' : 'outline'"
      size="sm"
      @click="emit('toggle')"
    >
      <Plus v-if="!isInShoppingList" class="size-4" />
      <Trash2 v-else class="size-4" />
    </Button>

    <!-- Category icon -->
    <CategoryIcon :category="item.category" :size="20" class="text-muted-foreground shrink-0" />

    <!-- Item info -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <RouterLink
          :to="createItemEditPath(item._containerId, item.id, 'shopping')"
          class="font-medium hover:text-primary hover:underline transition-colors"
        >
          {{ item.name }}
        </RouterLink>
        <ItemPriorityBadge :priority="item.priority" class="text-xs" />
        <Badge
          v-if="item.status === 'toBuy'"
          variant="outline"
          class="text-xs"
        >
          {{ t('gear.item.statuses.toBuy') }}
        </Badge>
        <Badge
          v-else-if="isExpiringSoon"
          variant="outline"
          :class="[
            'text-xs',
            isExpired ? 'text-red-600 border-red-600' : 'text-yellow-600 border-yellow-600'
          ]"
        >
          {{ isExpired ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}
        </Badge>
      </div>
      <div class="flex items-center gap-4 mt-1 text-sm text-muted-foreground flex-wrap">
        <span>{{ getCategoryLabel(item.category) }}</span>
        <span v-if="item.brand">{{ item.brand }}</span>
        <span>{{ t('gear.item.quantity') }}: {{ item.quantity }}</span>
        <span>
          {{ formattedWeight }}
        </span>
        <span v-if="item.price">
          {{ formattedPrice }}
        </span>
        <span v-if="item.expirationDate" :class="isExpired ? 'text-red-600' : 'text-yellow-600'">
          {{ isExpired ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}: {{ new Date(item.expirationDate).toLocaleDateString() }}
        </span>
      </div>
    </div>
    <div class="hiden: md:flex flex-row gap-2 items-center justify-end">
      <Button
        variant="default"
        size="sm"
        :loading="isBeingPurchased"
        @click="emit('purchase')"
      >
        <CheckCircle2 class="size-4" />
        <span class="hidden sm:inline">{{ t('gear.shopping.purchased', 'Purchased') }}</span>
      </Button>
    </div>
  </div>
</template>
