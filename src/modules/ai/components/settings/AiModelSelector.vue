<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAiModels } from '@/modules/ai/composables/useAiModels'

const { isAuthenticated = true } = defineProps<{
  isAuthenticated?: boolean
}>()

const { t } = useI18n()
const { models, selectedModel, selectModel } = useAiModels()

const selectedModelId = computed({
  get: () => selectedModel.value?.id ?? '',
  set: async (value: string) => {
    if (value) {
      await selectModel(value)
      toast.success(t('gear.settings.ai.modelUpdated'))
    }
  },
})
</script>

<template>
  <div class="space-y-3">
    <Label>
      {{ t('gear.settings.ai.defaultModel.label') }}
      <span class="text-destructive">*</span>
    </Label>
    <p class="text-sm text-muted-foreground">
      {{ t('gear.settings.ai.defaultModel.subtitle') }}
    </p>
    <Select v-model="selectedModelId" :disabled="!isAuthenticated">
      <SelectTrigger>
        <SelectValue :placeholder="t('gear.settings.ai.defaultModel.placeholder')">
          <span v-if="selectedModel" class="flex items-center gap-2">
            <span class="font-medium">{{ selectedModel.name }}</span>
            <span class="text-xs text-muted-foreground uppercase">{{ selectedModel.provider }}</span>
          </span>
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
  </div>
</template>
