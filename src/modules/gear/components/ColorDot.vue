<script setup lang="ts">
import { computed } from 'vue'
import type { TContainerColor } from '../types/gear.types'
import { COLOR_DOT_CLASSES, COLOR_TEXT_CLASSES } from '../utils/containerColors'
import type { Component } from 'vue'

const props = withDefaults(defineProps<{
  color?: TContainerColor | null
  icon?: Component | null
  size?: number
}>(), {
  size: 5,
})

const hasIcon = computed(() => !!props.icon)
const iconSize = computed(() => `${props.size * 4}px`)
</script>

<template>
  <component
    :is="icon"
    v-if="hasIcon"
    :style="{ width: iconSize, height: iconSize }"
    :class="[
      'shrink-0',
      COLOR_TEXT_CLASSES[color ?? 'default']
    ]"
  />
  <div
    v-else
    :class="[
      'size-3 rounded-full shrink-0',
      COLOR_DOT_CLASSES[color ?? 'default']
    ]"
  />
</template>
