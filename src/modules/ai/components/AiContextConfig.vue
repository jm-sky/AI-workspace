<!--
  AI Context Configuration Component
  Allows user to configure which fields to send to AI
-->
<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAiContext } from '../composables/useAiContext'

const { t } = useI18n()

const { isAuthenticated } = usePermissions()
const { selectedFields, availableFields, toggleField } = useAiContext()

const isFieldSelected = (field: string): boolean => {
  return selectedFields.value.includes(field)
}

const handleFieldToggle = (field: string): void => {
  toggleField(field)
}

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div class="absolute top-15.5 w-full border-b shadow-lg p-4 space-y-3 bg-card z-10">
    <div class="space-y-2" :class="{ 'opacity-50 pointer-events-none': !isAuthenticated }">
      <div class="flex flex-row gap-2 items-center justify-between pr-1">
        <Label class="text-sm font-medium">{{ t('ai.context.fields') }}</Label>
        <Button size="xs" variant="ghost" @click="emit('close')">
          <X class="size-4" />
        </Button>
      </div>
      <p class="text-xs text-muted-foreground">
        {{ t('ai.context.description') }}
      </p>
      <div class="grid grid-cols-2 gap-2 mt-3">
        <div
          v-for="field in availableFields"
          :key="field"
          class="flex items-center space-x-2"
        >
          <Checkbox
            :id="`field-${field}`"
            :model-value="isFieldSelected(field)"
            @update:model-value="handleFieldToggle(field)"
          />
          <Label
            :for="`field-${field}`"
            class="text-sm font-normal cursor-pointer"
          >
            {{ t(`gear.item.${field}`) }}
          </Label>
        </div>
      </div>
    </div>
  </div>
</template>

