<script setup lang="ts">
import { Star } from 'lucide-vue-next'

defineProps<{
  favorite: boolean
}>()
</script>

<template>
  <Star
    :class="[
      'size-4',
      favorite ? 'fill-yellow-500 text-yellow-500' : 'text-muted-foreground',
    ]"
  />
</template>
