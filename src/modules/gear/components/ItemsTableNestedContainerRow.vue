<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { TableCell, TableRow } from '@/components/ui/table'
import type { TContainerColor } from '../types/gear.types'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { formatItemWeight } from '../composables/useFormattedItemWeight'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { COLOR_BORDER_CLASSES } from '../utils/containerColors'
import { getContainerIcon } from '../utils/containerIcons'
import ItemPriorityBadge from './badges/ItemPriorityBadge.vue'
import CategoryIcon from './CategoryIcon.vue'
import ColorDot from './ColorDot.vue'
import ItemStatusBadge from './ItemStatusBadge.vue'

const { t, locale } = useI18n()
const router = useRouter()
const { settings: gearSettings } = useGearSettings()
const preferredWeightUnit = computed(() => gearSettings.value.preferredWeightUnit)

const props = defineProps<{
  nestedItems: IGearItemV2[]
  columnsLength: number
  container?: IGearItemV2
}>()

// Get container color with fallback to 'default'
const containerColor = computed<TContainerColor>(() => {
  return (props.container?.color as TContainerColor) ?? 'default'
})

// Get border color class
const borderColorClass = computed(() => {
  return COLOR_BORDER_CLASSES[containerColor.value]
})

// Check if nested item is a container (in V2, containers can be children of other containers)
function isNestedContainer(item: IGearItemV2): boolean {
  return item.itemType === 'container'
}

// Get nested container for an item (in V2, the item itself is a container)
function getNestedContainerForItem(item: IGearItemV2): IGearItemV2 | undefined {
  if (item.itemType !== 'container') return undefined
  return item
}

// Navigate to nested container
function navigateToNestedContainer(item: IGearItemV2) {
  if (item.itemType === 'container') {
    router.push(GearRoutePath.ContainerDetailById(item.id))
  }
}

// Get icon component for nested container
function getNestedContainerIcon(item: IGearItemV2) {
  if (item.itemType !== 'container') return null
  return getContainerIcon(item.containerType || 'backpack')
}
</script>

<template>
  <TableRow class="bg-muted/30 shadow-inner">
    <TableCell :colspan="columnsLength" class="p-0">
      <div class="flex flex-col border-l-2" :class="borderColorClass">
        <div class="pl-8 pr-4 py-3 text-sm font-medium text-muted-foreground border-b">
          {{ t('gear.item.containerContents') }} ({{ nestedItems.length }})
        </div>

        <div v-if="nestedItems.length === 0" class="pl-8 pr-4 py-3 text-sm text-muted-foreground italic">
          {{ t('gear.item.emptyContainer') }}
        </div>
        <template v-else>
          <div
            v-for="nestedItem in nestedItems"
            :key="nestedItem.id"
            class="pl-8 pr-4 py-3 flex items-center gap-4 text-sm border-b rounded hover:bg-muted/50"
          >
            <div class="flex items-center gap-2 min-w-0 md:min-w-92">
              <template v-if="isNestedContainer(nestedItem)">
                <ColorDot
                  :color="(getNestedContainerForItem(nestedItem)?.color as TContainerColor) ?? 'default'"
                  :icon="getNestedContainerIcon(nestedItem)"
                  :size="3.5"
                />
                <span
                  class="font-semibold cursor-pointer text-foreground/80 hover:text-primary transition-colors"
                  @click="navigateToNestedContainer(nestedItem)"
                >
                  {{ nestedItem.name }}
                </span>
              </template>
              <template v-else>
                <CategoryIcon :category="nestedItem.category || ''" :size="14" class="text-muted-foreground" />
                <span>{{ nestedItem.name }}</span>
              </template>
            </div>
            <div class="text-muted-foreground min-w-0 md:min-w-18">
              {{ nestedItem.quantity ?? 1 }}
            </div>
            <div class="text-muted-foreground text-end px-4 min-w-0 md:min-w-[80px]">
              {{ formatItemWeight(nestedItem as any, true, preferredWeightUnit, undefined, locale) }}
            </div>
            <div class="min-w-0 md:min-w-26">
              <ItemPriorityBadge :priority="nestedItem.priority ?? 'medium'" />
            </div>
            <ItemStatusBadge :status="nestedItem.status ?? 'owned'" class="text-xs" />
          </div>
        </template>
      </div>
    </TableCell>
  </TableRow>
</template>
