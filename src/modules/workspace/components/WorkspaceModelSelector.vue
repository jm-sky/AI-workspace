<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useWorkspaceModels } from '@/modules/workspace/composables/useWorkspaceModels'

const { t } = useI18n()
const { allowedModels, selectedModel, isLoading, isUpdating, selectModel } = useWorkspaceModels()

const selectedModelId = computed({
  get: () => selectedModel.value?.id ?? '',
  set: (value: string) => {
    if (value) void selectModel(value)
  },
})
</script>

<template>
  <Select
    v-model="selectedModelId"
    :disabled="isLoading || isUpdating || allowedModels.length === 0"
  >
    <SelectTrigger size="sm" class="w-full max-w-xs cursor-pointer">
      <SelectValue :placeholder="t('workspace.model.selectPlaceholder')">
        <span v-if="selectedModel" class="flex w-full items-center gap-2">
          <span class="truncate font-medium">{{ selectedModel.name }}</span>
          <span class="ml-auto text-xs uppercase text-muted-foreground">{{ selectedModel.provider }}</span>
        </span>
      </SelectValue>
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="model in allowedModels"
        :key="model.id"
        :value="model.id"
      >
        <div class="flex flex-col gap-0.5">
          <span class="font-medium">{{ model.name }}</span>
          <span class="text-xs text-muted-foreground">{{ model.provider }}</span>
        </div>
      </SelectItem>
    </SelectContent>
  </Select>
</template>
