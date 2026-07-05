<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import type { IItemWithContainerId } from '../../types/shopping.types'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import { formatItemPrice } from '../../composables/useFormattedItemPrice'
import { useGearSettings } from '../../composables/useGearSettings'
import ItemPriorityBadge from '../badges/ItemPriorityBadge.vue'
import CategoryIcon from '../CategoryIcon.vue'

const { t } = useI18n()

const { item } = defineProps<{
  item: IItemWithContainerId
}>()

const emit = defineEmits<{
  restore: []
}>()

const { defaultCurrency } = useGearSettings()
const { getCategoryLabel } = useCategoryLabel()
</script>

<template>
  <div class="flex items-center gap-4 p-4 border rounded-lg bg-muted/30 opacity-75">
    <!-- Category icon -->
    <CategoryIcon :category="item.category" :size="20" class="text-muted-foreground shrink-0" />

    <!-- Item info -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="font-medium">{{ item.name }}</span>
        <ItemPriorityBadge :priority="item.priority" class="text-xs" />
      </div>
      <div class="flex items-center gap-4 mt-1 text-sm text-muted-foreground flex-wrap">
        <span>{{ getCategoryLabel(item.category) }}</span>
        <span v-if="item.brand">{{ item.brand }}</span>
        <span>{{ t('gear.item.quantity') }}: {{ item.quantity }}</span>
        <span v-if="item.price">
          {{ formatItemPrice(item, true, defaultCurrency) }}
        </span>
      </div>
    </div>

    <!-- Restore button -->
    <Button
      variant="outline"
      size="sm"
      @click="emit('restore')"
    >
      {{ t('gear.shopping.restore', 'Restore') }}
    </Button>
  </div>
</template>
