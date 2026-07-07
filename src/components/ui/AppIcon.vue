<script setup lang="ts">
import { Bot } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'

const props = withDefaults(defineProps<{
  class?: HTMLAttributes['class']
}>(), {})
</script>

<template>
  <Bot :class="cn('text-primary', props.class)" />
</template>
