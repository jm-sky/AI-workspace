<script setup lang="ts">
import { CheckCircle2, Minus, Plus, X } from 'lucide-vue-next'
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

const { item } = defineProps<{
  item: IItemWithContainerId
  isBeingPurchased?: boolean
}>()

const emit = defineEmits<{
  purchase: []
  increment: []
  decrement: []
  delete: []
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

    <!-- Quantity controls -->
    <div class="flex items-center gap-2 shrink-0">
      <Button
        v-tooltip.bottom="t('gear.shopping.decrementQuantity')"
        variant="outline"
        size="sm"
        :aria-label="t('gear.shopping.decrementQuantity')"
        :disabled="item.quantity <= 1"
        @click="emit('decrement')"
      >
        <Minus class="size-4" />
      </Button>
      <span class="text-sm font-medium min-w-[2ch] text-center">
        {{ item.quantity }}
      </span>
      <Button
        v-tooltip.bottom="t('gear.shopping.incrementQuantity')"
        variant="outline"
        size="sm"
        :aria-label="t('gear.shopping.incrementQuantity')"
        @click="emit('increment')"
      >
        <Plus class="size-4" />
      </Button>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-2 shrink-0">
      <Button
        variant="default"
        size="sm"
        :loading="isBeingPurchased"
        @click="emit('purchase')"
      >
        <CheckCircle2 class="size-4" />
        <span class="hidden sm:inline">{{ t('gear.shopping.purchased', 'Purchased') }}</span>
      </Button>
      <Button
        v-tooltip.bottom="t('gear.shopping.removeFromList')"
        variant="outline"
        size="sm"
        :aria-label="t('gear.shopping.removeFromList')"
        @click="emit('delete')"
      >
        <X class="size-4" />
      </Button>
    </div>
  </div>
</template>
