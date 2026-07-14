<script setup lang="ts">
import { BrainIcon, EyeIcon, SparklesIcon, WrenchIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { formatContext, formatPrice, TIER_VARIANT } from '@/modules/workspace/utils/aiModelFormat'
import type { IAiModel } from '@/modules/workspace/types/workspaceConfig'

defineProps<{ model: IAiModel }>()

const { t } = useI18n()
</script>

<template>
  <div class="flex min-w-0 max-w-64 md:max-w-full flex-1 flex-col gap-1.5">
    <div class="flex items-center gap-2">
      <span class="truncate text-sm font-medium">{{ model.name }}</span>
      <Badge :variant="TIER_VARIANT[model.tier]" class="shrink-0 text-[10px]">
        {{ t(`workspace.model.tier.${model.tier}`) }}
      </Badge>
      <SparklesIcon
        v-if="model.recommended"
        class="size-3.5 shrink-0 text-primary"
        :aria-label="t('workspace.model.recommended')"
      />
      <span class="ml-auto shrink-0 text-[10px] uppercase text-muted-foreground">
        {{ model.provider }}
      </span>
    </div>

    <p v-if="model.description" class="line-clamp-2 text-xs text-muted-foreground">
      {{ model.description }}
    </p>

    <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted-foreground">
      <span class="font-mono">
        {{ t('workspace.model.price', {
          input: formatPrice(model.cost_per_1m_input),
          output: formatPrice(model.cost_per_1m_output),
        }) }}
      </span>
      <span class="font-mono">
        {{ t('workspace.model.context', { size: formatContext(model.context_length) }) }}
      </span>
      <span class="flex items-center gap-2">
        <EyeIcon
          v-if="model.supports_vision"
          class="size-3.5"
          :aria-label="t('workspace.model.feature.vision')"
        />
        <WrenchIcon
          v-if="model.supports_tools"
          class="size-3.5"
          :aria-label="t('workspace.model.feature.tools')"
        />
        <BrainIcon
          v-if="model.supports_reasoning"
          class="size-3.5"
          :aria-label="t('workspace.model.feature.reasoning')"
        />
      </span>
    </div>
  </div>
</template>
