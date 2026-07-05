<script setup lang="ts">
import { computed } from 'vue'
import type { TContainerColor, TGearContainerType } from '../types/gear.types'
import { getContainerIcon } from '../utils/containerIcons'
import ColorDot from './ColorDot.vue'

const { type, size = 16 } = defineProps<{
  color?: TContainerColor | null
  type: TGearContainerType
  size?: number
}>()

const ContainerIcon = computed(() => getContainerIcon(type))
</script>

<template>
  <ColorDot
    :color="color"
    :icon="ContainerIcon"
    :size="size"
  />
</template>
