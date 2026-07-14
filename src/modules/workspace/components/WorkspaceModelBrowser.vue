<script setup lang="ts">
import { CheckIcon, SearchIcon } from 'lucide-vue-next'
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { cn } from '@/lib/utils'
import WorkspaceModelCard from '@/modules/workspace/components/WorkspaceModelCard.vue'
import {
  CONTEXT_STEPS,
  COST_STEPS,
  createDefaultFilters,
  filterModels,
  formatContext,
  formatPrice,
  providerCounts,
  SORT_KEYS,
  sortModels,
} from '@/modules/workspace/utils/aiModelFormat'
import type { IAiModel } from '@/modules/workspace/types/workspaceConfig'
import type { SortKey } from '@/modules/workspace/utils/aiModelFormat'

const props = defineProps<{
  models: IAiModel[]
  selectedModelId?: string
  disabled?: boolean
}>()

const emit = defineEmits<{ select: [modelId: string] }>()

const { t } = useI18n()

type CapabilityKey = 'requireVision' | 'requireTools' | 'requireReasoning' | 'recommendedOnly'

const CAPABILITIES: CapabilityKey[] = [
  'requireVision',
  'requireTools',
  'requireReasoning',
  'recommendedOnly',
]

const filters = reactive(createDefaultFilters())
const sortKey = ref<SortKey>('recommended')

// Both sliders are index-based: their scales are non-linear (see COST_STEPS).
const costIndex = ref(COST_STEPS.length - 1)
const contextIndex = ref(0)

const providers = computed(() => providerCounts(props.models))

const results = computed(() => sortModels(filterModels(props.models, filters), sortKey.value))

const isFiltered = computed(() => results.value.length < props.models.length)

const costLabel = computed(() => {
  const cost = filters.maxOutputCost
  return cost === null ? t('workspace.model.filters.noLimit') : formatPrice(cost)
})

const contextLabel = computed(() => {
  const context = filters.minContext
  return context === null ? t('workspace.model.filters.noLimit') : formatContext(context)
})

const onCostChange = (value: number[] | undefined) => {
  const index = value?.[0] ?? COST_STEPS.length - 1
  costIndex.value = index
  filters.maxOutputCost = COST_STEPS[index] ?? null
}

const onContextChange = (value: number[] | undefined) => {
  const index = value?.[0] ?? 0
  contextIndex.value = index
  filters.minContext = CONTEXT_STEPS[index] ?? null
}

const toggleProvider = (provider: string) => {
  const index = filters.providers.indexOf(provider)
  if (index === -1) filters.providers.push(provider)
  else filters.providers.splice(index, 1)
}

const resetFilters = () => {
  Object.assign(filters, createDefaultFilters())
  costIndex.value = COST_STEPS.length - 1
  contextIndex.value = 0
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center gap-2">
      <div class="relative min-w-12 flex-1">
        <SearchIcon
          class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
        />
        <Input
          v-model="filters.search"
          :placeholder="t('workspace.model.searchPlaceholder')"
          class="pl-9"
        />
      </div>

      <div class="flex flex-wrap items-center gap-1">
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
    </div>

    <div class="grid gap-6 lg:grid-cols-[16rem_minmax(0,1fr)]">
      <aside class="space-y-6">
        <section class="space-y-3">
          <h3 class="text-xs font-medium uppercase text-muted-foreground">
            {{ t('workspace.model.filters.capabilities') }}
          </h3>
          <div
            v-for="key in CAPABILITIES"
            :key="key"
            class="flex items-center gap-2"
          >
            <Checkbox :id="key" v-model="filters[key]" />
            <Label :for="key" class="cursor-pointer text-sm font-normal">
              {{ t(`workspace.model.filters.${key}`) }}
            </Label>
          </div>
        </section>

        <section class="space-y-3 max-w-64 md:max-w-full">
          <div class="flex items-baseline justify-between">
            <h3 class="text-xs font-medium uppercase text-muted-foreground">
              {{ t('workspace.model.filters.maxOutputCost') }}
            </h3>
            <span class="font-mono text-xs">{{ costLabel }}</span>
          </div>
          <Slider
            :model-value="[costIndex]"
            :min="0"
            :max="COST_STEPS.length - 1"
            :step="1"
            @update:model-value="onCostChange"
          />
        </section>

        <section class="space-y-3 max-w-64 md:max-w-full">
          <div class="flex items-baseline justify-between">
            <h3 class="text-xs font-medium uppercase text-muted-foreground">
              {{ t('workspace.model.filters.minContext') }}
            </h3>
            <span class="font-mono text-xs">{{ contextLabel }}</span>
          </div>
          <Slider
            :model-value="[contextIndex]"
            :min="0"
            :max="CONTEXT_STEPS.length - 1"
            :step="1"
            @update:model-value="onContextChange"
          />
        </section>

        <section class="space-y-3">
          <h3 class="text-xs font-medium uppercase text-muted-foreground">
            {{ t('workspace.model.filters.providers') }}
          </h3>
          <div class="max-h-64 space-y-2 overflow-y-auto pr-1">
            <div
              v-for="entry in providers"
              :key="entry.provider"
              class="flex items-center gap-2"
            >
              <Checkbox
                :id="`provider-${entry.provider}`"
                :model-value="filters.providers.includes(entry.provider)"
                @update:model-value="toggleProvider(entry.provider)"
              />
              <Label
                :for="`provider-${entry.provider}`"
                class="flex min-w-0 flex-1 cursor-pointer items-center justify-between gap-2 text-sm font-normal"
              >
                <span class="truncate">{{ entry.provider }}</span>
                <span class="shrink-0 text-xs text-muted-foreground">{{ entry.count }}</span>
              </Label>
            </div>
          </div>
        </section>

        <Button
          variant="outline"
          size="sm"
          class="w-full"
          @click="resetFilters"
        >
          {{ t('workspace.model.filters.reset') }}
        </Button>
      </aside>

      <section class="space-y-3">
        <p class="text-sm text-muted-foreground">
          <template v-if="isFiltered">
            {{ t('workspace.model.showingOf', { shown: results.length, total: models.length }) }}
          </template>
          <template v-else>
            {{ t('workspace.model.results', { count: results.length }) }}
          </template>
        </p>

        <p v-if="results.length === 0" class="py-12 text-center text-sm text-muted-foreground">
          {{ t('workspace.model.empty') }}
        </p>

        <div class="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
          <button
            v-for="model in results"
            :key="model.id"
            type="button"
            :disabled="disabled"
            :aria-pressed="model.id === selectedModelId"
            :class="cn(
              'flex cursor-pointer items-start gap-3 rounded-lg border border-hairline bg-surface-raised p-3 text-left transition-colors hover:border-primary/40 disabled:cursor-not-allowed disabled:opacity-60',
              model.id === selectedModelId && 'border-primary',
            )"
            @click="emit('select', model.id)"
          >
            <CheckIcon
              :class="cn(
                'mt-0.5 size-4 shrink-0',
                model.id === selectedModelId ? 'opacity-100' : 'opacity-0',
              )"
            />
            <WorkspaceModelCard :model="model" />
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
