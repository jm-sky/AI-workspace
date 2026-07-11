<script setup lang="ts">
import { CheckIcon, ChevronsUpDownIcon, SearchIcon } from 'lucide-vue-next'
import {
  ListboxContent,
  ListboxFilter,
  ListboxItem,
  ListboxRoot,
  ListboxVirtualizer,
} from 'reka-ui'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'
import WorkspaceModelCard from '@/modules/workspace/components/WorkspaceModelCard.vue'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'
import {
  createDefaultFilters,
  filterModels,
  SORT_KEYS,
  sortModels,
} from '@/modules/workspace/utils/aiModelFormat'
import type { ComponentPublicInstance, HTMLAttributes } from 'vue'
import type { IAiModel } from '@/modules/workspace/types/workspaceConfig'
import type { SortKey } from '@/modules/workspace/utils/aiModelFormat'

/**
 * Row pitch fed to the virtualizer. Rows are positioned from this number rather
 * than measured, so the card is locked to it — never let the card grow taller.
 */
const ROW_HEIGHT = 116

/** Kept in px, not rem: the virtualizer reads it as the scroll viewport. */
const LIST_MAX_HEIGHT = 352

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
const listRef = ref<ComponentPublicInstance | null>(null)

/**
 * The listbox tracks the model object, not its id, because the virtualizer
 * compares `options` against the selected value to scroll it into view.
 */
const selected = computed(() => props.models.find((m) => m.id === modelId.value))

const results = computed(() =>
  sortModels(
    filterModels(props.models, { ...createDefaultFilters(), search: search.value }),
    sortKey.value,
  ),
)

const isFiltered = computed(() => results.value.length < props.models.length)

// The virtual window is derived from scrollTop, so a stale offset would drop a
// fresh result set into its middle.
watch([search, sortKey], () => {
  const el = listRef.value?.$el as HTMLElement | undefined
  el?.scrollTo({ top: 0 })
})

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
      <ListboxRoot
        :model-value="selected"
        by="id"
        selection-behavior="replace"
        highlight-on-hover
        class="flex flex-col overflow-hidden rounded-md"
      >
        <div class="relative border-b">
          <SearchIcon
            class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
          />
          <ListboxFilter
            v-model="search"
            auto-focus
            :placeholder="t('workspace.model.searchPlaceholder')"
            class="h-9 w-full bg-transparent pl-9 pr-3 text-sm outline-hidden placeholder:text-muted-foreground"
          />
        </div>

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

        <p
          v-if="results.length === 0"
          class="px-3 py-8 text-center text-sm text-muted-foreground"
        >
          {{ t('workspace.model.empty') }}
        </p>

        <ListboxContent
          v-else
          ref="listRef"
          :style="{ maxHeight: `${LIST_MAX_HEIGHT}px` }"
          class="overflow-y-auto px-2 py-2"
        >
          <ListboxVirtualizer
            v-slot="{ option }"
            :options="results"
            :estimate-size="ROW_HEIGHT"
            :text-content="(model: IAiModel) => model.name.toLowerCase()"
          >
            <ListboxItem
              :value="option"
              class="group w-full pb-2 outline-hidden"
              :style="{ height: `${ROW_HEIGHT}px` }"
              @select="onSelect(option)"
            >
              <div
                class="flex h-full cursor-pointer items-start gap-3 overflow-hidden rounded-lg border border-hairline bg-surface-raised p-3 transition-colors group-data-[highlighted]:border-primary/40 group-data-[state=checked]:border-primary"
              >
                <CheckIcon
                  class="mt-0.5 size-4 shrink-0 opacity-0 group-data-[state=checked]:opacity-100"
                />
                <WorkspaceModelCard :model="option" />
              </div>
            </ListboxItem>
          </ListboxVirtualizer>
        </ListboxContent>

        <div
          v-if="showBrowseAll"
          class="flex items-center justify-between gap-2 border-t px-3 py-2"
        >
          <span v-if="isFiltered" class="text-xs text-muted-foreground">
            {{ t('workspace.model.showingOf', {
              shown: results.length,
              total: models.length,
            }) }}
          </span>
          <span v-else class="text-xs text-muted-foreground">
            {{ t('workspace.model.results', { count: models.length }) }}
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
      </ListboxRoot>
    </PopoverContent>
  </Popover>
</template>
