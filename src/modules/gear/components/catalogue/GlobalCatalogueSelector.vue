<script setup lang="ts">
import { CheckIcon, ChevronsUpDownIcon, Package, Sparkles, XIcon } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import CreateOptionButton from '@/components/ui/combo-box/CreateOptionButton.vue'
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
import CategoryIcon from '@/modules/gear/components/CategoryIcon.vue'
import { useCatalogue } from '@/modules/gear/composables/catalogue/useCatalogue'
import { useItemCatalogV2 } from '@/modules/gear/composables/useItemCatalogV2'
import type { IGlobalCatalogueItem } from '@/modules/gear/types/catalogue.types'
import type { IItemWithContainer } from '@/modules/gear/utils/allItemsColumns'
import type { TUUID } from '@/shared/types/base.type'

export interface CatalogueOption {
  value: string
  label: string
  type: 'custom' | 'catalogue' | 'user-item'
  data?: IGlobalCatalogueItem | IItemWithContainer
}

const props = withDefaults(
  defineProps<{
    containerId: TUUID
    placeholder?: string
    searchPlaceholder?: string
    modelValue?: string
    clearable?: boolean
  }>(),
  {
    placeholder: 'Select item or enter custom name...',
    searchPlaceholder: 'Search items...',
    modelValue: '',
    clearable: true,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'select': [option: CatalogueOption]
}>()

const { t } = useI18n()
const { catalogueItems, isLoadingItems } = useCatalogue({ enableItemsQuery: true })

const open = ref(false)
const searchText = ref('')

// Get user items (excluding current container)
const { catalogItems: userItems } = useItemCatalogV2(() => props.containerId)

// Convert catalogue items to options
const catalogueOptions = computed<CatalogueOption[]>(() => {
  return (catalogueItems.value ?? []).map(item => ({
    value: `catalogue:${item.id}`,
    label: item.name,
    type: 'catalogue' as const,
    data: item,
  }))
})

// Convert user items to options
const userItemOptions = computed<CatalogueOption[]>(() => {
  return userItems.value.map(item => ({
    value: `user:${item.id}`,
    label: item.name,
    type: 'user-item' as const,
    data: item,
  }))
})

// All options combined
const allOptions = computed<CatalogueOption[]>(() => {
  return [...catalogueOptions.value, ...userItemOptions.value]
})

// Get display value
const displayValue = computed(() => {
  if (!props.modelValue) return ''

  // Check if it's a reference to catalogue/user item
  const option = allOptions.value.find(opt => opt.value === props.modelValue)
  if (option) return option.label

  // Otherwise it's a custom value
  return props.modelValue
})

// Get selected option type for display
const selectedOption = computed<CatalogueOption | null>(() => {
  if (!props.modelValue) return null

  const option = allOptions.value.find(opt => opt.value === props.modelValue)
  if (option) return option

  // Custom value
  return {
    value: props.modelValue,
    label: props.modelValue,
    type: 'custom',
  }
})

// Handle item selection
function handleSelect(option: CatalogueOption) {
  emit('update:modelValue', option.value)
  emit('select', option)
  open.value = false
}

// Handle creating custom value
function handleCreate(text: string) {
  if (text.trim()) {
    const customOption: CatalogueOption = {
      value: text.trim(),
      label: text.trim(),
      type: 'custom',
    }
    emit('update:modelValue', text.trim())
    emit('select', customOption)
    open.value = false
  }
}

// Handle clear
function handleClear() {
  emit('update:modelValue', '')
  emit('select', { value: '', label: '', type: 'custom' })
}

// Filter options based on search
const filteredCatalogueOptions = computed(() => {
  if (!searchText.value) return catalogueOptions.value
  const search = searchText.value.toLowerCase()
  return catalogueOptions.value.filter(opt =>
    opt.label.toLowerCase().includes(search) ||
    (opt.data as IGlobalCatalogueItem)?.brand?.toLowerCase().includes(search)
  )
})

const filteredUserItemOptions = computed(() => {
  if (!searchText.value) return userItemOptions.value
  const search = searchText.value.toLowerCase()
  return userItemOptions.value.filter(opt => opt.label.toLowerCase().includes(search))
})
</script>

<template>
  <Popover v-model:open="open">
    <div class="relative">
      <PopoverTrigger as-child>
        <Button
          variant="outline"
          role="combobox"
          :aria-expanded="open"
          class="w-full justify-between font-normal"
        >
          <div v-if="displayValue" class="flex items-center gap-2">
            <Sparkles v-if="selectedOption?.type === 'catalogue'" class="size-4 text-primary" />
            <Package v-else-if="selectedOption?.type === 'user-item'" class="size-4 text-muted-foreground" />
            <span>{{ displayValue }}</span>
          </div>
          <span v-else class="text-muted-foreground">
            {{ placeholder }}
          </span>
          <ChevronsUpDownIcon class="size-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <button
        v-if="clearable && modelValue"
        type="button"
        class="absolute right-10 top-1/2 -translate-y-1/2 cursor-pointer opacity-50 hover:opacity-100"
        @click.stop.prevent.capture="handleClear"
      >
        <XIcon class="size-4 shrink-0" />
      </button>
    </div>
    <PopoverContent class="w-[400px] p-0">
      <Command v-model:search-term="searchText">
        <CommandInput :placeholder="searchPlaceholder" />
        <CommandList>
          <CommandEmpty>
            <div class="py-6 text-center text-sm">
              <p class="text-muted-foreground">
                {{ t('gear.item.catalog.noItemsFound') }}
              </p>
              <CreateOptionButton
                class="mt-4"
                :search-text="searchText"
                :create-label="t('gear.comboBox.add')"
                @create="handleCreate"
              />
            </div>
          </CommandEmpty>

          <!-- Global Catalogue Items -->
          <CommandGroup v-if="filteredCatalogueOptions.length > 0" :heading="t('gear.catalogue.title')">
            <CommandItem
              v-for="option in filteredCatalogueOptions"
              :key="option.value"
              :value="option.value"
              @select="handleSelect(option)"
            >
              <div class="flex w-full items-center justify-between gap-2">
                <div class="flex min-w-0 flex-1 items-center gap-2">
                  <CategoryIcon
                    :category="(option.data as IGlobalCatalogueItem).category"
                    :size="16"
                    class="shrink-0"
                  />
                  <span class="truncate">{{ option.label }}</span>
                </div>
                <div class="flex shrink-0 items-center gap-2">
                  <Badge v-if="(option.data as IGlobalCatalogueItem).brand" variant="outline" class="text-xs">
                    {{ (option.data as IGlobalCatalogueItem).brand }}
                  </Badge>
                  <Badge variant="secondary" class="flex items-center gap-1 text-xs">
                    <Sparkles class="size-3" />
                    {{ t('gear.catalogue.navTitle') }}
                  </Badge>
                </div>
              </div>
              <CheckIcon
                :class="cn('ml-2 size-4 shrink-0', modelValue === option.value ? 'opacity-100' : 'opacity-0')"
              />
            </CommandItem>
          </CommandGroup>

          <!-- User Items -->
          <CommandGroup v-if="filteredUserItemOptions.length > 0" :heading="t('gear.item.catalog.tabExisting')">
            <CommandItem
              v-for="option in filteredUserItemOptions"
              :key="option.value"
              :value="option.value"
              @select="handleSelect(option)"
            >
              <div class="flex w-full items-center justify-between gap-2">
                <div class="flex min-w-0 flex-1 items-center gap-2">
                  <CategoryIcon
                    :category="(option.data as IItemWithContainer).category"
                    :size="16"
                    class="shrink-0"
                  />
                  <span class="truncate">{{ option.label }}</span>
                </div>
                <Badge variant="secondary" class="shrink-0 text-xs">
                  {{ (option.data as IItemWithContainer).containerName }}
                </Badge>
              </div>
              <CheckIcon
                :class="cn('ml-2 size-4 shrink-0', modelValue === option.value ? 'opacity-100' : 'opacity-0')"
              />
            </CommandItem>
          </CommandGroup>

          <!-- Create custom option when typing -->
          <CommandGroup v-if="searchText && !isLoadingItems">
            <div class="px-2 py-1.5">
              <CreateOptionButton
                :search-text="searchText"
                :create-label="t('gear.comboBox.add')"
                @create="handleCreate"
              />
            </div>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>
