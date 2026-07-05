<script setup lang="ts">
import { PencilIcon, RefreshCcwIcon, XIcon } from 'lucide-vue-next'
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useExpiration } from '../composables/useExpiration'
import { useGearMutations } from '../composables/useGearMutations'
import ContainerNameInput from './inputs/ContainerNameInput.vue'

const props = defineProps<{
  item: IGearItemV2
}>()

const { updateItem } = useGearMutations()
const { t } = useI18n()
const { isExpired, isExpiringSoon } = useExpiration(props.item)

// Inline editing state
const isEditingName = ref<boolean>(false)
const editingName = ref<string>('')
const nameInputRef = ref<HTMLInputElement | undefined>(undefined)
const isSavingName = ref<boolean>(false)

// Inline editing handlers
const startEditingName = () => {
  isEditingName.value = true
  editingName.value = props.item.name
  nextTick(() => {
    nameInputRef.value?.focus()
    nameInputRef.value?.select()
  })
}

const saveName = async () => {
  if (!editingName.value.trim()) {
    editingName.value = props.item.name
    isEditingName.value = false
    return
  }

  if (editingName.value === props.item.name) {
    isEditingName.value = false
    return
  }

  try {
    isSavingName.value = true
    await updateItem(props.item.id, { name: editingName.value.trim() })
    toast.success(t('common.success'))
    isEditingName.value = false
  } catch (error) {
    console.error('Failed to update item name:', error)
    toast.error(t('common.error'))
    editingName.value = props.item.name
  } finally {
    isSavingName.value = false
  }
}

const cancelEditingName = () => {
  editingName.value = props.item.name
  isEditingName.value = false
}

// Single keydown handler (avoids two `@keydown.*` bindings compiling to a duplicate
// onKeydown prop, which vue-tsc 3.3+ flags as TS1117)
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    event.preventDefault()
    saveName()
  } else if (event.key === 'Escape') {
    cancelEditingName()
  }
}
</script>

<template>
  <div v-if="!isEditingName" class="flex items-center gap-2 group">
    <h1 class="wrap-break-word mb-2 text-2xl font-bold sm:text-3xl cursor-pointer hover:text-primary transition-colors delay-200" :class="{ 'text-destructive': isExpired, 'text-yellow-600': isExpiringSoon }" @click="startEditingName">
      {{ item.name }}
    </h1>
    <Button
      variant="ghost"
      size="sm"
      class="opacity-0 group-hover:opacity-100 transition-opacity size-8 p-0 delay-200"
      :aria-label="t('gear.actions.edit')"
      @click.stop="startEditingName"
    >
      <PencilIcon class="size-4" />
    </Button>
  </div>
  <div v-else class="relative flex items-center gap-2 mb-2">
    <ContainerNameInput
      ref="nameInputRef"
      v-model="editingName"
      :disabled="isSavingName"
      @keydown="handleKeydown"
      @blur="saveName"
    />
    <RefreshCcwIcon v-if="isSavingName" class="absolute right-6 top-0 size-4 animate-spin translate-y-1/2" />
    <XIcon v-else class="cursor-pointer absolute right-6 top-0 size-4 translate-y-1/2" @click="cancelEditingName" />
  </div>
</template>

