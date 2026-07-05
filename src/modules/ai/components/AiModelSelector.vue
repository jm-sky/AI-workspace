<!--
  AI Model Selector Component
  Dropdown for selecting AI model
-->
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAiModels } from '../composables/useAiModels'

const { t } = useI18n()

const { isAuthenticated } = usePermissions()

const { models, selectedModel, loadModels, selectModel } = useAiModels()

const selectFirstModel = async () => {
  if (models.value.length > 0) {
    await selectModel(models.value[0]!.id)
  }
}

onMounted(async () => {
  if (models.value.length === 0) {
    await loadModels()
  }

  if (!selectedModel?.value && models.value.length > 0) {
    await selectFirstModel()
  }
})

const handleModelChange = async (modelId: string) => {
  await selectModel(modelId)
}

const selectedModelId = computed({
  get: () => selectedModel.value?.id ?? '',
  set: (value: string) => handleModelChange(value),
})
</script>

<template>
  <Select v-model="selectedModelId" :disabled="!isAuthenticated">
    <SelectTrigger v-tooltip.bottom="t('ai.model.selectTooltip')" size="sm" class="w-56 cursor-pointer hover:bg-accent hover:border-accent-foreground/50">
      <SelectValue :placeholder="t('ai.model.selectPlaceholder')" class="w-full flex items-center gap-2">
        <span class="font-medium">{{ selectedModel?.name }}</span>
        <span class="text-xs text-muted-foreground uppercase ml-auto">{{ selectedModel?.provider }}</span>
      </SelectValue>
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="model in models"
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

