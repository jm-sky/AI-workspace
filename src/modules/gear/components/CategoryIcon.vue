<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
import type { TContainerColor, TGearItemCategory } from '../types/gear.types'
import { getCategoryIcon } from '../utils/categoryIcons'
import { COLOR_TEXT_CLASSES } from '../utils/containerColors'
import type { HTMLAttributes } from 'vue'

const props = withDefaults(defineProps<{
  category: TGearItemCategory
  color?: TContainerColor | null
  size?: number
  class?: HTMLAttributes['class']
}>(), {
  size: 16,
})

const IconComponent = computed(() => getCategoryIcon(props.category))
</script>

<template>
  <component
    :is="IconComponent"
    :size="size"
    :class="cn(
      COLOR_TEXT_CLASSES[color ?? 'default'],
      props.class,
    )"
  />
</template>

