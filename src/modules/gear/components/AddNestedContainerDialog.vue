<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import ComboBox, { type ComboBoxOption } from '@/components/ui/combo-box/ComboBox.vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearV2 } from '../composables/useGearV2'

const { t } = useI18n()

const props = defineProps<{
  open: boolean
  currentContainerId: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  confirm: [containerId: string]
}>()

// Load the full container list through the active V2 service (API when authenticated,
// localStorage otherwise) into the store. The container detail page only loads the current
// container + its children, so we fetch all containers when the dialog opens.
const { containers, getItems } = useGearV2()

watch(
  () => props.open,
  (open) => {
    if (open) {
      getItems({ itemType: 'container' }).catch(() => {
        // Best-effort; fall back to whatever is already in the store
      })
    }
  },
  { immediate: true },
)

/**
 * Collect a container id and all of its descendants (V2 hierarchy via parentItemId).
 */
const collectSubtreeIds = (rootId: string, all: IGearItemV2[]): Set<string> => {
  const ids = new Set<string>([rootId])
  const walk = (parentId: string) => {
    for (const c of all) {
      if (c.parentItemId === parentId && !ids.has(c.id)) {
        ids.add(c.id)
        walk(c.id)
      }
    }
  }
  walk(rootId)
  return ids
}

// Get available containers for selection (exclude current container and its nested containers)
const availableContainers = computed<IGearItemV2[]>(() => {
  const allContainers = containers.value
  if (!props.currentContainerId) {
    return allContainers
  }

  const excludedIds = collectSubtreeIds(props.currentContainerId, allContainers)
  return allContainers.filter(c => !excludedIds.has(c.id))
})

// Combo-box options (search matches the rendered text: name + type label)
const containerOptions = computed<ComboBoxOption<IGearItemV2>[]>(() =>
  availableContainers.value.map(c => ({ value: c.id, label: c.name, data: c })),
)

const selectedContainerId = ref<string>('')

const containerTypeLabel = (option: ComboBoxOption<IGearItemV2>): string => {
  return t(`gear.container.types.${option.data?.containerType ?? 'other'}`)
}

const handleOpenChange = (open: boolean) => {
  emit('update:open', open)
  if (!open) {
    selectedContainerId.value = ''
  }
}

const handleConfirm = () => {
  if (selectedContainerId.value) {
    emit('confirm', selectedContainerId.value)
    handleOpenChange(false)
  }
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleOpenChange">
    <DialogContent class="w-full sm:max-w-md">
      <DialogHeader>
        <DialogTitle>{{ t('gear.container.addNested') }}</DialogTitle>
        <DialogDescription>
          {{ t('gear.container.addNestedDescription') }}
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-2">
        <label class="text-sm font-medium">
          {{ t('gear.container.selectContainer') }}
        </label>
        <ComboBox
          v-model:value="selectedContainerId"
          :options="containerOptions"
          class="w-full"
          :placeholder="t('gear.container.selectContainerPlaceholder')"
          :search-placeholder="t('gear.container.searchContainers', 'Search containers...')"
          :empty-message="t('gear.container.noContainersAvailable')"
          clearable
          popover-content-class="w-[calc(100vw-3rem)] sm:w-[var(--reka-popper-anchor-width)] p-0"
        >
          <template #option-before>
            <Package :size="16" class="text-muted-foreground" />
          </template>
          <template #option-content="{ option }">
            <span class="truncate">{{ option.label }}</span>
            <span class="text-xs text-muted-foreground ml-1 shrink-0">
              ({{ containerTypeLabel(option as ComboBoxOption<IGearItemV2>) }})
            </span>
          </template>
        </ComboBox>

        <p v-if="availableContainers.length === 0" class="text-sm text-muted-foreground">
          {{ t('gear.container.noContainersAvailable') }}
        </p>
      </div>

      <DialogFooter class="flex-col-reverse gap-2 sm:flex-row">
        <Button variant="outline" class="w-full sm:w-auto" @click="handleOpenChange(false)">
          {{ t('gear.actions.cancel') }}
        </Button>
        <Button class="w-full sm:w-auto" :disabled="!selectedContainerId" @click="handleConfirm">
          {{ t('gear.actions.add') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
