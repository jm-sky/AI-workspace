<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import WorkspaceModelBrowser from '@/modules/workspace/components/WorkspaceModelBrowser.vue'
import { useWorkspaceModels } from '@/modules/workspace/composables/useWorkspaceModels'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'

const { t } = useI18n()
const {
  allowedModels,
  selectedModel,
  isLoading,
  isUpdating,
  selectModel,
} = useWorkspaceModels()

const selectedModelId = computed(() => selectedModel.value?.id ?? '')

const onSelect = (modelId: string) => {
  if (modelId !== selectedModelId.value) void selectModel(modelId)
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div class="space-y-1">
        <h2 class="text-xl font-semibold">
          {{ t('workspace.settings.models') }}
        </h2>
        <p class="text-sm text-muted-foreground">
          {{ t('workspace.settings.modelsDescription') }}
        </p>
        <p class="text-xs text-muted-foreground">
          {{ t('workspace.settings.modelsHint') }}
        </p>
      </div>

      <Button as-child variant="outline">
        <RouterLink :to="WorkspaceRoutePath.Chat">
          {{ t('workspace.settings.backToChat') }}
        </RouterLink>
      </Button>
    </div>

    <div
      v-if="selectedModel"
      class="rounded-lg border border-hairline bg-surface-raised px-4 py-3"
    >
      <p class="text-xs uppercase text-muted-foreground">
        {{ t('workspace.model.defaultModel') }}
      </p>
      <p class="mt-1 text-sm font-medium">
        {{ selectedModel.name }}
        <span class="ml-2 text-xs uppercase text-muted-foreground">
          {{ selectedModel.provider }}
        </span>
      </p>
    </div>

    <p v-if="isLoading" class="text-sm text-muted-foreground">
      {{ t('common.loading') }}
    </p>

    <WorkspaceModelBrowser
      v-else
      :models="allowedModels"
      :selected-model-id="selectedModelId"
      :disabled="isUpdating"
      @select="onSelect"
    />
  </div>
</template>
