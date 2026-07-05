<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useGearV2 } from '../composables/useGearV2'

const { t } = useI18n()

const props = defineProps<{
  open: boolean
  itemId: string
  currentContainerId: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  move: [targetContainerId: string]
}>()

// Load all containers through the active V2 service (API or localStorage) into the store.
// The store may only hold the current container's subtree depending on the opening page.
const { containers, getItems } = useGearV2()

watch(
  () => props.open,
  (open) => {
    if (open) {
      getItems({ itemType: 'container' }).catch(() => {})
    }
  },
  { immediate: true },
)

// Get available containers for selection (exclude current container)
const availableContainers = computed(() => {
  return containers.value.filter(c => c.id !== props.currentContainerId)
})

const selectedContainerId = ref<string>('')

const handleOpenChange = (open: boolean) => {
  emit('update:open', open)
  if (!open) {
    selectedContainerId.value = ''
  }
}

const handleMove = () => {
  if (selectedContainerId.value) {
    emit('move', selectedContainerId.value)
    handleOpenChange(false)
  }
}

const isOpen = computed({
  get: () => props.open,
  set: (value) => handleOpenChange(value),
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click="handleOpenChange(false)"
    >
      <div class="bg-card mx-4 w-[95vw] max-w-md rounded-lg border shadow-lg" @click.stop>
        <div class="space-y-4 p-6">
          <div>
            <h2 class="text-lg font-semibold">
              {{ t('gear.item.moveItem') }}
            </h2>
            <p class="mt-1 text-sm text-muted-foreground">
              {{ t('gear.item.moveItemDescription') }}
            </p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">
              {{ t('gear.container.selectContainer') }}
            </label>
            <Select v-model="selectedContainerId">
              <SelectTrigger>
                <SelectValue
                  :placeholder="t('gear.container.selectContainerPlaceholder')"
                />
              </SelectTrigger>
              <SelectContent>
                <template v-for="container in availableContainers" :key="container.id">
                  <SelectItem :value="container.id">
                    <div class="flex items-center gap-2">
                      <Package :size="16" class="text-muted-foreground" />
                      <span>{{ container.name }}</span>
                      <span class="text-xs text-muted-foreground">({{ t(`gear.container.types.${container.containerType ?? 'other'}`) }})</span>
                    </div>
                  </SelectItem>
                </template>
              </SelectContent>
            </Select>
          </div>

          <p v-if="availableContainers.length === 0" class="text-sm text-muted-foreground">
            {{ t('gear.item.noOtherContainers') }}
          </p>

          <div class="flex justify-end gap-2 pt-4">
            <Button variant="outline" @click="handleOpenChange(false)">
              {{ t('gear.actions.cancel') }}
            </Button>
            <Button :disabled="!selectedContainerId" @click="handleMove">
              {{ t('gear.actions.move') }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
