<script setup lang="ts">
import { Box, ChevronRight, Link2 } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import { COLOR_TEXT_CLASSES } from '@/modules/gear/utils/containerColors'
import ItemsTableMoveButtons from './ItemsTableMoveButtons.vue'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const {
  item,
  publicMode,
  isExpired,
  isExpiringSoon,
  isNestedContainer,
  isRowExpanded,
  canMoveUp,
  canMoveDown,
  nestedContainer,
} = defineProps<{
  item: IGearItemV2
  publicMode: boolean
  isExpired: boolean
  isExpiringSoon: boolean
  isNestedContainer: boolean
  isRowExpanded: boolean
  canMoveUp: boolean
  canMoveDown: boolean
  nestedContainer?: IGearItemV2
}>()

const emit = defineEmits<{
  moveUp: []
  moveDown: []
  navigate: []
  navigateToNestedContainer: []
  toggleExpand: []
}>()

const textClass = computed<string>(() => {
  if (isExpired) return 'text-destructive font-semibold'
  if (isExpiringSoon) return 'text-yellow-600'
  return ''
})

const isLinkedItem = computed<boolean>(() => {
  return !!item.linkedItemId
})

const containerColor = computed<string>(() => {
  const color = nestedContainer?.color
  if (color && color in COLOR_TEXT_CLASSES) {
    return COLOR_TEXT_CLASSES[color as keyof typeof COLOR_TEXT_CLASSES]
  }
  return COLOR_TEXT_CLASSES.default
})
</script>

<template>
  <div
    class="flex items-center gap-2"
    :class="textClass"
  >
    <!-- Move up/down buttons (only in non-public mode) -->
    <ItemsTableMoveButtons
      v-if="!publicMode"
      :can-move-up
      :can-move-down
      @move-up="emit('moveUp')"
      @move-down="emit('moveDown')"
    />

    <!-- Expand/Collapse button for nested containers -->
    <Button
      v-if="isNestedContainer"
      variant="ghost"
      size="sm"
      class="size-6 p-0 shrink-0"
      :aria-expanded="isRowExpanded"
      :aria-label="isRowExpanded ? t('gear.item.collapseContainer', 'Collapse container') : t('gear.item.expandContainer', 'Expand container')"
      @click.stop="emit('toggleExpand')"
    >
      <ChevronRight
        class="size-4 text-muted-foreground transition-transform"
        :class="{ 'rotate-90': isRowExpanded }"
      />
    </Button>

    <!-- Nested container display -->
    <template v-if="isNestedContainer">
      <Box class="size-4 text-muted-foreground shrink-0" :class="containerColor" />
      <span
        class="font-semibold cursor-pointer text-foreground/80 hover:text-primary transition-colors"
        @click="emit('navigateToNestedContainer')"
      >
        {{ item.name }}
      </span>
    </template>

    <!-- Regular item display -->
    <div
      v-else
      class="flex items-center gap-1.5 cursor-pointer hover:text-primary transition-colors"
      @click="emit('navigate')"
    >
      <span>
        {{ item.name }}
      </span>
      <Link2 v-if="isLinkedItem" class="size-3 text-violet-500" aria-hidden="true" />
    </div>

    <!-- Badges -->
    <Badge v-if="isNestedContainer" variant="outline" class="text-xs">
      {{ t('gear.item.nestedContainer') }}
    </Badge>
    <Badge v-if="isExpired" variant="destructive" class="text-xs">
      {{ t('gear.item.expiration.expired') }}
    </Badge>
    <Badge v-if="isExpiringSoon" variant="outline" class="text-xs text-yellow-600 border-yellow-600">
      {{ t('gear.item.expiration.expiringSoon') }}
    </Badge>
  </div>
</template>
