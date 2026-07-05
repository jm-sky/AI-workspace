<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import { useGearSettings } from '../../composables/useGearSettings'
import { DEFAULT_ITEM_CATEGORY } from '../../utils/constants'
import CategoryIcon from '../CategoryIcon.vue'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearItemCategory } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()
const { customCategories } = useGearSettings()
const { getCategoryLabel } = useCategoryLabel()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto]
}>()

// In edit mode, always show select
const editedCategory = ref<TGearItemCategory>(props.item.category ?? DEFAULT_ITEM_CATEGORY)

const defaultCategories = [
  'blades',
  'fire',
  'light',
  'tools',
  'firstAid',
  'water',
  'food',
  'shelter',
  'navigation',
  'communication',
  'clothing',
  'hygiene',
  'other',
] as const

// Handle category change
function handleCategoryChange(newCategory: unknown) {
  if (newCategory === props.item.category) {
    emit('change', {})
    return
  }

  emit('change', { category: newCategory as TGearItemCategory })
}

// Watch for external changes to item
watch(
  () => props.item.category,
  (newCategory) => {
    editedCategory.value = newCategory ?? DEFAULT_ITEM_CATEGORY
  },
)
</script>

<template>
  <Select
    :model-value="editedCategory"
    @update:model-value="handleCategoryChange"
  >
    <SelectTrigger
      :aria-label="t('gear.item.category')"
      class="h-[2.1rem]! min-w-[140px] border-transparent"
    >
      <SelectValue>
        <div class="flex items-center gap-2">
          <CategoryIcon :category="editedCategory" :size="16" />
          <span>{{ getCategoryLabel(editedCategory) }}</span>
        </div>
      </SelectValue>
    </SelectTrigger>
    <SelectContent>
      <!-- Default Categories -->
      <SelectItem
        v-for="category in defaultCategories"
        :key="category"
        :value="category"
      >
        <div class="flex items-center gap-2">
          <CategoryIcon :category="category" :size="16" />
          <span>{{ t(`gear.item.categories.${category}`) }}</span>
        </div>
      </SelectItem>

      <!-- Custom Categories -->
      <template v-if="customCategories.length > 0">
        <div class="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
          {{ t('settings.categories.title') }}
        </div>
        <SelectItem
          v-for="category in customCategories"
          :key="category.id"
          :value="category.value"
        >
          <div class="flex items-center gap-2">
            <CategoryIcon :category="category.value" :size="16" />
            <span>{{ getCategoryLabel(category.value) }}</span>
          </div>
        </SelectItem>
      </template>
    </SelectContent>
  </Select>
</template>

