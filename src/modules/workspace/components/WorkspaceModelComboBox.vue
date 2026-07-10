<script setup lang="ts">
import {
  BrainIcon,
  CheckIcon,
  ChevronsUpDownIcon,
  EyeIcon,
  SparklesIcon,
  WrenchIcon,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'
import type { AiModelTier, IAiModel } from '@/modules/workspace/types/workspaceConfig'

type SortKey = 'recommended' | 'power' | 'price' | 'context' | 'name'

const props = defineProps<{
  models: IAiModel[]
  disabled?: boolean
  triggerSize?: 'sm' | 'default'
  class?: HTMLAttributes['class']
}>()

const modelId = defineModel<string>({ default: '' })

const { t } = useI18n()

const open = ref(false)
const sortKey = ref<SortKey>('recommended')

const SORT_KEYS: SortKey[] = ['recommended', 'power', 'price', 'context', 'name']

// Strongest first, so tier can drive descending "power" order directly.
const TIER_RANK: Record<AiModelTier, number> = { frontier: 0, balanced: 1, fast: 2 }

const TIER_VARIANT: Record<AiModelTier, 'premium' | 'secondary' | 'outline'> = {
  frontier: 'premium',
  balanced: 'secondary',
  fast: 'outline',
}

const selected = computed(() => props.models.find((m) => m.id === modelId.value))

/** Blended per-1M price: outputs are the minority of tokens, so weight inputs higher. */
const blendedPrice = (model: IAiModel) => model.cost_per_1m_input * 0.75 + model.cost_per_1m_output * 0.25

const sortedModels = computed(() => {
  const models = [...props.models]
  switch (sortKey.value) {
    case 'context':
      return models.sort((a, b) => b.context_length - a.context_length)
    case 'name':
      return models.sort((a, b) => a.name.localeCompare(b.name))
    case 'power':
      return models.sort(
        (a, b) => TIER_RANK[a.tier] - TIER_RANK[b.tier] || blendedPrice(b) - blendedPrice(a),
      )
    case 'price':
      return models.sort((a, b) => blendedPrice(a) - blendedPrice(b))
    default:
      return models.sort(
        (a, b) =>
          Number(b.recommended) - Number(a.recommended) ||
          TIER_RANK[a.tier] - TIER_RANK[b.tier] ||
          blendedPrice(a) - blendedPrice(b),
      )
  }
})

const formatContext = (tokens: number) => {
  if (tokens >= 1_000_000) return `${Math.round(tokens / 100_000) / 10}M`
  return `${Math.round(tokens / 1000)}K`
}

const formatPrice = (usd: number) => (usd < 0.1 ? `$${usd.toFixed(3)}` : `$${usd.toFixed(2)}`)

const onSelect = (model: IAiModel) => {
  modelId.value = model.id
  open.value = false
}
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        role="combobox"
        :size="triggerSize ?? 'default'"
        :aria-expanded="open"
        :disabled="disabled || models.length === 0"
        :class="cn('w-full justify-between font-normal', props.class)"
      >
        <span v-if="selected" class="flex min-w-0 items-center gap-2">
          <span class="truncate font-medium">{{ selected.name }}</span>
          <span class="text-xs uppercase text-muted-foreground">{{ selected.provider }}</span>
        </span>
        <span v-else class="text-muted-foreground">
          {{ t('workspace.model.selectPlaceholder') }}
        </span>
        <ChevronsUpDownIcon class="size-4 shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>

    <PopoverContent
      align="start"
      class="w-[min(28rem,calc(100vw-2rem))] p-0"
    >
      <Command>
        <CommandInput :placeholder="t('workspace.model.searchPlaceholder')" />

        <div class="flex flex-wrap items-center gap-1 border-b px-2 py-1.5">
          <span class="mr-1 text-xs text-muted-foreground">{{ t('workspace.model.sortBy') }}</span>
          <button
            v-for="key in SORT_KEYS"
            :key="key"
            type="button"
            :aria-pressed="sortKey === key"
            :class="cn(
              'cursor-pointer rounded-full px-2 py-0.5 text-xs transition-colors',
              sortKey === key
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
            )"
            @click="sortKey = key"
          >
            {{ t(`workspace.model.sort.${key}`) }}
          </button>
        </div>

        <CommandList class="max-h-[22rem]">
          <CommandEmpty>{{ t('workspace.model.empty') }}</CommandEmpty>
          <CommandGroup class="p-2">
            <CommandItem
              v-for="model in sortedModels"
              :key="model.id"
              :value="model.id"
              class="mb-1 cursor-pointer items-start gap-3 rounded-lg border border-hairline bg-surface-raised p-3 last:mb-0 data-[highlighted]:border-primary/40"
              @select="onSelect(model)"
            >
              <CheckIcon
                :class="cn('mt-0.5 size-4 shrink-0', modelId === model.id ? 'opacity-100' : 'opacity-0')"
              />
              <div class="flex min-w-0 flex-1 flex-col gap-1.5">
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
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>
