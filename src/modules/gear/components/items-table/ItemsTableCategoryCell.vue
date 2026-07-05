<script setup lang="ts">
import { computed } from 'vue'
import { useCategoryLabel } from '@/modules/gear/composables/useCategoryLabel'
import CategoryIcon from '../CategoryIcon.vue'
import type { TGearItemCategory } from '@/modules/gear/types/gear.types'

const { category } = defineProps<{
  category: TGearItemCategory
}>()

const { getCategoryLabel } = useCategoryLabel()

const label = computed<string>(() => getCategoryLabel(category))
</script>

<template>
  <div class="flex items-center gap-2">
    <CategoryIcon :category :size="16" class="text-muted-foreground" />
    <span>{{ label }}</span>
  </div>
</template>
