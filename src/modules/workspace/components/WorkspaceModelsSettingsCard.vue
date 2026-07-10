<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import WorkspaceModelComboBox from '@/modules/workspace/components/WorkspaceModelComboBox.vue'
import { useWorkspaceModels } from '@/modules/workspace/composables/useWorkspaceModels'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'

const { t } = useI18n()
const {
  allowedModels,
  selectedModel,
  isLoading,
  isUpdating,
  selectModel,
  configQuery,
} = useWorkspaceModels()

const selectedModelId = computed({
  get: () => selectedModel.value?.id ?? '',
  set: (value: string) => {
    if (value) void selectModel(value)
  },
})

const allowedModelIds = computed(() => configQuery.data.value?.allowedModels ?? [])
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-1">
      <h2 class="text-xl font-semibold">
        {{ t('workspace.settings.models') }}
      </h2>
      <p class="text-sm text-muted-foreground">
        {{ t('workspace.settings.modelsDescription') }}
      </p>
    </div>

    <Card>
      <CardHeader>
        <CardTitle class="text-base">
          {{ t('workspace.model.defaultModel') }}
        </CardTitle>
        <CardDescription>
          {{ t('workspace.settings.modelsHint') }}
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <WorkspaceModelComboBox
          v-model="selectedModelId"
          :models="allowedModels"
          :disabled="isLoading || isUpdating"
          class="w-full max-w-md cursor-pointer"
        />

        <p v-if="selectedModel?.description" class="text-sm text-muted-foreground">
          {{ selectedModel.description }}
        </p>

        <p v-if="allowedModelIds.length > 0" class="text-xs text-muted-foreground">
          {{ t('workspace.model.allowedModels', { count: allowedModelIds.length }) }}
        </p>
      </CardContent>
    </Card>

    <Button as-child variant="outline">
      <RouterLink :to="WorkspaceRoutePath.Chat">
        {{ t('workspace.settings.backToChat') }}
      </RouterLink>
    </Button>
  </div>
</template>
