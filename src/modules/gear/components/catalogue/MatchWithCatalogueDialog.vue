<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { refDebounced } from '@vueuse/core'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import SearchInput from '@/components/ui/input/SearchInput.vue'
import { Label } from '@/components/ui/label'
import type { IGlobalCatalogueItem } from '../../types/catalogue.types'
import type { IGearItemV2, TGearItemCategory } from '../../types/gear.types.v2'
import { useCatalogue } from '../../composables/catalogue/useCatalogue'
import { catalogueApiService } from '../../services/catalogueApiService'
import CategorySelect from '../inputs/CategorySelect.vue'
import MatchWithCatalogueDialogItem from './MatchWithCatalogueDialogItem.vue'

const { t } = useI18n()

const open = defineModel<boolean>('open', { default: false })

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  itemUpdated: []
}>()

const { linkItemToCatalogue, isLinking } = useCatalogue()

// Search state
const searchQueryRaw = ref('')
const category = ref<TGearItemCategory | null>(null)
const searchQuery = refDebounced(searchQueryRaw, 300)

// Search catalogue items with local query
const searchParams = computed(() => ({
  query: searchQuery.value?.trim() ?? null,
  category: category.value ?? null, // Pre-fill with item category for better matches
  isActive: true,
  skip: 0,
  limit: 20,
}))

const {
  data: searchResults,
  isLoading: isLoadingItems,
} = useQuery({
  queryKey: ['catalogue', 'search', searchParams],
  queryFn: () => catalogueApiService.getCatalogueItems(searchParams.value),
  enabled: computed(() => open.value),
  staleTime: 30 * 1000, // 30 seconds
})

const catalogueItems = computed<IGlobalCatalogueItem[]>(() => searchResults.value ?? [])

// Selected catalogue item
const selectedCatalogueItemId = ref<string | null>(null)

const selectedCatalogueItem = computed<IGlobalCatalogueItem | null>(() => {
  if (!selectedCatalogueItemId.value) return null
  return catalogueItems.value.find(item => item.id === selectedCatalogueItemId.value) ?? null
})

// Reset when dialog opens
watch(
  () => open.value,
  (isOpen) => {
    if (isOpen) {
      searchQueryRaw.value = props.item.name // Pre-fill with item name
      selectedCatalogueItemId.value = null
    } else {
      searchQueryRaw.value = ''
      selectedCatalogueItemId.value = null
    }
  },
)

const handleOpenChange = (isOpen: boolean) => {
  open.value = isOpen
}

const handleConfirm = async () => {
  if (!selectedCatalogueItemId.value) return

  try {
    await linkItemToCatalogue(props.item.id, selectedCatalogueItemId.value)
    toast.success(t('gear.catalogue.matchedWithCatalogue'))
    handleOpenChange(false)
    emit('itemUpdated')
  } catch (error) {
    console.error('Failed to link item to catalogue:', error)
    toast.error(t('common.error'))
  }
}

const canSubmit = computed<boolean>(() => {
  return !!selectedCatalogueItemId.value && !isLinking.value
})

// Filter items to exclude already matched ones (optional)
const filteredCatalogueItems = computed<IGlobalCatalogueItem[]>(() => {
  return catalogueItems.value.filter(item => item.isActive ?? true)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click="handleOpenChange(false)"
    >
      <div class="mx-4 w-[95vw] max-w-2xl rounded-lg border bg-card shadow-lg" @click.stop>
        <div class="space-y-4 p-6">
          <!-- Title -->
          <div>
            <h2 class="text-lg font-semibold">
              {{ t('gear.catalogue.matchWithCatalogue') }}
            </h2>
            <p class="mt-1 text-sm text-muted-foreground">
              {{ item.name }}
            </p>
          </div>

          <!-- Search Input -->
          <div class="space-y-2">
            <Label for="catalogue-search">
              {{ t('gear.catalogue.searchCatalogue') }}
            </Label>
            <div class="flex flex-row items-center gap-2">
              <SearchInput
                id="catalogue-search"
                v-model="searchQueryRaw"
                name="catalogue-search"
                :placeholder="t('gear.catalogue.searchPlaceholder')"
                :disabled="isLinking"
              />
              <CategorySelect
                id="catalogue-category"
                v-model="category"
                :placeholder="t('gear.filters.all')"
                :nullable="true"
              />
            </div>
          </div>

          <!-- Results List -->
          <div class="max-h-[400px] space-y-2 overflow-y-auto rounded-lg border bg-muted/50 p-4">
            <div v-if="isLoadingItems" class="py-8 text-center text-sm text-muted-foreground">
              {{ t('common.loading') }}
            </div>
            <div
              v-else-if="filteredCatalogueItems.length === 0"
              class="py-8 text-center text-sm text-muted-foreground"
            >
              {{ t('gear.catalogue.noMatchesFound') }}
            </div>
            <div v-else class="space-y-2">
              <MatchWithCatalogueDialogItem
                v-for="catalogueItem in filteredCatalogueItems"
                :key="catalogueItem.id"
                :catalogue-item="catalogueItem"
                :selected="selectedCatalogueItemId === catalogueItem.id"
                :is-linking="isLinking"
                @select="selectedCatalogueItemId = catalogueItem.id"
              />
            </div>
          </div>

          <!-- Selected Item Info -->
          <div v-if="selectedCatalogueItem" class="rounded-lg border bg-primary/5 p-3 text-sm">
            <div class="font-medium">
              {{ t('gear.catalogue.selectedCatalogueItem') }}
            </div>
            <div class="mt-1 text-muted-foreground">
              {{ selectedCatalogueItem.name }}
              <span v-if="selectedCatalogueItem.brand">
                - {{ selectedCatalogueItem.brand }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-2 pt-4">
            <Button variant="outline" :disabled="isLinking" @click="handleOpenChange(false)">
              {{ t('gear.actions.cancel') }}
            </Button>
            <Button :disabled="!canSubmit" :loading="isLinking" @click="handleConfirm">
              {{ t('gear.catalogue.match') }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

