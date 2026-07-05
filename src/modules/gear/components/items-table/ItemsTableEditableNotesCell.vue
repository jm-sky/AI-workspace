<script setup lang="ts">
import { Check, RefreshCcwIcon, XIcon } from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useInlineItemEditingV2 } from '../../composables/useInlineItemEditingV2'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  update: [item: IGearItemV2]
}>()

// Use shared composable
const { isLoading, save } = useInlineItemEditingV2(props.item)

// In edit mode, always show input
const editedNotes = ref(props.item.notes ?? '')
const isResetting = ref(false)

// Handle blur - save immediately (unless reset is in progress)
async function handleBlur() {
  // Don't save if reset button was clicked
  if (isResetting.value) {
    return
  }

  const trimmedNotes = editedNotes.value.trim()
  const originalNotes = props.item.notes?.trim() ?? ''

  if (trimmedNotes !== originalNotes) {
    const updated = await save({ notes: trimmedNotes ?? null })
    if (updated) {
      emit('update', updated)
    }
  }
}

// Save on Enter
async function handleEnter() {
  const trimmedNotes = editedNotes.value.trim()
  const originalNotes = props.item.notes?.trim() ?? ''

  if (trimmedNotes !== originalNotes) {
    const updated = await save({ notes: trimmedNotes ?? null })
    if (updated) {
      emit('update', updated)
    }
  }
}

// Watch for external changes to item
watch(
  () => props.item.notes,
  (newNotes) => {
    editedNotes.value = newNotes ?? ''
  },
)

// Handle mousedown on reset button - prevent blur from saving
function handleResetMousedown() {
  isResetting.value = true
}

// Reset value and clear flag
function handleReset() {
  editedNotes.value = props.item.notes ?? ''
  // Clear flag after a small delay to ensure blur handler has finished
  setTimeout(() => {
    isResetting.value = false
  }, 0)
}
</script>

<template>
  <div class="flex items-center">
    <div class="relative flex-1 mr-1">
      <Input
        :id="`item-notes-${item.id}`"
        v-model="editedNotes"
        :name="`item-notes-${item.id}`"
        :aria-label="t('gear.item.notes')"
        :disabled="isLoading"
        :placeholder="t('gear.item.notes')"
        class="pr-8 py-1! h-[2.1rem]! border-0"
        @keyup.enter="handleEnter"
        @blur="handleBlur"
      />
      <!-- Reset button -->
      <button
        v-if="editedNotes && editedNotes !== (props.item.notes ?? '') && !isLoading"
        type="button"
        class="absolute right-2 top-0 bottom-0 my-auto p-0"
        @mousedown.prevent="handleResetMousedown"
        @click.stop.prevent="handleReset"
      >
        <XIcon class="size-4" />
      </button>
    </div>
    <Button
      v-tooltip="isLoading ? t('gear.actions.saving') : t('gear.actions.save')"
      size="sm"
      variant="ghost"
      class="px-2!"
      :aria-label="t('gear.actions.save')"
      @click="handleEnter"
    >
      <Check v-if="!isLoading" class="size-4" />
      <RefreshCcwIcon v-if="isLoading" class="size-4 animate-spin" />
    </Button>
  </div>
</template>

