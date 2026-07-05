<script setup lang="ts">
import { RefreshCcw, X } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Input } from '@/components/ui/input'
import SearchInput from '@/components/ui/input/SearchInput.vue'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import CategorySelect from '@/modules/gear/components/inputs/CategorySelect.vue'
import { usePriceTierLabel } from '@/modules/gear/composables/usePriceTierLabel'
import { GEAR_ITEM_QUALITIES } from '@/modules/gear/types/gear.types'
import type { TCataloguePriceTier } from '@/modules/gear/types/catalogue.types'
import type { TGearItemCategory, TGearItemQuality } from '@/modules/gear/types/gear.types'

const { t } = useI18n()
const { getPriceTierLabel } = usePriceTierLabel()

defineProps<{
  loading?: boolean
  hasActiveFilters?: boolean
}>()

// Define models using defineModel
const searchQuery = defineModel<string>('searchQuery', { default: '' })
const category = defineModel<TGearItemCategory | null>('category', { default: null })
const brand = defineModel<string>('brand', { default: '' })
const priceTier = defineModel<TCataloguePriceTier | null>('priceTier', { default: null })
const quality = defineModel<TGearItemQuality | null>('quality', { default: null })

const emit = defineEmits<{
  clearFilters: []
  refresh: []
}>()

const priceTiers: TCataloguePriceTier[] = ['low', 'medium', 'high']

// Computed qualities for select
const qualityOptions = computed(() => {
  return GEAR_ITEM_QUALITIES.map((qual: TGearItemQuality) => ({
    value: qual,
    label: t(`gear.item.qualities.${qual}`),
  }))
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Search and Refresh Row -->
    <div class="flex flex-row items-center gap-2">
      <SearchInput
        id="catalogue-search"
        v-model="searchQuery"
        name="catalogue-search"
        :placeholder="$t('gear.catalogue.searchPlaceholder')"
      />
      <Button
        variant="ghost"
        size="sm"
        :loading
        :aria-label="t('gear.filters.refresh')"
        @click="emit('refresh')"
      >
        <RefreshCcw v-if="!loading" class="size-4" />
      </Button>
    </div>

    <!-- Filters Row -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Category Filter -->
      <div class="space-y-1.5">
        <Label for="category-filter" class="text-xs text-muted-foreground">
          {{ t('gear.catalogue.category') }}
        </Label>
        <CategorySelect
          id="category-filter"
          v-model="category"
          :nullable="true"
          :placeholder="t('gear.filters.all')"
        />
      </div>

      <!-- Brand Filter -->
      <div class="space-y-1.5">
        <Label for="brand-filter" class="text-xs text-muted-foreground">
          {{ t('gear.catalogue.brand') }}
        </Label>
        <Input
          id="brand-filter"
          v-model="brand"
          name="brand-filter"
          :placeholder="t('gear.filters.all')"
        />
      </div>

      <!-- Price Tier Filter -->
      <div class="space-y-1.5">
        <Label for="price-tier-filter" class="text-xs text-muted-foreground">
          {{ t('gear.catalogue.priceTier') }}
        </Label>
        <Select v-model="priceTier">
          <SelectTrigger id="price-tier-filter">
            <SelectValue :placeholder="t('gear.filters.all')" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem :value="null">
              {{ t('gear.filters.all') }}
            </SelectItem>
            <SelectItem v-for="tier in priceTiers" :key="tier" :value="tier">
              {{ getPriceTierLabel(tier) }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- Quality Filter -->
      <div class="space-y-1.5">
        <Label for="quality-filter" class="text-xs text-muted-foreground">
          {{ t('gear.catalogue.quality') }}
        </Label>
        <Select v-model="quality">
          <SelectTrigger id="quality-filter">
            <SelectValue :placeholder="t('gear.filters.all')" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem :value="null">
              {{ t('gear.filters.all') }}
            </SelectItem>
            <SelectItem v-for="option in qualityOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>

    <!-- Clear Filters Button -->
    <div v-if="hasActiveFilters" class="flex justify-end">
      <Button variant="outline" size="sm" @click="emit('clearFilters')">
        <X class="size-4" />
        {{ t('gear.catalogue.clearFilters') }}
      </Button>
    </div>
  </div>
</template>
