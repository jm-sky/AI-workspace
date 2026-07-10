<script setup lang="ts">
import { CheckIcon, ChevronsUpDownIcon } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
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
import WorkspaceModelCard from '@/modules/workspace/components/WorkspaceModelCard.vue'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'
import { SORT_KEYS, sortModels } from '@/modules/workspace/utils/aiModelFormat'
import type { HTMLAttributes } from 'vue'
import type { IAiModel } from '@/modules/workspace/types/workspaceConfig'
import type { SortKey } from '@/modules/workspace/utils/aiModelFormat'

/** The whole catalog is too long to scroll; the browse page exists for that. */
const RENDER_LIMIT = 50

const props = defineProps<{
  models: IAiModel[]
  disabled?: boolean
  showBrowseAll?: boolean
  triggerSize?: 'sm' | 'default'
  class?: HTMLAttributes['class']
}>()

const modelId = defineModel<string>({ default: '' })

const { t } = useI18n()

const open = ref(false)
const sortKey = ref<SortKey>('recommended')
const search = ref('')

const selected = computed(() => props.models.find((m) => m.id === modelId.value))

const sortedModels = computed(() => sortModels(props.models, sortKey.value))

// Command matches against each item's rendered text, so an item we slice off is
// one it can never find. While a search is active every model has to be mounted.
const visibleModels = computed(() =>
  search.value ? sortedModels.value : sortedModels.value.slice(0, RENDER_LIMIT),
)

const isTruncated = computed(() => visibleModels.value.length < sortedModels.value.length)

const onSelect = (model: IAiModel) => {
  modelId.value = model.id
  search.value = ''
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
        <CommandInput
          :placeholder="t('workspace.model.searchPlaceholder')"
          @input="search = ($event.target as HTMLInputElement).value"
        />

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
              v-for="model in visibleModels"
              :key="model.id"
              :value="model.id"
              class="mb-1 cursor-pointer items-start gap-3 rounded-lg border border-hairline bg-surface-raised p-3 last:mb-0 data-[highlighted]:border-primary/40"
              @select="onSelect(model)"
            >
              <CheckIcon
                :class="cn('mt-0.5 size-4 shrink-0', modelId === model.id ? 'opacity-100' : 'opacity-0')"
              />
              <WorkspaceModelCard :model="model" />
            </CommandItem>
          </CommandGroup>
        </CommandList>

        <div
          v-if="showBrowseAll"
          class="flex items-center justify-between gap-2 border-t px-3 py-2"
        >
          <span v-if="isTruncated" class="text-xs text-muted-foreground">
            {{ t('workspace.model.showingOf', {
              shown: visibleModels.length,
              total: sortedModels.length,
            }) }}
          </span>
          <span v-else class="text-xs text-muted-foreground">
            {{ t('workspace.model.results', { count: sortedModels.length }) }}
          </span>
          <Button
            as-child
            variant="ghost"
            size="sm"
            class="h-auto shrink-0 px-2 py-1 text-xs"
            @click="open = false"
          >
            <RouterLink :to="WorkspaceRoutePath.SettingsModels">
              {{ t('workspace.model.browseAll') }}
            </RouterLink>
          </Button>
        </div>
      </Command>
    </PopoverContent>
  </Popover>
</template>
