<script setup lang="ts">
import { UndoIcon } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Input } from '@/components/ui/input'
import ItemsTableMoveButtons from './ItemsTableMoveButtons.vue'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
  isExpired?: boolean
  isExpiringSoon?: boolean
  isSaving?: boolean
  canMoveUp?: boolean
  canMoveDown?: boolean
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, save?: boolean]
  moveUp: []
  moveDown: []
}>()

// In edit mode, always show input
const editedName = ref(props.item.name)

const textClass = computed<string>(() => {
  if (props.isExpired) return 'text-destructive font-semibold'
  if (props.isExpiringSoon) return 'text-yellow-600'
  return ''
})

// Handle change - emit updates to parent
function handleChange(save: boolean = false) {
  if (editedName.value.trim() === '') {
    // Validation - name is required, reset to original
    editedName.value = props.item.name
    return
  }

  if (editedName.value.trim() !== props.item.name) {
    emit('change', { name: editedName.value.trim() }, save)
  } else {
    // No changes - emit empty to clear dirty state
    emit('change', {}, save)
  }
}

// Handle Enter - same as blur
function handleEnter() {
  handleChange(true)
}

// Watch for external changes to item
watch(
  () => props.item.name,
  (newName) => {
    editedName.value = newName
  },
)

// Reset value
function handleReset() {
  editedName.value = props.item.name
  emit('change', {})
}
</script>

<template>
  <div class="flex items-center gap-1 min-w-48">
    <!-- Move up/down buttons -->
    <ItemsTableMoveButtons
      v-if="canMoveUp !== undefined && canMoveDown !== undefined"
      :can-move-up="canMoveUp"
      :can-move-down="canMoveDown"
      @move-up="emit('moveUp')"
      @move-down="emit('moveDown')"
    />
    <div class="relative flex-1">
      <Input
        :id="`item-name-${item.id}`"
        v-model="editedName"
        v-tooltip="isExpiringSoon ? t('gear.item.expiration.expiringSoon') : ''"
        :name="`item-name-${item.id}`"
        :aria-label="t('gear.item.name')"
        class="pl-2 py-1! h-[2.1rem]!"
        :class="[textClass, isExpiringSoon ? 'border border-yellow-600' : 'border-transparent']"
        :disabled="isSaving"
        @keydown.enter.prevent="handleEnter"
        @blur="handleChange"
      />
      <!-- Reset button -->
      <button
        v-if="editedName && editedName !== props.item.name"
        v-tooltip.bottom="t('gear.actions.undo')"
        type="button"
        :aria-label="t('gear.actions.undo')"
        class="absolute right-2 top-0 bottom-0 my-auto p-0"
        @click.stop.prevent="handleReset"
      >
        <UndoIcon class="size-4" />
      </button>
    </div>
    <!-- Badges for expired/expiring items -->
    <Badge v-if="isExpired" variant="destructive" class="text-xs">
      {{ t('gear.item.expiration.expired') }}
    </Badge>
  </div>
</template>

