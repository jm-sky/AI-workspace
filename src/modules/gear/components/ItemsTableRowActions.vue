<script setup lang="ts">
import {
  AlertCircle,
  CheckCircle2,
  Eye,
  Link2Off,
  MoreHorizontal,
  MoveIcon,
  ShoppingCart,
  Trash2,
} from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import type { IGearItemV2, TGearItemPriority, TGearItemStatus } from '../types/gear.types.v2'
import { getActionIcon } from '../utils/actionIcons'

const { t } = useI18n()

const props = defineProps<{
  row: IGearItemV2
}>()

const emit = defineEmits<{
  edit: [item: IGearItemV2]
  delete: [item: IGearItemV2]
  move: [item: IGearItemV2]
  statusChange: [status: TGearItemStatus]
  viewContainer: [item: IGearItemV2]
  recognizeParameters: [item: IGearItemV2]
  uploadPhoto: [item: IGearItemV2]
  starItem: [item: IGearItemV2, priority: TGearItemPriority]
  unlinkFromCatalogue: [item: IGearItemV2]
}>()

const EditIcon = getActionIcon('edit')
const UploadPhotoIcon = getActionIcon('uploadPhoto')
const StarItemIcon = getActionIcon('starItem')
const RecognizeParametersIcon = getActionIcon('recognizeParameters')

// Check if item is a nested container
const isNestedContainer = computed(() => {
  return props.row.itemType === 'container'
})

// Check if item is linked to catalogue
const isLinkedToCatalogue = computed(() => {
  return !!props.row.catalogueItemId
})
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        v-tooltip.bottom="t('gear.actions.moreActions')"
        variant="ghost"
        class="size-8 p-0"
        :aria-label="t('gear.actions.moreActions')"
      >
        <MoreHorizontal class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <!-- For nested containers: show "View Container" first -->
      <template v-if="isNestedContainer">
        <DropdownMenuItem @click="emit('viewContainer', row)">
          <Eye class="size-4 mr-2" />
          {{ t('gear.item.viewContainer') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
          @click="emit('delete', row)"
        >
          <Trash2 class="size-4 mr-2" />
          {{ t('gear.actions.delete') }}
        </DropdownMenuItem>
      </template>
      <!-- For regular items: standard actions -->
      <template v-else>
        <DropdownMenuItem @click="emit('edit', row)">
          <EditIcon class="size-4 mr-2" />
          {{ t('gear.actions.edit') }}
        </DropdownMenuItem>
        <DropdownMenuItem @click="emit('recognizeParameters', row)">
          <RecognizeParametersIcon class="size-4 mr-2" />
          {{ t('gear.actions.recognizeParameters') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem @click="emit('uploadPhoto', row)">
          <UploadPhotoIcon class="size-4 mr-2" />
          {{ t('gear.actions.uploadPhoto') }}
        </DropdownMenuItem>
        <DropdownMenuItem @click="emit('starItem', row, row.priority === 'critical' ? 'medium' : 'critical')">
          <StarItemIcon :class="['size-4 mr-2', { 'fill-yellow-400': row.priority === 'critical' }]" />
          {{ t('gear.actions.starItem') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem @click="emit('move', row)">
          <MoveIcon class="size-4 mr-2" />
          {{ t('gear.actions.move') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          v-if="isLinkedToCatalogue"
          @click="emit('unlinkFromCatalogue', row)"
        >
          <Link2Off class="size-4 mr-2" />
          {{ t('gear.catalogue.unlinkFromCatalogue') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator v-if="isLinkedToCatalogue" />
        <DropdownMenuItem
          v-if="row.status !== 'owned'"
          @click="emit('statusChange', 'owned')"
        >
          <CheckCircle2 class="size-4 mr-2" />
          {{ t('gear.item.statuses.owned') }}
        </DropdownMenuItem>
        <DropdownMenuItem
          v-if="row.status !== 'missing'"
          @click="emit('statusChange', 'missing')"
        >
          <AlertCircle class="size-4 mr-2" />
          {{ t('gear.item.statuses.missing') }}
        </DropdownMenuItem>
        <DropdownMenuItem
          v-if="row.status !== 'toBuy'"
          @click="emit('statusChange', 'toBuy')"
        >
          <ShoppingCart class="size-4 mr-2" />
          {{ t('gear.item.statuses.toBuy') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
          @click="emit('delete', row)"
        >
          <Trash2 class="size-4 mr-2" />
          {{ t('gear.actions.delete') }}
        </DropdownMenuItem>
      </template>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
