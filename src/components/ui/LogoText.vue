<script setup lang="ts">
import { cn } from '@/lib/utils'
import { config } from '@/shared/config/config'
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

const props = withDefaults(defineProps<{
  as?: PrimitiveProps['as']
  class?: HTMLAttributes['class']
}>(), {
  as: 'span',
})
</script>

<template>
  <component :is="props.as" :class="cn('text-base font-bold text-transparent bg-clip-text bg-linear-to-r from-primary via-sky-700 to-primary sm:text-xl md:text-2xl', props.class)">
    {{ config.app.name }}
  </component>
</template>
